# Atom: gateway-internal-hooks

- **Scope**: project (OpenClawWorkSpace)
- **Confidence**: [固] — 從 Gateway dist 原始碼逆向確認
- **Trigger**: internal hook, registerInternalHook, triggerInternalHook, createInternalHookEvent, HOOK.md, HookRunner, bundled hooks, gateway:startup, agent:bootstrap, message:received, message:sent, message:transcribed, message:preprocessed, command:new, command:reset, command:stop, hook 載入, hook 事件, workspace hook 開發
- **Last-used**: 2026-03-06
- **Confirmations**: 1
- **Type**: architecture
- **Tags**: openclaw, gateway, hooks, internal-hooks, hookrunner, plugin
- **Related**: memory-writer-investigation, openclaw-architecture, openclaw-config-intelligence
- **Supersedes**: (none)

---

## 知識段落

### 1. 雙 Hook 架構（兩套完全獨立的系統）

| 面向 | Internal Hooks | HookRunner |
|------|---------------|------------|
| **用途** | Workspace/managed hooks 事件通知 | Plugin 生命週期 hooks |
| **Registry** | `globalThis.__openclaw_internal_hook_handlers__` (Map) | `registry.typedHooks` (Array) |
| **來源** | HOOK.md frontmatter → `registerInternalHook()` | Plugin 程式碼直接註冊 |
| **事件模型** | type:action 組合 (e.g. `message:sent`) | 命名 hooks (e.g. `before_model_resolve`) |
| **執行順序** | 按註冊順序 | 按 priority（高優先） |
| **錯誤處理** | catch & log，不中斷其他 handler | `catchErrors: true` 時 catch |
| **hook 數量** | 10 個事件 | 24 個 hooks |

**唯一關聯**：Workspace hooks（HOOK.md-based）載入後註冊為 internal hooks。不使用 HookRunner。

### 2. Internal Hook 完整事件清單

#### gateway 類

| action | 觸發位置 | 模式 | 說明 |
|--------|---------|------|------|
| **startup** | gateway-cli:20723 | fire-and-forget (setTimeout 250ms) | Gateway 啟動完成後 |

Context: `cfg` (完整設定), `deps` (CLI dependencies), `workspaceDir`

#### agent 類

| action | 觸發位置 | 模式 | 說明 |
|--------|---------|------|------|
| **bootstrap** | reply:13427, pi-embedded:3060 | **blocking (awaited)** | Session 初始化，bootstrap 檔案載入前 |

Context: `workspaceDir`, `bootstrapFiles` (陣列，**hook 可修改**), `cfg`, `sessionKey`, `sessionId`, `agentId`

> **重要**：`agent:bootstrap` 是唯一能修改 bootstrap 檔案列表的事件。Hook 可直接 push/splice `context.bootstrapFiles`。

#### message 類

| action | 觸發位置 | 模式 | context 關鍵欄位 |
|--------|---------|------|------------------|
| **received** | reply:22785, pi-embedded:52141 | blocking | from, content, timestamp, channelId, accountId, conversationId, messageId, metadata (provider, surface, threadId, senderId, senderName, senderUsername, senderE164, guildId, channelName) |
| **transcribed** | reply:85384, pi-embedded:49677 | fire-and-forget | from, to, body, bodyForAgent, transcript, timestamp, channelId, conversationId, messageId, senderId, senderName, senderUsername, provider, surface, mediaPath, mediaType, cfg |
| **preprocessed** | reply:85385, pi-embedded:49678 | fire-and-forget | from, to, body, bodyForAgent, transcript, timestamp, channelId, conversationId, messageId, senderId, senderName, senderUsername, provider, surface, mediaPath, mediaType, isGroup, groupId, cfg |
| **sent** | deliver:1298 (多個 deliver-*.js) | fire-and-forget | to, content, success, error (失敗時), channelId, accountId, conversationId, messageId, isGroup, groupId |

> **`message:before` 不存在**。已確認 codebase 只有 received/transcribed/preprocessed/sent。

#### command 類

