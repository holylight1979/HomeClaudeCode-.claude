# Atom: Gateway chat.send 與 LINE 訊息路由

- Scope: global
- Confidence: [固]
- Source: 2026-03-04 holylight — OpenClaw 2026.3.1 source code analysis
- Last-used: 2026-03-06
- Confirmations: 7
- Trigger: chat.send 行為、LINE 推送、cross-context messaging、session routing、deliverOutboundPayloads、OriginatingChannel、LINE Push API
- Privacy: public

## 知識

### chat.send 行為（line 10699）

### 流程

1. 驗證 params → 清理 message → 處理 attachments
2. `loadSessionEntry(rawSessionKey)` 載入 session
3. 檢查 send policy → 去重 (idempotencyKey)
4. **同步回應** `{ runId, status: "started" }`
5. `dispatchInboundMessage()`:
   - 設 `OriginatingChannel: "internal"` ← **關鍵**
   - 建立 reply dispatcher
   - 跑 agent（LLM + tools）
6. 完成後 `broadcastChatFinal()` → broadcast 到所有 WebSocket clients

### 核心限制

**chat.send 不會自動送到 LINE/Discord**。
- `OriginatingChannel` 被設為 `"internal"`
- 回應只透過 WebSocket broadcast 回傳給連接的 client
- **沒有 `targetChannel` 參數**（GitHub issue #22725 提議中但未合併）

### 跨頻道限制

> "Cross-context messaging denied: action=send target provider"

session 綁定在特定 channel context，webchat 送的訊息不會自動跨到 LINE。

## LINE Outbound Delivery（如何主動推送到 LINE）

### 三種方式讓訊息到 LINE

1. **Agent 的 `send` tool**：agent 在執行中使用 send tool 主動送訊息到 channel
2. **`announce` flow**：`runSubagentAnnounceFlow` — 定時任務 (cron) 用這個
3. **直接 API**：`deliverOutboundPayloads({ channel: "line", to: "<userId>", payloads: [...] })`

### LINE Push API 路徑

`deliverOutboundPayloads()` (deliver-GmIEfm3k.js, line 971)
→ `deliverOutboundPayloadsCore()`
→ `createChannelHandler()` → `loadChannelOutboundAdapter("line")`
→ LINE adapter `sendText()` / `sendPayload()`
→ `pushMessageLine(to, text, opts)` (reply-XaR8IPbY.js, line 42355)
→ `sendMessageLine()` → `pushLineMessages()`
→ `@line/bot-sdk` `MessagingApiClient.pushMessage({ to: chatId, messages })`

### LINE Webhook Inbound 路徑

POST `/line/webhook`（registered via `registerPluginHttpRoute` in `monitorLineProvider()`, reply-XaR8IPbY.js line 43393）
→ Gateway auth enforced（`shouldEnforceGatewayAuthForPluginPath()`）
→ `createLineNodeWebhookHandler()` 驗證 `X-Line-Signature`（HMAC-SHA256）
→ `dispatchReplyWithBufferedBlockDispatcher()`
→ reply: `replyMessageLine()` (用 reply token) 或 fallback: `pushMessageLine()`

## Session Keys（確認的）

| Key | 用途 | 綁定 |
|-----|------|------|
| `agent:main:main` | 全域 main session | 最後使用的 channel（可能被 webchat 覆蓋）|
| `agent:main:direct:holylight` | per-peer DM session | LINE user `U556bc083405a12bb3a9d2dbb66983386` |
| `agent:main:discord:channel:*` | Discord channel session | Discord guild channel |

## Session Store

- 檔案：`{stateDir}/store/sessions.json` 或 `{stateDir}/agents/{agentId}/store/sessions.json`
- 記憶體 cache + TTL
- Windows: retry 3 次 / 50ms（atomic write race condition）
- Prune: 30 天 / 500 entries / 10MB rotate

## 實際可行的 Claude Code → LINE 方案

### 方案 A：在 chat.send 的 message 中指示 OpenClaw 轉發

在訊息中明確告訴 OpenClaw「請把以下內容透過 LINE 發給 holylight」，讓 agent 自己用 send tool 推送。**依賴 agent 是否有 send tool 權限**。

### 方案 B：直接呼叫 LINE Push API（已實作）

`line-push.js` — 繞過 OpenClaw，直接用 LINE Messaging API Push 推送。
- 腳本: `.claude/scripts/line-push.js`
- 用法: `node line-push.js "訊息內容"`
- 自動從 openclaw.json 讀 channelAccessToken + identityLinks 取 LINE userId
- 2026-03-04 測試通過（status: delivered）

### 方案 C：等 2026.3.2+ 的 cross-context messaging

GitHub issue #22725 — 尚未合併。

## 參考連結

- [Cross-context messaging issue #22725](https://github.com/openclaw/openclaw/issues/22725)
- [Gateway broadcasts to all clients #32579](https://github.com/openclaw/openclaw/issues/32579)
- [Gateway Protocol (WebSocket)](https://www.learnclawdbot.org/docs/gateway/protocol)
- [DeepWiki: OpenClaw internals](https://deepwiki.com/openclaw/openclaw)
- Source: `gateway-cli-tzSO700C.js` line 10699 (chat.send), `deliver-GmIEfm3k.js` line 971 (delivery), `reply-XaR8IPbY.js` line 42355 (LINE push)
