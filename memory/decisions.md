# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統
- Last-used: 2026-03-05
- Confirmations: 5
- Type: decision

## 知識

- [固] 原子記憶 V2.3：Hybrid RECALL + Ranked Search + Workflow Guardian
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] MCP 傳輸格式：JSONL，protocolVersion 2025-11-25
- [固] 記憶檢索統一用 Python V2.2，已移除 Node.js memory-v2
- [固] Stop hook 只保留 Guardian 閘門，移除 Discord 通知
- [固] 雙 LLM：Claude Code（雲端決策）+ Ollama qwen3（本地語意處理）
- [固] Ollama models: qwen3-embedding:0.6b + qwen3:1.7b
- [固] Vector DB: ChromaDB（i7-3770 不支援 AVX2，LanceDB 不適用）
- [固] OpenClaw workspace atoms 透過 additional_atom_dirs 整合（extra:openclaw 層，5 atoms）
- [固] Node.js memory-v2 已退役（2026-03-05），由 V2.3 Python 版取代，腳本保留備回退

## 行動

- 記憶寫入走 write-gate 品質閘門
- 向量搜尋 fallback 順序：Ollama → sentence-transformers → keyword
- Guardian 閘門最多阻止 2 次，第 3 次強制放行

## 演化日誌

- 2026-03-05: 建立 README.md（哲學/Token比較/流程圖/大型專案使用法）+ Install-forAI.md 安裝指南
- 2026-03-05: V2.3 合併安裝，從公司版遷移核心工具鏈到家用電腦
- 2026-03-05: LanceDB → ChromaDB（i7-3770 不支援 AVX2，LanceDB search crash）
- 2026-03-05: embedding model 指定 qwen3-embedding:0.6b（避免 latest 4.7GB 版 timeout）
- 2026-03-05: search_min_score 從 0.65 降至 0.45（0.6b 小模型 score 普遍較低）
- 2026-03-05: OpenClaw atoms 整合（additional_atom_dirs），Node.js memory-v2 退役
- 2026-03-05: V2.3 全面升級 OpenClaw Phase 1+2 完成 — MEMORY.md 3欄格式修正、root CLAUDE.md、4個大師級 atom
