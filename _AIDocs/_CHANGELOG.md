# 變更記錄

> 保留最近 ~8 筆。舊條目移至 `_CHANGELOG_ARCHIVE.md`。

---

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-03-22 | **V2.17 對外文件全面更新**：全文件版本號 V2.15→V2.17 統一。README 版本歷史補 V2.16/V2.17。Architecture 加入自我迭代自動化+覆轍偵測段落 | `CLAUDE.md`, `README.md`, `Install-forAI.md`, `_AIDocs/*.md`, `memory/decisions.md` |
| 2026-03-22 | **V2.17 覆轍偵測**：跨 session 重複失敗模式自動警告。寄生式設計附著 episodic atom。SessionEnd 寫入覆轍信號，SessionStart 掃描注入 `[Guardian:覆轍]` | `hooks/workflow-guardian.py`, `memory/decisions-architecture.md` |
| 2026-03-22 | **V2.16 自我迭代自動化**：衰減分數掃描 + [臨]→[觀] 自動晉升 + 震盪持久化 + config.json `self_iteration` 區塊 | `hooks/workflow-guardian.py`, `workflow/config.json`, `memory/decisions-architecture.md` |
| 2026-03-19 | **V2.15 定義版本**：全文件版本號 V2.12→V2.15 統一。移除內嵌版本標註。README 版本歷史補 V2.13/V2.14/V2.15 | `CLAUDE.md`, `README.md`, `Install-forAI.md`, `_AIDocs/*.md`, `memory/decisions*.md`, `rules/session-management.md` |
| 2026-03-19 | **V2.14 Token Diet**：注入前 strip 9 種 metadata + 行動/演化日誌。SessionEnd 從 byte_offset 跳已萃取段。cross-session lazy search 預篩。省 ~1550 tok/session | `hooks/workflow-guardian.py`, `hooks/extract-worker.py`, `memory/MEMORY.md`, `workflow/config.json` |
| 2026-03-19 | **V2.13 Failures 自動化系統**：Guardian 偵測失敗關鍵字 → detached extract-worker 萃取失敗模式 → 三維路由自動寫入對應 failure atom | `hooks/extract-worker.py`, `hooks/workflow-guardian.py`, `workflow/config.json`, `memory/failures/` |
| 2026-03-19 | **atom 精準拆分+設定精修**：toolchain-ollama 獨立拆分 + workflow-icld 拆分 + trigger 瘦身 + failures 拆分子 atoms + GIT 流程去重 + 設定檔去重/瘦身/統一管理 | `memory/*.md`, `workflow/config.json` |
| 2026-03-19 | **vector service timeout 修正**：冷啟動 7.5s 但 caller timeout 2-5s，調整 timeout + 預熱 | `hooks/workflow-guardian.py`, `tools/memory-vector-service/` |
_(舊條目已移至 `_CHANGELOG_ARCHIVE.md`。最近移入：2026-03-18 逐輪增量萃取 + 注入精準化 + Fix Escalation)_