| action | 觸發位置 | 模式 | context 關鍵欄位 |
|--------|---------|------|------------------|
| **stop** | reply:79530, pi-embedded:28495 | blocking | sessionEntry, sessionId, commandSource, senderId |
| **reset** | reply:80496 | **blocking** (可回傳 messages) | sessionEntry, previousSessionEntry, commandSource, senderId, cfg |
| **new** | reply:80585 | **blocking** (可回傳 messages) | (同 reset) |

> `command:reset`/`command:new` 的 hook 若 push messages 到 `event.messages`，會路由回使用者。

### 3. Hook 載入流程

**入口**: `gateway-cli-CuFEx2ht.js:20711` (`startGatewaySidecars`)

```
clearInternalHooks()  // 清除所有已註冊 handlers
↓
loadInternalHooks(cfg, workspaceDir)
  ├─ Stage 1: loadWorkspaceHookEntries() — 目錄掃描
  │   ├─ 1. extraDirs (cfg.hooks.internal.load.extraDirs)
  │   ├─ 2. bundledHooksDir (dist/bundled/) — 不可變
  │   ├─ 3. managedHooksDir (~/.openclaw/hooks/)
  │   └─ 4. workspaceHooksDir (.openclaw/workspace/hooks/) ← 最高優先
  │
  └─ Stage 2: Legacy config handlers
      └─ cfg.hooks.internal.handlers[] → { module, export?, event }
↓
setTimeout(250ms) → triggerInternalHook(gateway:startup)
```

**每個 hook 目錄結構**：
- `HOOK.md` — frontmatter 含 name, description, events
- Handler 檔案（依序嘗試）：`handler.ts` → `handler.js` → `index.ts` → `index.js`
- 可選 `package.json` with `openclaw.hooks` 陣列

**HOOK.md events 解析** (`frontmatter-BLUo-dxn.js:244-248 normalizeStringList`):
- 陣列格式：每個元素 trim
- 字串格式：以逗號分割再 trim
- **無大小寫轉換、無底線/破折號轉換** — 完全照原文使用

**Import 機制** (`buildImportUrl`):
- 轉為 `file://` URL
- bundled hooks：不加 query params（不可變）
- 其他來源：加 `?t={mtimeMs}&s={size}` 支援 hot-reload
- stat 失敗時 fallback `?t={Date.now()}`

**錯誤處理**（所有失敗都是 non-fatal）:
- 路徑逃逸檢查（realpath boundary check）→ 失敗則 log + skip
- Handler 檔案讀取失敗 → log + skip
- Handler 不是 function → log + skip
- Events 空或缺失 → warn + skip
- Import 失敗 → log + skip（靜默繼續）
- 註冊失敗 → log + skip

### 4. Bundled Hooks（4 個）

| Hook | 事件 | 功能 | 設定 |
|------|------|------|------|
| **boot-md** | `gateway:startup` | 啟動時對每個 agent scope 執行 BOOT.md | — |
| **bootstrap-extra-files** | `agent:bootstrap` | 透過 glob patterns 注入額外 bootstrap 檔案 (AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, MEMORY.md) | `entries.bootstrap-extra-files.paths` |
| **command-logger** | `command` (all) | 記錄所有指令到 `~/.openclaw/logs/commands.log` (JSONL) | — |
| **session-memory** | `command:new`, `command:reset` | 讀取最近 N 則對話，產生 LLM slug，儲存到 workspace/memory/ | `entries.session-memory.messages` (default 15), `.llmSlug` |

### 5. HookRunner 完整清單（24 個，Plugin 專用）

**Modifying Hooks**（循序執行，結果合併）:
1. `runBeforeModelResolve` — 覆寫 LLM provider/model
2. `runBeforePromptBuild` — 注入 system prompt
3. `runBeforeAgentStart` — Legacy (model resolve + prompt build)
4. `runMessageSending` — 修改/取消外送訊息
5. `runBeforeToolCall` — 修改/阻擋 tool calls
6. `runToolResultPersist` — (同步) 修改持久化的 tool results
7. `runBeforeMessageWrite` — (同步) 阻擋/修改訊息寫入 JSONL
8. `runSubagentSpawning` — 分配 subagent session bindings
9. `runSubagentDeliveryTarget` — 解析 subagent delivery routing

