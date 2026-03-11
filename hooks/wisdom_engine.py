#!/usr/bin/env python3
"""
wisdom_engine.py — Wisdom Engine V2.8

Three forces: Causal Graph, Situation Classifier, Reflection Engine.
Called by workflow-guardian.py. Cold start = zero tokens.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

WISDOM_DIR = Path.home() / ".claude" / "memory" / "wisdom"
CAUSAL_GRAPH_PATH = WISDOM_DIR / "causal_graph.json"
REFLECTION_PATH = WISDOM_DIR / "reflection_metrics.json"

DEFAULT_WEIGHTS = {"file": 2.0, "feature": 4.0, "arch": 5.0, "quick": -4.0, "thorough": 3.0}
ARCH_KEYWORDS = {"架構", "refactor", "重構", "migrate", "migration", "重寫"}
QUICK_KEYWORDS = {"快速", "簡單", "quick", "simple", "小改"}
THOROUGH_KEYWORDS = {"好好", "徹底", "thorough", "完整", "仔細"}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)
    except OSError as e:
        print(f"[wisdom] save error {path.name}: {e}", file=sys.stderr)
        if tmp.exists():
            tmp.unlink()


# ── Force 1: Causal Graph ────────────────────────────────────────────────────

def get_causal_warnings(touched_files: List[str], max_depth: int = 2) -> List[str]:
    """BFS over causal graph → ≤3 warning strings."""
    graph = _load_json(CAUSAL_GRAPH_PATH, {"nodes": {}, "edges": []})
    edges = graph.get("edges", [])
    if not edges or not touched_files:
        return []

    touched_set = set()
    for f in touched_files:
        norm = f.replace("\\", "/")
        touched_set.add(norm)
        if "/" in norm:
            touched_set.add(norm.rsplit("/", 1)[-1])

    warnings, visited, warned_edges = [], set(), set()
    queue = [(f, 0) for f in touched_set]
    while queue:
        node, depth = queue.pop(0)
        if node in visited or depth > max_depth:
            continue
        visited.add(node)
        for edge in edges:
            if edge.get("confidence", 0) < 0.6:
                continue
            e_from = edge.get("from", "")
            if node == e_from or node in e_from or e_from in node:
                target = edge.get("to", "")
                edge_key = (e_from, target)
                if edge_key in warned_edges:
                    continue
                warned_edges.add(edge_key)
                through = edge.get("through", "")
                evidence = edge.get("evidence", "")
                hint = evidence or (f"via {through}" if through else "")
                warnings.append(
                    f"[因果] {e_from} ←{through}→ {target} ({edge['confidence']:.2f})"
                    + (f" | {hint}" if hint else "")
                )
                if target not in visited:
                    queue.append((target, depth + 1))
    return warnings[:3]


def add_causal_edge(
    edge_from: str,
    edge_to: str,
    relation: str = "coupled_via",
    through: str = "",
    evidence: str = "",
    confidence: float = 0.7,
) -> bool:
    """Add a new edge to the causal graph. Returns True if added, False if duplicate."""
    graph = _load_json(CAUSAL_GRAPH_PATH, {"nodes": {}, "edges": []})
    edges = graph.get("edges", [])

    # Dedup: skip if same from→to already exists
    for edge in edges:
        if edge.get("from") == edge_from and edge.get("to") == edge_to:
            return False

    # Auto-create nodes
    nodes = graph.setdefault("nodes", {})
    for n in (edge_from, edge_to):
        if n not in nodes:
            ntype = "file" if "." in n or "/" in n else "concept"
            nodes[n] = {"type": ntype, "domain": "auto"}
    if through and through not in nodes:
        nodes[through] = {"type": "concept", "domain": "auto"}

    edges.append({
        "from": edge_from,
        "to": edge_to,
        "relation": relation,
        "through": through,
        "confidence": confidence,
        "evidence": evidence or f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} auto",
    })
    graph["edges"] = edges
    _save_json(CAUSAL_GRAPH_PATH, graph)
    return True


def update_causal_confidence(edge_from: str, edge_to: str, hit: bool) -> None:
    """Bayesian update: hit → approach 1.0, miss → decay toward 0."""
    graph = _load_json(CAUSAL_GRAPH_PATH, {"nodes": {}, "edges": []})
    edges = graph.get("edges", [])
    updated = False
    for edge in edges:
        if edge.get("from") == edge_from and edge.get("to") == edge_to:
            if hit:
                edge["confidence"] = edge["confidence"] * 0.9 + 0.1
            else:
                edge["confidence"] = edge["confidence"] * 0.95
            updated = True
            break
    graph["edges"] = [e for e in edges if e.get("confidence", 0) >= 0.3]
    if updated:
        _save_json(CAUSAL_GRAPH_PATH, graph)


# ── Force 2: Situation Classifier ────────────────────────────────────────────

def classify_situation(prompt_analysis: Dict[str, Any]) -> Dict[str, str]:
    """Weighted scoring → approach (direct/confirm/plan) + inject string."""
    metrics = _load_json(REFLECTION_PATH, {})
    weights = metrics.get("calibrated_weights", DEFAULT_WEIGHTS)
    keywords = set(prompt_analysis.get("keywords", []))
    intent = prompt_analysis.get("intent", "")

    file_count = min(prompt_analysis.get("estimated_files", 1), 5)
    score = (
        file_count * weights.get("file", 2.0)
        + (1 if intent == "feature" else 0) * weights.get("feature", 4.0)
        + (1 if keywords & ARCH_KEYWORDS else 0) * weights.get("arch", 5.0)
        + (1 if keywords & QUICK_KEYWORDS else 0) * weights.get("quick", -4.0)
        + (1 if keywords & THOROUGH_KEYWORDS else 0) * weights.get("thorough", 3.0)
    )

    if score <= 4:
        return {"approach": "direct", "inject": ""}
    elif score <= 10:
        return {"approach": "confirm", "inject": "[情境:確認] 跨檔修改，建議先列範圍"}
    else:
        return {"approach": "plan", "inject": "[情境:規劃] 架構級變更，建議 Plan Mode"}


# ── Force 3: Reflection Engine ───────────────────────────────────────────────

def _empty_reflection() -> Dict[str, Any]:
    return {
        "window_size": 10,
        "metrics": {
            "first_approach_accuracy": {
                "single_file": {"correct": 0, "total": 0},
                "multi_file": {"correct": 0, "total": 0},
                "architecture": {"correct": 0, "total": 0},
            },
            "over_engineering_rate": {
                "user_reverted_or_simplified": 0, "total_suggestions": 0,
            },
            "silence_accuracy": {
                "held_back_and_user_didnt_ask": 0,
                "held_back_but_user_needed": 0,
                "spoke_but_user_ignored": 0,
            },
        },
        "calibrated_weights": dict(DEFAULT_WEIGHTS),
        "blind_spots": [],
        "last_reflection": None,
    }


def get_reflection_summary() -> List[str]:
    """SessionStart: inject blind spot reminders (only if data exists)."""
    metrics = _load_json(REFLECTION_PATH, {})
    blind_spots = metrics.get("blind_spots", [])
    if not blind_spots:
        return []
    return [f"[自知] {spot}" for spot in blind_spots[:2]]


def reflect(state: Dict[str, Any]) -> None:
    """SessionEnd: update accuracy stats from session data."""
    metrics = _load_json(REFLECTION_PATH, _empty_reflection())
    faa = metrics.setdefault("metrics", _empty_reflection()["metrics"]) \
                 .setdefault("first_approach_accuracy", {})

    mod_files = state.get("modified_files", [])
    file_count = len(set(m.get("path", "") for m in mod_files))
    if file_count <= 1:
        task_type = "single_file"
    elif file_count <= 4:
        task_type = "multi_file"
    else:
        task_type = "architecture"

    bucket = faa.setdefault(task_type, {"correct": 0, "total": 0})
    bucket["total"] += 1
    if state.get("wisdom_retry_count", 0) == 0:
        bucket["correct"] += 1

    # Blind spot detection
    blind_spots = []
    for tt, b in faa.items():
        total = b.get("total", 0)
        correct = b.get("correct", 0)
        if total >= 3:
            rate = correct / total
            if rate < 0.7:
                blind_spots.append(f"{tt} 首次正確率 {rate:.0%}")
    metrics["blind_spots"] = blind_spots
    metrics["last_reflection"] = datetime.now(timezone.utc).isoformat()
    _save_json(REFLECTION_PATH, metrics)


def track_retry(state: Dict[str, Any], file_path: str) -> None:
    """PostToolUse: count repeated edits to the same file as retries."""
    edits = state.get("modified_files", [])
    norm = file_path.replace("\\", "/")
    count = sum(1 for m in edits if m.get("path", "").replace("\\", "/") == norm)
    if count >= 2:
        state["wisdom_retry_count"] = state.get("wisdom_retry_count", 0) + 1
