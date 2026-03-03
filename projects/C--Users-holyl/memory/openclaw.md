# OpenClaw 操作知識

> Scope: 全域（holyl 主機）
> Confidence: [固] 已實測驗證
> Source: 2026-02-28 實作 cron job session
> Last-used: 2026-02-28
> Trigger: 提到 OpenClaw / cron / LINE 推送 / 排程 / 天氣穿搭
> Privacy: 不含 token，僅結構性知識

---

## 安裝與版本

- `openclaw` via npm global, version 2026.2.26
- 指令路徑: `C:\Users\holyl\AppData\Roaming\npm\openclaw`
- 設定檔: `E:\OpenClawWorkSpace\.openclaw\openclaw.json`（含敏感 token，讀取時注意不外洩）

## Gateway

- Local loopback: `ws://127.0.0.1:18789`
- Auth mode: token
- Gateway service: Scheduled Task installed（Windows 排程任務）
- Node service: 未安裝

## Channels

| Channel | 狀態 | 備註 |
|---------|------|------|
| LINE    | enabled, ok | plugin: `line`, name: `光仔AI-LINE`, dmPolicy: pairing, groupPolicy: allowlist |
| Discord | enabled, ok | plugin: `discord` + `discord-reader`, bot: `@光AI.Jr` |

### Identity Links
- `holylight` 綁定: `discord:831783571513278464` + `line:U556bc083405a12bb3a9d2dbb66983386`

### Session Keys 格式
- Direct DM (跨 channel): `agent:main:direct:holylight`
- LINE 群組: `agent:main:line:group:group:<groupId>`
- Discord 頻道: `agent:main:discord:channel:<channelId>`

## Cron 排程

### 常用指令
```bash
# 列出所有 jobs
openclaw cron list

# 新增 job
openclaw cron add --name "<name>" --cron "<5-field expr>" --tz "Asia/Taipei" --exact \
  --message "<prompt>" --announce --channel line --to "<userId>" \
  --session-key "<sessionKey>" --timeout-seconds 120

# 手動執行（測試用）
openclaw cron run "<jobId>" --expect-final --timeout 180000

# 執行紀錄
openclaw cron runs --id "<jobId>"

# 狀態
openclaw cron status

# 停用 / 啟用 / 刪除
openclaw cron disable "<jobId>"
openclaw cron enable "<jobId>"
openclaw cron rm "<jobId>"

# 修改欄位
openclaw cron edit "<jobId>" --message "<new prompt>"
```

### 現有 Cron Jobs
| Name | ID | Schedule | Target | 用途 |
|------|----|----------|--------|------|
| morning-weather-outfit | `3306c000-1d0d-4908-8569-1aa6b78c8055` | `30 6 * * *` Asia/Taipei | LINE → holylight | 每日天氣穿搭建議（土城/中和） |

### Cron 設計筆記
- `--announce` = agent 處理完後將 summary 推送到 `--channel` + `--to` 指定的 chat
- `--exact` = 禁用 stagger，準時觸發
- `--session-key` 控制 agent session routing（可用 direct session 或 isolated）
- `--timeout-seconds` 建議 ≥ 120，agent 需要搜尋天氣資料
- job store 位置: `E:\OpenClawWorkSpace\.openclaw\cron\jobs.json`
- 實測 agent 處理約 31 秒，delivery 成功

## Message 發送

```bash
# 發送訊息到 LINE
openclaw message send --channel line --target "<userId 或 groupId>" --message "內容"

# 發送到 Discord
openclaw message send --channel discord --target "<channelId>" --message "內容"
```

## 其他常用指令

```bash
# 健康檢查
openclaw health
openclaw status          # 完整狀態（含 channels, sessions）
openclaw status --deep   # 加上 probe

# Sessions
openclaw sessions --store "E:/OpenClawWorkSpace/.openclaw/agents/main/sessions/sessions.json"
openclaw sessions --json  # JSON 格式

# Channels
openclaw channels status --probe

# Doctor（診斷修復）
openclaw doctor
```

## 注意事項
- `openclaw.json` 的 `tools.deny` 包含 `cron`（限制 agent 不能自己操作 cron，但 CLI 不受影響）
- `directory self --channel line` 目前會報 "Unknown channel: line"，但 LINE 實際上是透過 plugin 連線而非原生 channel，不影響功能
- Sessions store 路徑在 workspace (`E:\OpenClawWorkSpace\`) 下，非預設 `~/.openclaw/`，查詢時需用 `--store` 指定