**Void Hooks**（平行執行，fire-and-forget）:
10-24: `runLlmInput`, `runLlmOutput`, `runAgentEnd`, `runBeforeCompaction`, `runAfterCompaction`, `runBeforeReset`, `runMessageReceived`, `runMessageSent`, `runAfterToolCall`, `runSessionStart`, `runSessionEnd`, `runSubagentSpawned`, `runSubagentEnded`, `runGatewayStart`, `runGatewayStop`

### 6. Event 結構

```typescript
interface InternalHookEvent {
  type: "command" | "session" | "agent" | "gateway" | "message"
  action: string
  sessionKey: string
  context: Record<string, unknown>  // 可由 hook 修改
  timestamp: Date
  messages: string[]  // hook 可 push 回覆訊息
}

type InternalHookHandler = (event: InternalHookEvent) => Promise<void> | void
```

**eventKey 匹配邏輯**（triggerInternalHook）:
1. 查 type-only handlers (e.g. `"message"`) → 收到該 type 所有事件
2. 查 type:action handlers (e.g. `"message:sent"`) → 只收特定事件
3. 兩者都命中時，全部呼叫

### 7. 已知限制與注意事項

- `message:before` 不存在 — 任何宣告此事件的 hook 永遠不會被觸發
- fire-and-forget hooks 的 handler 錯誤會被吞掉（只 log）
- Workspace hooks 有最高優先，可覆蓋同名 bundled/managed hook
- Handler 必須是 async function 或返回 Promise
- Bootstrap-extra-files 只接受特定 basename（AGENTS.md 等），自訂檔名會被忽略
- Hot-reload 透過 URL query params 實現，bundled hooks 不支援 hot-reload

---

## 行動段落

### 開發新 Workspace Hook 的 Checklist

1. 在 `.openclaw/workspace/hooks/<hook-name>/` 建立目錄
2. 建立 `HOOK.md`，frontmatter 必須包含 `name` 和 `events`（逗號分隔或陣列）
3. 建立 `handler.js`（或 .ts），export default async function
4. 確保 hooks 目錄有 `package.json` with `"type": "module"`（ESM）
5. 事件名稱必須完全匹配（case-sensitive，無自動轉換）
6. 可用事件：gateway:startup, agent:bootstrap, message:received/transcribed/preprocessed/sent, command:stop/reset/new
7. 要修改 bootstrap 檔案只能用 `agent:bootstrap` 事件
8. 要在 reset/new 時回傳訊息，push 到 `event.messages`
9. 重啟 Gateway 後 hook 生效（或等 hot-reload 機制偵測檔案變更）

### Debug Hook 問題

1. 檢查 Gateway stderr/stdout — 所有 hook 錯誤都會 log
2. 確認 HOOK.md events 欄位使用正確事件名（參考上方清單）
3. 確認 handler export 是 function（`typeof handler === 'function'`）
4. 確認無路徑逃逸（handler 必須在 workspace 目錄內）
5. 確認 ESM 相容（`"type": "module"` in package.json）

---

## 關鍵檔案路徑

| 檔案 | 用途 |
|------|------|
| `dist/internal-hooks-Y1c3CR6c.js` | 核心 registry (registerInternalHook, triggerInternalHook) |
| `dist/registry-ds-_TqV5.js` | Plugin hook 整合 |
| `dist/gateway-cli-CuFEx2ht.js:20411` | loadInternalHooks — 載入 + import |
| `dist/workspace-Dn54fYWU.js:284` | loadWorkspaceHookEntries — HOOK.md 掃描 |
| `dist/frontmatter-BLUo-dxn.js:244` | normalizeStringList — events 解析 |
| `dist/reply-DhtejUNZ.js` | 大部分事件觸發點 |
| `dist/deliver-DPAduhp1.js:27` | createHookRunner — 24 個 plugin hooks |
| `dist/bundled/` | 4 個 bundled hooks |

---

## 演化日誌

| 日期 | 事件 |
|------|------|
| 2026-03-06 | 初建：從 Gateway dist v2026.3.2 逆向分析，確認 10 個 internal hook 事件、24 個 HookRunner hooks、4 個 bundled hooks、完整載入流程 |
