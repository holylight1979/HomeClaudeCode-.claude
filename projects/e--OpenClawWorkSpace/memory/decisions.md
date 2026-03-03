# Atom: OpenClaw 工程決策

- Scope: global
- Confidence: [固]
- Source: 2026-02-26 holylight — OpenClaw 初始安裝至 Bridge 整合全過程
- Last-used: 2026-02-28
- Trigger: 修改 OpenClaw 配置、安裝升級、安全策略討論、平台整合問題
- Privacy: public

## 知識

### 記憶架構
- MEMORY.md 只放索引+高頻事實（~30 行），分類檔按需讀取
- CHANGELOG 滾動淘汰：保留最近 ~8 筆，舊條目移至 `_CHANGELOG_ARCHIVE.md`
- 原則：**常態載入最小化，細節按需深入**

### LLM 後端
- OpenAI Codex OAuth (gpt-5.3-codex)，走 ChatGPT 訂閱
- Anthropic API 按量付費（無餘額）、禁止第三方 OAuth（違反 TOS）

### 安全策略
- config deny > prompt（compaction 會丟 prompt 級指令）
- 2026-02-27 轉為全面放權：`exec.security: "full"` + `exec.ask: "off"` + `fs.workspaceOnly: false` + `elevated.enabled: true`
- 版本 >= 2026.1.29（CVE-2026-25253, CVSS 8.8）

### 安裝方式
- `npm install -g openclaw@latest`（非原始碼建置，Windows pnpm build 會失敗）

### Discord
- allowlist + requireMention、groupPolicy: allowlist、dmPolicy: pairing

### LINE
- ngrok 免費方案，URL 不固定，webhook 路徑：`/line/webhook`（不是 `/channels/line/webhook`）
- status WARN "token not configured" 是顯示 bug
- **群組需三層設定齊全**：`groupPolicy: "allowlist"` + `groups.{id}` + `allowFrom`（缺一靜默丟棄）
- 群組 `allowFrom: ["*"]` 允許所有人；也可填 LINE userId 陣列限制
- DM 用 `dmPolicy: "pairing"`，群組用 `groupPolicy: "allowlist"`

### Config 雙檔合併
- Workspace: `OPENCLAW_HOME/.openclaw/openclaw.json`（完整設定）
- User-level: `~/.openclaw/openclaw.json`（最小設定：commands + gateway.mode/port/auth + meta）
- 兩份 merge，user-level 不該放 channels/plugins/agents 等 workspace-specific 設定

### Sandbox
- off（無 Docker），用 config 級 tools.deny 補償

### Session
- per-peer + identityLinks（Discord/LINE 共用 session）
- `tools.sessions.visibility: "agent"`

### Gateway
- Scheduled Task 服務，`openclaw gateway install/start/stop`

### GitHub Repo
- `holylight1979/OpenClaw-AtomicMemory`（Public）
- Secrets 用 `{{PLACEHOLDER}}`，openclaw.json 需 merge 升級

## 行動

- 修改 OpenClaw 配置時：先讀本 atom 確認已有決策，避免重複踩坑
- 安全相關變更：必須遵循 config deny 原則，不依賴 prompt 級指令
- 升級 OpenClaw：用 `npm install -g openclaw@latest`，openclaw.json 用 merge 不要覆蓋
- 新增 plugin：必須加入 `plugins.allow` 明確列出
