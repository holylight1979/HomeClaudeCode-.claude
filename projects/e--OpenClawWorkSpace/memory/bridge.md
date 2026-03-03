# Atom: LINE → Claude Code Bridge

- Scope: global
- Confidence: [固]
- Source: 2026-02-27 holylight — Bridge 完整整合（server + plugins + MCP + hooks）
- Last-used: 2026-02-27
- Trigger: 涉及 Bridge 服務、computer-use、Claude Code 整合、LINE→Claude 操作
- Privacy: public

## 知識

### Bridge Service
- 路徑：`E:\OpenClawWorkSpace\scripts\openclaw-bridge-server.js`
- Port 3847，loopback only，Bearer token 認證
- Endpoints: screenshot, click, type, key, window-focus, window-list, clipboard, /claude/execute, /notify/*

### OpenClaw Plugins
- `computer-use`：7 個桌面操作工具，fetch 到 bridge
- `claude-bridge`：inject/observe/execute，UI 自動化注入 VS Code Claude

### Claude Code MCP
- `@anthropic-ai/computer-use` — 官方 computer-use
- `@anthropic-ai/browser-use` — 瀏覽器自動化
- `openclaw-notify` — 自建，`notify_user` 工具（發 Discord/LINE 通知）

### 觸發方式
- 指令：`/vscc`, `/vsccc`, `/vscodeclaudecode`
- 語意：「用 claude code」「請用電腦執行」「用本機的 claude 做」

### 流程
1. focus VS Code → Command Palette → Claude: Focus Input → paste → Enter
2. 截圖 + vision 解讀 → 摘要回傳 LINE
3. Fallback：VS Code 沒開 → `claude -p` headless

### 注意
- Claude CLI：`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude.exe`
- Bridge token：`BRIDGE_TOKEN` env var（預設待更換）
- 需先啟動 bridge（已整合到 OpenClaw-Start.bat）

## 原子記憶系統

- ai-kb-framework：`E:\OpenClawWorkSpace\ai-kb-framework\`
- 完整規格：`E:\OpenClawWorkSpace\skills\atomic-memory\SKILL.md`
- Scope：global / users/{platform}_{id} / channels / merged/{alias}
- Confidence 映射：[固]=VERIFIED, [觀]=OBSERVED, [臨]=INFERRED
- 隱私分級：public / private / sensitive

## 行動

- Bridge 相關問題：先確認 bridge service 是否啟動（`curl http://127.0.0.1:3847/health`）
- 修改 plugin：圖片回傳必須用 OpenAI `image_url` 格式（不是 Anthropic 格式）
- 新增 MCP server：加到 `~/.claude.json` 的 mcpServers + repo 的 `claude/mcp-servers.json`
