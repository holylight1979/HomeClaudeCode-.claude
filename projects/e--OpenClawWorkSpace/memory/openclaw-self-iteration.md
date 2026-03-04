# Atom: OpenClaw 自我迭代與升級

- Scope: global
- Confidence: [觀]
- Source: 2026-03-05 V2.3 升級全面掃描
- Last-used: 2026-03-05
- Trigger: 升級 OpenClaw, 版本管理, config merge, plugin 管理, 自我除錯, 迭代, 維護, 更新版本, 除錯流程
- Privacy: public

## 知識

### 升級 SOP

1. **備份**: 複製 `E:\OpenClawWorkSpace` 整個目錄（含 .openclaw/）
2. **停服務**: OpenClawPanel → Stop All（或 `openclaw gateway stop`）
3. **升級**: `npm install -g openclaw@{版本}`（非原始碼建置）
4. **Config merge**: OpenClaw 升級會嘗試 merge config，但需手動確認
   - 核對 `openclaw.json` 有無新增必要欄位
   - 確認 channels 設定未被覆蓋
5. **啟動測試**: `start-gateway.bat` → health check → 測試 Discord/LINE
6. **更新記錄**: `_CHANGELOG.md` + 相關 atoms

### 版本歷史

| 版本 | 日期 | 重要變更 |
|------|------|---------|
| 2026.3.1 | 初始版 | memorySearch schema 精簡、plugins 需 `enable` 明確啟用 |
| 2026.3.2 | 2026-03-04 | controlUi basePath 修復、LINE groupAllowFrom 新增 |

### 升級注意事項（2026.3.1→3.2 經驗）

- `memorySearch` schema 精簡（移除 mode/maxAtoms/minScore 等）
- plugins 需 `openclaw plugins enable` 明確啟用
- LINE `groupAllowFrom` 新增（取代嵌套 `groups.*.allowFrom`）
- `discord-reader`/`computer-use`/`claude-bridge` plugins 已移除
- user-level config 不可有 `channels.discord`（merge 干擾）

### Plugin 管理

- 安裝: `openclaw plugins install <name>`
- 啟用: `openclaw plugins enable <name>`
- 清單: `openclaw plugins list`
- **注意**: plugin 需明確啟用，安裝不等於啟用

### 自我除錯流程

1. **Gateway 不啟動**
   - 確認 `OPENCLAW_CONFIG_PATH` → `auth-profiles.json` 存在 → port 未被佔用
   - Panel 會捕獲 stderr 顯示錯誤

2. **Discord 無回應**
   - 檢查 groupPolicy/dmPolicy → allowFrom → blockStreaming≠true
   - 確認 bot token 有效 + intents 正確

3. **LINE webhook 404**
   - controlUi basePath 必須是 "/ui"（不是 "/"）
   - ngrok traffic-policy 注入 Bearer token
   - webhook 路徑: `/line/webhook`（不是 `/channels/line/webhook`）

4. **記憶不觸發**
   - Gateway: 確認 hooks enabled + Ollama 運行
   - Claude Code: 確認 MEMORY.md 3 欄格式 + workflow-guardian.py

5. **VRAM 不足**
   - 停用 reranker（省 0.4GB）→ 停用 A21 profiler（再省 0.4GB）→ A4-only 模式

### GC 排程

- Windows Scheduled Task: `OpenClaw-AtomGC`
- 執行時間: 每週一 04:00
- 腳本: `scripts/run-gc.js --exec`
- 功能: [臨]30d 歸檔、[觀]90d 列 review、superseded 30d 歸檔、staging 過期清理

### 系統健康監控

- Heartbeat: 每 30 分鐘自動執行 preprocessor
- 報表: `preprocessor-reports/` 目錄
- `system-health.md` atom: 自動更新狀態（HEARTBEAT_OK / ACTION_REQUIRED）
- CHANGELOG 超 8 筆: 自動標記需滾動淘汰

## 行動

- 升級前：必須備份 + 停服務
- 升級後：核對 config merge 結果 + 測試各平台
- 定期維護：檢查 preprocessor-reports/ 是否有 ACTION_REQUIRED
- 記憶系統異常：依除錯流程逐步排查
