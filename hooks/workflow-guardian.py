#!/usr/bin/env python3
"""
workflow-guardian.py — Workflow Guardian Hook Script

Claude Code hooks 的統一入口，從 stdin 讀取 JSON，
根據 hook_event_name 分派到對應 handler。

Handles: SessionStart, UserPromptSubmit, PostToolUse,
         PreCompact, Stop, SessionEnd

Requirements: Python 3.8+, zero external dependencies.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─── Constants ───────────────────────────────────────────────────────────────

CLAUDE_DIR = Path.home() / ".claude"
WORKFLOW_DIR = CLAUDE_DIR / "workflow"
MEMORY_DIR = CLAUDE_DIR / "memory"
CONFIG_PATH = WORKFLOW_DIR / "config.json"
MEMORY_INDEX = "MEMORY.md"

# Defaults (overridable via config.json)
DEFAULTS = {
    "enabled": True,
    "stop_gate_max_blocks": 2,
    "min_files_to_block": 2,
    "remind_after_turns": 3,
    "max_reminders": 3,
    "stale_threshold_hours": 24,
    "sync_keywords": ["同步", "sync", "commit", "提交", "結束", "收工"],
    "completion_indicators": ["已同步", "同步完成", "已更新", "已提交", "committed"],
}

# ─── Config ──────────────────────────────────────────────────────────────────


def load_config() -> Dict[str, Any]:
    """Load config with defaults fallback."""
    config = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, OSError):
            pass
    return config


# ─── State File I/O ──────────────────────────────────────────────────────────


def state_path(session_id: str) -> Path:
    return WORKFLOW_DIR / f"state-{session_id}.json"


def read_state(session_id: str) -> Optional[Dict[str, Any]]:
    """Read state file. Returns None if not found or corrupt."""
    path = state_path(session_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_state(session_id: str, state: Dict[str, Any]) -> None:
    """Atomic write: write to temp then rename."""
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = _now_iso()
    path = state_path(session_id)
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        tmp_path.replace(path)
    except OSError:
        # Best effort; if write fails, continue silently
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def new_state(session_id: str, cwd: str, source: str) -> Dict[str, Any]:
    """Create a fresh state object."""
    return {
        "schema_version": "1.0",
        "session": {
            "id": session_id,
            "started_at": _now_iso(),
            "cwd": cwd,
            "source": source,
        },
        "phase": "init",
        "modified_files": [],
        "knowledge_queue": [],
        "sync_pending": False,
        "stop_blocked_count": 0,
        "remind_count": 0,
        "last_updated": _now_iso(),
    }


# ─── Memory Index Parsing ────────────────────────────────────────────────────

TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")


def parse_memory_index(memory_dir: Path) -> List[str]:
    """Parse MEMORY.md atom index, return list of atom names."""
    index_path = memory_dir / MEMORY_INDEX
    if not index_path.exists():
        return []
    try:
        text = index_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return []

    atoms = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_table:
            if stripped.startswith("| Atom") or stripped.startswith("|Atom"):
                in_table = True
                continue
        else:
            if stripped.startswith("|---") or stripped.startswith("| ---"):
                continue
            if not stripped.startswith("|"):
                break
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if cells:
                atoms.append(cells[0])
    return atoms


# ─── Output Helpers ──────────────────────────────────────────────────────────


def output_json(data: Dict[str, Any]) -> None:
    """Print JSON to stdout and exit 0."""
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)


def output_nothing() -> None:
    """Exit 0 with no output (fast path)."""
    sys.exit(0)


def output_block(reason: str) -> None:
    """Output a block decision (for Stop hook)."""
    output_json({"decision": "block", "reason": reason})


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ─── Event Handlers ──────────────────────────────────────────────────────────


def handle_session_start(input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    session_id = input_data.get("session_id", "unknown")
    cwd = input_data.get("cwd", "")
    source = input_data.get("source", "startup")

    # On compact/resume, reuse existing state
    existing = read_state(session_id)
    if existing and source in ("compact", "resume"):
        state = existing
        # Re-inject full context after compaction
        mod_count = len(state.get("modified_files", []))
        kq_count = len(state.get("knowledge_queue", []))
        phase = state.get("phase", "working")
        lines = [
            f"[Workflow Guardian] Session resumed ({source}). Phase: {phase}.",
            f"Modified files: {mod_count}. Knowledge queue: {kq_count}.",
        ]
        if mod_count > 0:
            files = [m["path"].rsplit("/", 1)[-1] for m in state["modified_files"][-5:]]
            lines.append(f"Recent: {', '.join(files)}")
        if kq_count > 0:
            items = [q["content"][:40] for q in state["knowledge_queue"][:3]]
            lines.append(f"Pending knowledge: {'; '.join(items)}")
        lines.append("Remember: check CLAUDE.md sync rules before ending.")
    else:
        state = new_state(session_id, cwd, source)

        # Parse memory indices
        global_atoms = parse_memory_index(MEMORY_DIR)

        # Try to find project memory
        project_atoms = []
        projects_dir = CLAUDE_DIR / "projects"
        if projects_dir.exists():
            # Find matching project dir by cwd
            cwd_normalized = cwd.replace("\\", "/").replace(":", "").replace("/", "-")
            for proj_dir in projects_dir.iterdir():
                if proj_dir.is_dir():
                    mem_dir = proj_dir / "memory"
                    if mem_dir.is_dir():
                        # Check if project slug matches cwd
                        if any(
                            part in proj_dir.name
                            for part in cwd_normalized.split("-")
                            if len(part) > 2
                        ):
                            project_atoms = parse_memory_index(mem_dir)
                            break

        state["memory_loaded"] = {
            "global_atoms": global_atoms,
            "project_atoms": project_atoms,
        }
        state["phase"] = "working"

        lines = [
            "[Workflow Guardian] Active.",
            f"Global atoms: {', '.join(global_atoms) if global_atoms else 'none'}.",
        ]
        if project_atoms:
            lines.append(f"Project atoms: {', '.join(project_atoms)}.")
        lines.append("I will track file modifications and remind you to sync before ending.")

    write_state(session_id, state)

    output_json({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    })


def handle_user_prompt_submit(
    input_data: Dict[str, Any], config: Dict[str, Any]
) -> None:
    session_id = input_data.get("session_id", "")
    state = read_state(session_id)
    if not state:
        output_nothing()
        return

    # Fast path: nothing pending
    mod_count = len(state.get("modified_files", []))
    kq_count = len(state.get("knowledge_queue", []))
    if mod_count == 0 and kq_count == 0:
        output_nothing()
        return

    prompt = input_data.get("prompt", "")
    remind_after = config.get("remind_after_turns", 3)
    sync_kw = config.get("sync_keywords", [])
    remind_count = state.get("remind_count", 0)

    # Check if user is asking for sync
    prompt_has_sync = any(kw in prompt for kw in sync_kw)

    lines = []
    if prompt_has_sync:
        # Full status dump
        lines.append(f"[Guardian] Sync context: {mod_count} files modified, {kq_count} knowledge items pending.")
        if mod_count > 0:
            files = list({m["path"] for m in state["modified_files"]})
            lines.append(f"Files: {', '.join(f.rsplit('/', 1)[-1] for f in files[:10])}")
        if kq_count > 0:
            for q in state["knowledge_queue"]:
                lines.append(f"  - {q.get('classification', '[臨]')} {q['content'][:60]}")
    elif remind_count < remind_after:
        # Increment remind count but don't inject yet
        state["remind_count"] = remind_count + 1
        write_state(session_id, state)
        output_nothing()
        return
    else:
        # Check max_reminders cap to avoid infinite nagging
        max_reminders = config.get("max_reminders", 3)
        total_reminds = state.get("total_reminds", 0)
        if total_reminds >= max_reminders:
            # Already reminded enough times this session; go silent
            write_state(session_id, state)
            output_nothing()
            return
        # Time to remind
        lines.append(
            f"[Guardian] Reminder: {mod_count} files modified, {kq_count} knowledge items pending. "
            "Consider syncing when current task completes."
        )
        state["remind_count"] = 0  # reset cycle counter
        state["total_reminds"] = total_reminds + 1  # increment lifetime counter

    write_state(session_id, state)

    if lines:
        output_json({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(lines),
            }
        })
    else:
        output_nothing()


def handle_post_tool_use(input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    session_id = input_data.get("session_id", "")
    state = read_state(session_id)
    if not state:
        output_nothing()
        return

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if file_path:
        state.setdefault("modified_files", []).append({
            "path": file_path,
            "tool": tool_name,
            "at": _now_iso(),
        })
        state["sync_pending"] = True
        write_state(session_id, state)

    output_nothing()


def handle_pre_compact(input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    session_id = input_data.get("session_id", "")
    state = read_state(session_id)
    if not state:
        output_nothing()
        return

    # Mark snapshot for recovery after compaction
    state["pre_compact_snapshot"] = _now_iso()
    write_state(session_id, state)
    output_nothing()


def handle_stop(input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    session_id = input_data.get("session_id", "")
    state = read_state(session_id)
    if not state:
        output_nothing()
        return

    max_blocks = config.get("stop_gate_max_blocks", 2)
    stop_count = state.get("stop_blocked_count", 0)
    phase = state.get("phase", "working")

    # Anti-loop guard
    if stop_count >= max_blocks:
        state["phase"] = "done"
        write_state(session_id, state)
        output_nothing()
        return

    # Already synced or marked done
    if phase in ("done", "syncing"):
        output_nothing()
        return

    # Check if sync is needed
    mod_count = len(state.get("modified_files", []))
    kq_count = len(state.get("knowledge_queue", []))
    unique_files = list({m["path"] for m in state.get("modified_files", [])})
    min_files = config.get("min_files_to_block", 2)

    # Muted session — always allow
    if state.get("muted"):
        output_nothing()
        return

    # Nothing to sync
    if mod_count == 0 and kq_count == 0:
        state["phase"] = "done"
        write_state(session_id, state)
        output_nothing()
        return

    # Below threshold: soft reminder only (no block)
    if len(unique_files) < min_files and kq_count == 0:
        state["phase"] = "done"
        write_state(session_id, state)
        output_nothing()
        return

    # Block: meaningful sync needed
    state["stop_blocked_count"] = stop_count + 1
    write_state(session_id, state)

    file_names = ", ".join(f.rsplit("/", 1)[-1] for f in unique_files[:8])

    reason = (
        f"[Workflow Guardian] This session modified {len(unique_files)} file(s)"
        + (f" and has {kq_count} pending knowledge item(s)" if kq_count > 0 else "")
        + f". Files: {file_names}.\n"
        "Please check CLAUDE.md sync rules and ask the user which sync steps apply."
    )

    output_block(reason)


def handle_session_end(input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    session_id = input_data.get("session_id", "")
    state = read_state(session_id)
    if not state:
        sys.exit(0)
        return

    state["ended_at"] = _now_iso()
    state["phase"] = "done"

    mod_count = len(state.get("modified_files", []))
    kq_count = len(state.get("knowledge_queue", []))
    if state.get("sync_pending") and (mod_count > 0 or kq_count > 0):
        print(
            f"Warning: Session ending with unsaved work. "
            f"{mod_count} modified files, {kq_count} knowledge items.",
            file=sys.stderr,
        )

    write_state(session_id, state)
    sys.exit(0)


# ─── Dispatcher ──────────────────────────────────────────────────────────────

HANDLERS = {
    "SessionStart": handle_session_start,
    "UserPromptSubmit": handle_user_prompt_submit,
    "PostToolUse": handle_post_tool_use,
    "PreCompact": handle_pre_compact,
    "Stop": handle_stop,
    "SessionEnd": handle_session_end,
}


def main():
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

    # Read JSON from stdin
    try:
        raw = sys.stdin.buffer.read()
        input_data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Can't parse input; exit silently (non-blocking)
        sys.exit(0)

    config = load_config()
    if not config.get("enabled", True):
        sys.exit(0)

    event = input_data.get("hook_event_name", "")
    handler = HANDLERS.get(event)
    if handler:
        try:
            handler(input_data, config)
        except Exception as e:
            # Never crash; log to stderr (verbose mode only) and continue
            print(f"[workflow-guardian] Error in {event}: {e}", file=sys.stderr)
            sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
