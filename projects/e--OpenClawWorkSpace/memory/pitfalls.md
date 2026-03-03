# Atom: OpenClaw 坑點速查

- Scope: global
- Confidence: [固]
- Source: 2026-02-26~27 holylight — 安裝、整合、除錯過程中踩到的坑
- Last-used: 2026-02-28
- Trigger: 遇到錯誤訊息、異常行為、啟動失敗、設定不生效時
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

## 行動

- 遇到未知錯誤時：先查本表，再查 `_AIDocs/_CHANGELOG.md` 的修正記錄
- 新發現的坑：追加到本 atom，更新 Last-used 日期
