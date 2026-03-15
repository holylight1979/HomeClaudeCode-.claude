# Atom: OpenClaw 坑點速查

- Scope: global
- Confidence: [固]
- Source: 2026-02-26~27 holylight — 安裝、整合、除錯過程中踩到的坑
- Last-used: 2026-03-15
- Confirmations: 7
- Trigger: 遇到錯誤訊息、異常行為、啟動失敗、設定不生效、沒有回應、連不上、Discord bot、webhook 失敗、ngrok error、404、502
- Privacy: public

## 知識

| 坑點 | 解法 |
|------|------|
| PATH 快取 | 每裝完工具重開 PowerShell |
| openclaw 指令找不到 | `npm prefix -g` 路徑加入 PATH |
| LINE crash-loop WARN | 顯示 bug，重啟 gateway 後可用 |
| ngrok URL 會變 | 重啟後更新 LINE webhook URL（`/line/webhook`） |
| tools.profile 留空 → 工具消失 | 必須設 `profile: "full"` |
| Dashboard 顯示離線 | 用 `openclaw dashboard --no-open` 帶 token |
| Plugin import 外部模組失敗 | 不能 import TypeBox/plugin-sdk，用原生 JSON Schema + fetch |
| plugins.allow 未設定 → CRITICAL | 有 extensions 時必須明確列出 |
| Bridge port EADDRINUSE | 先 kill 舊 node process |
| Claude CLI 不在 PATH | 用 VS Code extension 的 `resources/native-binary/claude.exe` |
| SendKeys 對 webview 不可靠 | 用 clipboard + Ctrl+V paste |
| Plugin 圖片 MIME undefined | OpenAI API 需 `image_url` + data URL 格式 |
| WinForms npm .cmd 找不到 | `UseShellExecute=false` 不解析 .cmd，用 `cmd.exe /c` |
| PS 5.1 Get-Process.CommandLine null | 用 `Get-CimInstance Win32_Process` |
| Process.Kill 不殺子 process | 用 `taskkill /T /F /PID` tree kill |
| npm ngrok binary 是 macOS 版 | 用 `node_modules\ngrok\bin\ngrok.exe` |
| `__OPENCLAW_REDACTED__` 顯示 | 安全遮罩機制，不代表值遺失 |
| LINE 群組訊息靜默丟棄（200 OK 但無 log） | `groupPolicy: "allowlist"` 需搭配 `allowFrom`；群組 config 加 `"allowFrom": ["*"]` |
| 兩份 config 合併衝突 | workspace (`OPENCLAW_HOME/.openclaw/`) 和 user-level (`~/.openclaw/`) 會 merge；user-level 放最小設定避免覆蓋 |
| user-level config 的 plugins.allow 列不存在的 plugin → Config invalid | plugins.allow 只列該層級存在的 plugin，workspace-only plugin 不要放 user-level |
| Gateway 殺掉後自動 respawn | Scheduled Task 會重啟；要徹底停用 `openclaw gateway stop` 或刪除排程 |
| exec.security/ask enum 值錯誤 → Gateway 拒啟動 | security: deny/allowlist/**full**、ask: **off**/on-miss/always（不是 allow/never） |
| VS Code (Electron) get_ui_tree 看不到內部元素 | 純靠 screenshot+OCR 視覺辨識，不用 UI Automation |
| Claude Code 輸入框 mouse_click 不聚焦 | 用 `Ctrl+Escape` 快捷鍵聚焦（切換 focus/unfocus） |
| 切 tab 後看到自己 session 的 tool output | 切 tab 後立即截圖，或大量捲動 (50+) 跳過 |
| controlUi 預設 basePath `/` 攔截 plugin webhook routes → LINE 404 + `/health` 回 HTML | 設 `gateway.controlUi.basePath: "/ui"` 隔離 SPA catch-all。Dashboard URL 改為 `/ui#token=...`（#32435, #32584） |
| LINE health-monitor 每 30 分鐘 stale-socket 重啟 → webhook route 可能丟失 | basePath 隔離後問題減輕；若仍發生需重啟 Gateway（上游 bug #26478, #28622） |
| `allowBots: "mentions"` → Config invalid | `allowBots` 只接受 boolean（`true`/`false`），文件說支援 `"mentions"` 但 schema 不允許 |
| `channels.discord.requireMention` → Config invalid | 2026.3.2 不認可此 key（已移除或從未在 discord channel 層級支援），刪除即可 |
| `channels.discord.dm.policy` 冗餘 → Doctor 每次啟動警告 | 上層已有 `dmPolicy`，移除 `dm.policy` 避免重複 |
| Panel Gateway 啟動失敗但無錯誤訊息 | 舊版 `StartProcess` 用 `catch {}` 吞掉所有錯誤；已改為 `TryStartGateway()` 捕獲 stderr + MessageBox 顯示 |
| Gateway 冷啟動需 7~11 秒 | Panel health check 原本只等 3 秒就放棄；已改為 15 秒 polling |
| `blockStreaming: true` + `streaming: "off"` = **deadlock** | streaming off 不產生 streaming 事件，blockStreaming 等信號永不來 → 訊息卡住永不送出。正確：`blockStreaming: false` |
| user-level config 有 `channels.discord` → Discord DM 靜默丟棄 | user-level 的 channel 設定在 merge 時干擾 workspace 完整設定（缺 token/dmPolicy 等）。**user-level 不應有任何 channel 設定** |
| user-level plugin entries 列已移除的 plugin → 載入異常 | 2026.3.2 移除了 `discord-reader`/`computer-use`/`claude-bridge`，user-level 殘留 entries 需清理 |
| Heartbeat nagging loop: 相同警報 30+ 次重複無法自動解決 | 需加入 auto-resolution 或 N 次後靜音機制。目前只能人工介入 |
| Weekly identity report cron 失敗 | 需要建立 `atoms/persons/_registry.md` 等基礎路徑（已有但格式/內容不足） |
| Phase 4 session 提取：JSON 欄位名稱不一致 | session JSON 的 peer/identity 欄位命名隨版本變動，提取時需容錯處理多種 key 名 |
| Phase 4 persons owner/user 分類混淆 | holylight 是 owner 不是 user；分層結構需在 `_registry.md` 明確標註角色 |
| LINE 無法回傳圖片 | LINE channel 可收圖但無法主動發送圖片/截圖給使用者 |
| Google Maps goo.gl 短網址無法解析 | OpenClaw 無法展開 Google Maps 短網址取得實際地址 |
| 工作空間沙箱限制 (`workspaceOnly`) | 無法寫入 `平台工作空間\`，需調整 `fs.workspaceOnly` 設定或使用 workspace 內路徑 |
| Discord 洗版問題（長內容分割） | 長 JSON/markdown 用「摘要 + 檔案附件」策略，已建立 discord-global-policy.md |
| workspace hooks 不會自動載入 | `workspace/hooks/` 有 HOOK.md + handler.ts 不代表已安裝。必須跑 `openclaw hooks install <path>` 才會複製到 `~/.openclaw/hooks/` 並生效 |
| `message:sent` 事件不觸發（所有 auto-reply） | v2026.3.2 的 auto-reply pipeline（Discord/LINE）完全繞過 `deliverOutboundPayloads`，走 reply dispatcher → channel plugin。`message:sent` 只在 CLI `--deliver` 和 cron 時觸發。**已解決**：memory-writer V4 改用 `message:before` + transcript reading |
| hook 安裝位置混淆 | 開發目錄 `.openclaw/workspace/hooks/` 是原始碼；運行目錄 `~/.openclaw/hooks/` 是 Gateway 實際載入的位置。修改後需重新 `openclaw hooks install` 同步 |
| atom-context-injector 注入依賴 bootstrapFiles | hook 透過 `ctx.bootstrapFiles` 找 USER.md 並 append content。若 USER.md 不存在或 missing=true，注入靜默失敗 |
| Gateway 啟動不帶 `OPENCLAW_CONFIG_PATH` → 用錯 config | `openclaw gateway --force` 不會自動帶 env var；必須用 `start-gateway.bat`（內含 `set OPENCLAW_CONFIG_PATH=...`）或手動設定。用錯 config 會導致 model 錯誤 + hooks 不載入 |
| `ctx.workspaceDir` 不是 internal workspace | hook 收到的 `ctx.workspaceDir` 是專案根 `E:\OpenClawWorkSpace`，不是 `.openclaw/workspace/`。存取 atoms/preprocessor 需自行拼接 `.openclaw/workspace/` |
| `.openclaw/workspace/` 是獨立 git repo | 父 repo 無法用 `git add` 追蹤其檔案。workspace 的 hooks/atoms 需在 workspace repo 內 commit |
| session 級「記住」不跨頻道 | agent 收到「記住 X」時只存在當前 session context，不會自動寫入 atom。需要 agent 主動 fs_write 或 memory-writer hook 觸發。**已解決**：memory-writer V4 正常運作 |
| workspace hooks `.ts` 載入失敗（靜默） | `.openclaw/workspace/package.json` 有 `"type": "commonjs"`，導致 hooks 的 `.ts` 檔案被當 CJS → `import` 語句 SyntaxError。Gateway 的 `catch` 靜默吞掉錯誤。**修法**：在 `workspace/hooks/` 加 `package.json` with `"type": "module"` |

## 行動

- 遇到未知錯誤時：先查本表，再查 `_AIDocs/_CHANGELOG.md` 的修正記錄
- 新發現的坑：追加到本 atom，更新 Last-used 日期
