# Atom: OpenClaw Config Intelligence — 設定參數語義圖

- Scope: global
- Confidence: [固]
- Source: 2026-02-28 holylight — 逆向 openclaw dist source + 實際除錯驗證
- Last-used: 2026-02-28
- Trigger: 修改 openclaw.json 設定、新增 channel/group、除錯設定不生效、理解參數關係
- Privacy: public

## 核心概念：OpenClaw 設定的 3 層模型

OpenClaw 設定不是扁平的 key-value，而是**三層依賴鏈**。缺任一層 → 靜默失敗。

```
Channel Policy（開關）→ Entity Config（誰）→ Sender Auth（誰裡的誰）
```

## Channel 通用欄位語義

每個 channel（discord/line/telegram/whatsapp）共用同一套語義框架：

| 欄位 | 語義 | 預設值 | 靜默失敗風險 |
|------|------|--------|-------------|
| `enabled` | channel 總開關 | false | 無 log，webhook 直接 404 |
| `dmPolicy` | DM 處理模式 | — | `"pairing"` 需配對，`"open"` 直接允許，`"allowlist"` 需 `allowFrom` |
| `groupPolicy` | 群組處理模式 | `"allowlist"` | **fail-closed**：未設定 = 禁止所有群組 |
| `allowFrom` | DM 允許的 sender ID 清單 | `[]` | 也是 groupAllowFrom 的 fallback |
| `groupAllowFrom` | 群組內允許的 sender 清單 | 回退到 `allowFrom` | 無 entries 且無 fallback → 靜默丟棄 |
| `groups` / `guilds` | 個別群組/guild 設定 | `{}` | allowlist 模式下，群組不在此 = 不處理 |

## LINE 群組訊息的完整依賴鏈

```
webhook 到達 → 簽名驗證 → shouldProcessLineEvent()
  ├─ DM (source.type=user): dmPolicy 檢查 → allowFrom 檢查 → 處理
  └─ 群組 (source.type=group):
      ├─ groupPolicy 檢查（"disabled" → 丟棄）
      ├─ groupPolicy="allowlist" 時：
      │   ├─ 群組 ID 在 groups 裡？（不在 → 丟棄）
      │   ├─ effectiveGroupAllow 有 entries？
      │   │   ├─ 優先：groups.{id}.allowFrom（群組級）
      │   │   ├─ 其次：channel.groupAllowFrom（channel 級）
      │   │   ├─ 回退：channel.allowFrom（DM 清單）
      │   │   └─ 全空 → **靜默丟棄**（"no groupAllowFrom"）
      │   └─ sender 在 allowFrom 裡？（不在 → 丟棄）
      └─ groupPolicy="open"：直接允許所有群組
```

**關鍵**：所有丟棄都用 `logVerbose()`，預設不顯示。看不到任何錯誤 log。

## Discord vs LINE 設定對比

```json
// Discord — guilds 裡有 users 陣列（同時充當 group allowFrom）
"discord": {
  "groupPolicy": "allowlist",
  "guilds": {
    "GUILD_ID": { "requireMention": true, "users": ["USER_ID"] }
  }
}

// LINE — groups 裡需要 allowFrom（不是 users！）
"line": {
  "groupPolicy": "allowlist",
  "groups": {
    "GROUP_ID": { "requireMention": false, "allowFrom": ["*"] }
  }
}
```

注意：Discord 用 `users`，LINE 用 `allowFrom`。欄位名不同但語義相似。

## Config 合併規則

兩份 config 的 merge 行為：
- `~/.openclaw/openclaw.json`（user-level）— 放 gateway/commands/meta 等全域設定
- `OPENCLAW_HOME/.openclaw/openclaw.json`（workspace）— 放 channels/plugins/agents 等 workspace-specific 設定
- 合併時 workspace 優先，但 user-level 的 plugins.allow 若列出 workspace-only plugin → "Config invalid"

**安全原則**：user-level config 保持最小。不要複製 workspace 的 channels/plugins 設定到 user-level。

## Gateway 內部路由機制

```
webhook HTTP handler
  → 簽名驗證（失敗 → 401）
  → 200 OK 立即返回（LINE 要求）
  → shouldProcessLineEvent()（靜默過濾）
  → buildLineMessageContext()
  → lane enqueue（session routing）
  → embedded agent run（LLM 呼叫）
```

注意：HTTP 200 OK 是在過濾**之前**返回的。所以即使訊息被丟棄，LINE 也不會 retry。

## 除錯口訣

1. **200 OK 但無 log** → 查 shouldProcess 過濾鏈（groupPolicy + allowFrom）
2. **401 Unauthorized** → 簽名/token 問題
3. **log 有 "embedded run start" 但 isError=true** → LLM 呼叫失敗
4. **"Config invalid"** → enum 值錯誤或引用了不存在的 plugin
5. **Gateway 啟動失敗 exit 7** → 已有實例佔用 port，`openclaw gateway stop` 或 taskkill

## 行動

- 新增 channel group 時：確認三層設定齊全（policy + entity + sender auth）
- 200 OK 但靜默丟棄：開 verbose logging 或直接查 source code 的 shouldProcess 函式
- 修改 config 後：必須重啟 gateway（config 不是 hot-reload）
- 除錯時：先用 curl 手動發 webhook 分離問題（簽名 vs 路由 vs LLM）
