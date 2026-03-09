# Atom: memory-writer hook 調查完整記錄

- Scope: project
- Confidence: [固]
- Source: 2026-03-05~06 — 多 session 深度調查
- Last-used: 2026-03-06 (RESOLVED — hook 正常運作)
- Confirmations: 4
- Trigger: memory-writer, hook 不觸發, message:before, message:sent, message:preprocessed, staging
- Privacy: public

## 問題

memory-writer hook handler 從未被 Gateway 呼叫過。canary 寫檔測試確認 handler function 完全沒有執行。

## 已確認的事實

### Gateway Internal Hook 系統架構

- **registry**: `globalThis.__openclaw_internal_hook_handlers__` (Map)
- **註冊**: `registerInternalHook(eventKey, handler)` → Map.set(eventKey, [...handlers])
- **觸發**: `triggerInternalHook(event)` → 查 `Map.get(event.type)` + `Map.get(event.type:event.action)`
- **eventKey 是精確匹配**：`message:before` 只匹配 action="before"，不匹配 action="preprocessed"

### Gateway v2026.3.2 實際存在的 message 事件

| 事件 | 位置 | 觸發時機 |
|------|------|---------|
| `message:received` | reply-*.js, pi-embedded-*.js, subagent-registry line 45014 | 訊息進入 ingress |
| `message:transcribed` | 同上 line 42550 | 語音轉文字後 |
| `message:preprocessed` | 同上 line 42551 | preprocessor 完成後、agent 開始前 |
| `message:sent` | deliver-*.js line 1298 | deliverOutboundPayloads 送出後（auto-reply 不走此路徑） |

**`message:before` 不存在於任何 Gateway 程式碼中。**

### hook 載入流程

1. `loadInternalHooks()` (gateway-cli line 20411)
2. `loadWorkspaceHookEntries()` → 掃描 bundled/managed/workspace hooks 目錄
3. 讀 HOOK.md frontmatter → `resolveOpenClawMetadata()` → 提取 events
4. merge: extraDirs → bundled → managed → workspace（後者優先）
5. `shouldIncludeHook()` 檢查 requires/enabled
6. `import(buildImportUrl(handlerPath))` 載入 handler
7. `registerInternalHook(event, handler)` 註冊到 Map

### 已排除的問題

| 排除項 | 驗證方法 |
|--------|---------|
| HOOK.md 解析錯誤 | test-fm.mjs 確認 events=["message:before"] 正確解析 |
| handler.ts 無法 import | 加 `hooks/package.json` type:module 後 import 成功（typeof default = function） |
| shouldIncludeHook 排除 | test-hook-load.mjs 確認 included:true |
| 事件不存在 | `message:before` 確認不存在於 Gateway codebase |
| sessionKey 位置 | `message:preprocessed` context 無 sessionKey，改讀 event.sessionKey |
| handler 有 bug | canary 寫檔測試確認 handler function 從未被呼叫 |

### 未解之謎

1. **之前的 staging entries**（`2026-03-05-09c1b355.md` 和 `2026-03-05-cdd88123.md`）如何產生？
   - 內容標記 "auto-captured by memory-writer" 符合 handler 模板
   - sessionKey 是 `agent:main:direct:holylight`（LINE session）
   - 時間點與 gateway-chat.js 測試重疊，但 session key 不匹配
   - **可能解釋**：Gateway 在某個罕見路徑觸發了事件，或者 preprocessor 有自己的 staging 機制

2. **`message:preprocessed` 註冊後仍不觸發**
   - HOOK.md 改為 `events: ["message:preprocessed"]`，handler 移除 action filter
   - 加 canary 無條件寫檔，Gateway 重啟後測試 → canary 為空
   - 可能原因：handler import 在 Gateway 的 ESM context 中仍然失敗（即使獨立 import 測試成功）

### handler 的 import context 差異

- **獨立測試**：`node --input-type=module -e "import('file:///...')"` → 成功
- **Gateway context**：`openclaw.mjs` 是 ESM，但 import 路徑經過 `buildImportUrl()` 加了 cache-busting query
- Gateway 可能用不同的 Node flags 或 module resolution
- Gateway 用 `import(buildImportUrl(path, source))` 而 error 被 `catch (err) { log.error(...) }` 吞掉

### 關鍵 Gateway 原始碼路徑

| 檔案 | 用途 |
|------|------|
| `deliver-DPAduhp1.js` | HookRunner + deliverOutboundPayloads + message:sent |
| `subagent-registry-CkqrXKq4.js` | auto-reply pipeline + message:preprocessed/received/transcribed |
| `gateway-cli-CuFEx2ht.js` | hook loader (loadInternalHooks, line 20411) |
| `workspace-Dn54fYWU.js` | workspace hook discovery + HOOK.md parsing |
| `workspace-DRKABzFd.js` | 另一版 workspace（loadHookFromDir） |
| `registry-ds-_TqV5.js` | internal hook registry (registerInternalHook/triggerInternalHook) |
| `frontmatter-BLUo-dxn.js` | frontmatter parser + resolveOpenClawManifestBlock |

### 目錄結構

```
~/.openclaw/hooks/                  # managed hooks（Gateway 載入）
  memory-writer/
    HOOK.md                         # events: ["message:preprocessed"]
    handler.ts                      # V4 handler
  memory-retriever/
    HOOK.md                         # events: ["message:preprocessed"]（已修復 2026-03-06）
    handler.ts
  atom-context-injector/
    HOOK.md                         # events: ["agent:bootstrap"]
    handler.ts

E:\OpenClawWorkSpace\.openclaw\workspace\hooks\  # workspace hooks（優先級最高）
  package.json                      # {"type":"module"} ← 修復 CJS 問題
  memory-writer/                    # 與 managed 同步
  memory-retriever/
  atom-context-injector/

E:\OpenClawWorkSpace\.openclaw\workspace\
  package.json                      # {"type":"commonjs"} ← 根因之一
  staging/                          # staging entries 目錄
  preprocessor/                     # 18 算法模組
```

### 完整事件清單交叉引用

> 完整的 Internal Hook 系統逆向分析見 `memory/gateway-internal-hooks.md`。
> 該 atom 包含：10 個 internal hook 事件、24 個 HookRunner hooks、4 個 bundled hooks、載入流程、事件結構。

### 已解決（2026-03-06）

**根因**：HOOK.md 從 `message:before`（不存在的事件）改為 `message:preprocessed` 後，**Gateway 沒有重啟**。
重啟後 hook 立即正常運作。verbose 輸出確認：`Registered hook: memory-writer -> message:preprocessed`。

**完整驗證結果**：
- canary 寫入成功 → handler 被呼叫 ✓
- transcript reading 正確讀取上一輪 assistant response ✓
- memory signal "記住了" 被偵測 → staging entry 寫入 ✓
- handler 升級為 V5（清理 canary/debug，更新文件）

**附帶修復**：
- managed hooks 目錄加 `package.json` with `"type": "module"`
- openclaw.json `extraDirs` 修正為父目錄
- memory-retriever 已修復：`message:before` → `message:preprocessed`（2026-03-06）
- AGENTS.md 新增 `_profile.md` 寫入指引，讓 agent 知道個人事實要寫到共享位置

## 行動

- 修改 hook 後**必須重啟 Gateway** 才生效（hot-reload 靠 URL query params，但首次載入不會重試）
- 用 `openclaw gateway --verbose` 可看到所有 hook 載入結果
- 跨頻道記憶：個人事實要寫到 `_profile.md`（atom-context-injector 每次 bootstrap 都會載入），不能只寫 `memory/YYYY-MM-DD.md`（session-local）
