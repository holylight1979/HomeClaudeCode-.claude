# 變更記錄

> 保留最近 ~8 筆。舊條目移至 `_CHANGELOG_ARCHIVE.md`。

---

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-03-29 | **Dead code 清理**：per_turn 重啟、rdchat reauth marker 系統移除（~70行）、.mcp.json 刪除、stale_threshold_hours 移除、causal_graph stubs 刪除、DESIGN.md 歸檔至 _reference | `tools/ollama_client.py`, `hooks/wisdom_engine.py`, `hooks/wg_core.py`, `workflow/config.json` |
| 2026-03-29 | **V2.22 注入閘門修正**：plan/draft 內容分類過濾 + `wg_content_classify.py` 共用模組。extract-worker/episodic/write_gate 三層攔截 | `hooks/extract-worker.py`, `hooks/wg_episodic.py`, `hooks/wg_content_classify.py` |
| 2026-03-29 | **全面健檢（23 bug 修正）**：資源洩漏（7.6B model→0.6b、fallback→none）、extract-worker content 解析/cp950/str.get()、reranker import、episodic 子目錄、MCP check、SQL injection 防禦 | `hooks/*.py`, `tools/ollama_client.py`, `tools/memory-vector-service/` |
| 2026-03-29 | **向量服務穩定性**：防 crash + 防進程連帶被殺 | `tools/memory-vector-service/` |
| 2026-03-24 | **V2.21 Hook 模組化**：workflow-guardian 拆分為 wg_core/wg_paths/wg_extraction/wg_intent/wg_episodic 等模組 | `hooks/wg_*.py` |
| 2026-03-24 | **V2.20 路徑模組化**：wg_paths.py 獨立管理所有路徑常數與函式 | `hooks/wg_paths.py`, `hooks/wg_core.py` |
| 2026-03-22 | **V2.17 覆轍偵測 + 自我迭代自動化 + 文件更新** | `hooks/workflow-guardian.py`, `CLAUDE.md`, `README.md`, `_AIDocs/*.md` |
| 2026-03-19 | **V2.13–V2.15**：Failures 自動化 + Token Diet + 版本統一 | `hooks/*.py`, `workflow/config.json`, `memory/*.md` |
_(舊條目已移至 `_CHANGELOG_ARCHIVE.md`。最近移入：2026-03-18 逐輪增量萃取 + 注入精準化 + Fix Escalation)_
