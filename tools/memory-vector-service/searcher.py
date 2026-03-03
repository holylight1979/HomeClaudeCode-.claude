"""
searcher.py — 語意搜尋引擎

使用 LanceDB 進行向量搜尋。
"""

import json
from typing import Any, Dict, List, Optional

from indexer import create_embedder, search_vectors


def search(
    query: str,
    config: Dict[str, Any],
    top_k: int = 5,
    min_score: float = 0.65,
    layer_filter: Optional[str] = None,
    include_distant: bool = False,
    embedder=None,
) -> List[Dict[str, Any]]:
    """Semantic search across indexed atoms.

    Returns list of results sorted by score (descending):
    [{"atom_name", "title", "section", "text", "score", "confidence", "file_path", "layer", "line_number"}, ...]
    """
    if not query.strip():
        return []

    if embedder is None:
        embedder = create_embedder(config)

    # Embed query
    query_vec = embedder.embed([query])
    if not query_vec or not query_vec[0]:
        return []

    # Search LanceDB
    # LanceDB cosine metric: _distance = 1 - cosine_similarity
    raw_results = search_vectors(
        query_vec[0],
        top_k=top_k * 3,  # Fetch more for dedup
        layer_filter=layer_filter,
    )

    if not raw_results:
        return []

    # Process and dedup by atom
    hits: List[Dict[str, Any]] = []
    seen_atoms: Dict[str, float] = {}

    for row in raw_results:
        distance = row.get("_distance", 1.0)
        score = 1.0 - distance  # cosine similarity

        if score < min_score:
            continue

        atom_key = f"{row.get('layer', '')}:{row.get('atom_name', '')}"

        # Post-filter for "project" layer
        if layer_filter == "project" and not row.get("layer", "").startswith("project:"):
            continue

        # Dedup: keep highest scoring chunk per atom
        if atom_key in seen_atoms:
            if score <= seen_atoms[atom_key]:
                continue
        seen_atoms[atom_key] = score
        hits = [h for h in hits if f"{h['layer']}:{h['atom_name']}" != atom_key]

        hits.append({
            "atom_name": row.get("atom_name", ""),
            "title": row.get("title", ""),
            "section": row.get("section", ""),
            "text": row.get("text", ""),
            "score": round(score, 4),
            "confidence": row.get("confidence", ""),
            "file_path": row.get("file_path", ""),
            "layer": row.get("layer", ""),
            "line_number": int(row.get("line_number", 0)),
        })

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:top_k]


def search_raw(
    query: str,
    config: Dict[str, Any],
    top_k: int = 10,
    min_score: float = 0.5,
    embedder=None,
) -> List[Dict[str, Any]]:
    """Raw search without atom-level dedup. Used by reranker."""
    if not query.strip():
        return []

    if embedder is None:
        embedder = create_embedder(config)

    query_vec = embedder.embed([query])
    if not query_vec or not query_vec[0]:
        return []

    raw_results = search_vectors(query_vec[0], top_k=top_k)

    hits = []
    for row in raw_results:
        distance = row.get("_distance", 1.0)
        score = 1.0 - distance
        if score < min_score:
            continue
        hits.append({
            "atom_name": row.get("atom_name", ""),
            "title": row.get("title", ""),
            "section": row.get("section", ""),
            "text": row.get("text", ""),
            "score": round(score, 4),
            "confidence": row.get("confidence", ""),
            "file_path": row.get("file_path", ""),
            "layer": row.get("layer", ""),
            "line_number": int(row.get("line_number", 0)),
        })

    return hits


if __name__ == "__main__":
    import sys
    from config import load_config

    query_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "測試搜尋"
    cfg = load_config()
    results = search(query_text, cfg, top_k=5, min_score=0.5)
    print(json.dumps(results, indent=2, ensure_ascii=False))
