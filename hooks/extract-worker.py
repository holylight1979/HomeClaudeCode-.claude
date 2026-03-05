#!/usr/bin/env python3
"""Detached extraction worker for V2.4 response capture.

Spawned by workflow-guardian.py as an independent subprocess.
Survives hook timeout (3s) — runs ~30s on GTX 1050 Ti.

Usage: python extract-worker.py <session_id> <cwd> <config_json>
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

CLAUDE_DIR = Path.home() / ".claude"
WORKFLOW_DIR = CLAUDE_DIR / "workflow"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def cwd_to_project_slug(cwd: str) -> str:
    slug = cwd.replace(":", "-").replace("\\", "-").replace("/", "-").replace(".", "-")
    if slug:
        slug = slug[0].lower() + slug[1:]
    return slug


def read_state(session_id: str) -> Optional[Dict[str, Any]]:
    path = WORKFLOW_DIR / f"state-{session_id}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_state(session_id: str, state: Dict[str, Any]) -> None:
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = _now_iso()
    path = WORKFLOW_DIR / f"state-{session_id}.json"
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        tmp_path.replace(path)
    except OSError:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def _find_transcript(session_id: str, cwd: str) -> Optional[Path]:
    slug = cwd_to_project_slug(cwd)
    candidate = CLAUDE_DIR / "projects" / slug / f"{session_id}.jsonl"
    return candidate if candidate.exists() else None


def _extract_last_assistant_text(transcript_path: Path, max_chars: int = 3000) -> str:
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines_raw = f.readlines()
    except (OSError, UnicodeDecodeError):
        return ""

    for raw_line in reversed(lines_raw):
        try:
            obj = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "assistant":
            continue
        content = obj.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        texts = []
        total = 0
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text", "")
                if t:
                    texts.append(t)
                    total += len(t)
                    if total >= max_chars:
                        break
        if texts:
            return "\n".join(texts)[:max_chars]
    return ""


_EXTRACT_PROMPT = (
    "Extract reusable technical knowledge from this AI assistant response. "
    "Output a JSON array of objects, each with 'content' (max 80 chars, concise fact) "
    "and 'type' (one of: factual, procedural, architectural, pitfall). "
    "Only extract: root causes, API behaviors, architecture constraints, "
    "debugging patterns, configuration values, environment-specific behaviors. "
    "Skip: code changes, general programming knowledge, session-specific details, greetings. "
    "If nothing worth extracting, output empty array [].\n\n"
    "Response text:\n{text}\n\nJSON:"
)


def _call_ollama(prompt: str, model: str = "qwen3:1.7b", timeout: int = 120) -> str:
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 2048}
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")
    except Exception:
        return ""


def extract(session_id: str, cwd: str, config: dict) -> None:
    transcript = _find_transcript(session_id, cwd)
    if not transcript:
        return

    rc = config.get("response_capture", {})
    max_chars = rc.get("per_turn_max_chars", 3000)
    min_chars = rc.get("per_turn_min_response_chars", 100)
    max_items = rc.get("per_turn_max_items", 2)

    text = _extract_last_assistant_text(transcript, max_chars=max_chars)
    if not text or len(text) < min_chars:
        return

    state = read_state(session_id)
    if not state:
        return
    existing = state.get("knowledge_queue", [])

    prompt = _EXTRACT_PROMPT.format(text=text[:max_chars])
    raw = _call_ollama(prompt)
    if not raw:
        return

    # Parse JSON
    items = []
    try:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            items = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        for m in re.finditer(r'"content"\s*:\s*"([^"]{10,80})"', raw):
            items.append({"content": m.group(1), "type": "factual"})

    if not items:
        return

    # Dedup + validate
    existing_fps = {q.get("content", "")[:40].lower() for q in existing}
    results = []
    now = _now_iso()
    for item in items[:max_items]:
        content = item.get("content", "").strip()
        if not content or len(content) < 10:
            continue
        if content[:40].lower() in existing_fps:
            continue
        kt = item.get("type", "factual")
        if kt not in ("factual", "procedural", "architectural", "pitfall"):
            kt = "factual"
        results.append({
            "content": content[:80],
            "classification": "[臨]",
            "knowledge_type": kt,
            "source": "per-turn",
            "at": now,
        })
        existing_fps.add(content[:40].lower())

    if results:
        # Re-read state for freshness
        state = read_state(session_id)
        if not state:
            return
        state["pending_extraction"] = results
        write_state(session_id, state)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)
    session_id = sys.argv[1]
    cwd = sys.argv[2]
    config = json.loads(sys.argv[3])
    try:
        extract(session_id, cwd, config)
    except Exception:
        pass  # Silent failure — never block Claude Code
