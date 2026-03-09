# Atom: OpenClaw 工程決策

- Scope: global
- Confidence: [固]
- Source: 2026-02-26 holylight — OpenClaw 初始安裝至 Bridge 整合全過程
- Last-used: 2026-03-05
- Trigger: 修改 OpenClaw 配置、安裝升級、安全策略討論、平台整合問題、ngrok 啟動、Discord 設定、LINE 設定、sandbox、Gateway auth
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
- kill switch 機制：`停下來` (stop) / `你繼續` (resume) — Discord 內有效
- OpenClaw 正確拒絕「最高優先級覆蓋」特權升級嘗試

### 安裝方式
- `npm install -g openclaw@latest`（非原始碼建置，Windows pnpm build 會失敗）

### Discord
- groupPolicy: "open"（guild 回應所有訊息）、dmPolicy: "open"
- streaming: "off" + blockStreaming: **false**（完成後直接送出，不走 streaming pipeline）
- **禁止** blockStreaming: true + streaming: "off" 組合（= deadlock，訊息永不送出）
- dm: { enabled: true, policy: "allowlist", allowFrom: ["*"], groupEnabled: true, groupChannels: ["*"] }
- allowBots: true、allowFrom: ["*"]
- configWrites: true（允許 agent 透過 /config set 自行修改 Discord 設定）
- replyToMode: "all"（回覆所有訊息使用 reply threading）

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

### Gateway Session 提取（Phase 4）
- 從 7 個 Gateway session JSON 提取人事時地物，寫入 `.openclaw/workspace/atoms/`
- persons 分 owner/user 兩層：holylight 為 owner（含 context/interests/personality/principles/relationships 子目錄），luway/wellstseng/wendy 為 user（僅 `_profile.md`）
- events 獨立 atom：tesla-delivery、multi-ai-consensus、atomic-memory-v211-discussion、discord-output-policy
- `_registry.md` 作為 persons 映射索引
- session-profiles/ 保留原始 JSON（7 個）供未來回溯
- CC atoms（本檔 + pitfalls）同步記錄提取過程中的決策與坑點

### Gateway
- Scheduled Task 服務，`openclaw gateway install/start/stop`

### GitHub Repo
- `holylight1979/OpenClaw-AtomicMemory`（Public）
- Secrets 用 `{{PLACEHOLDER}}`，openclaw.json 需 merge 升級

### Discord 行為規則
- 長內容輸出：摘要 + 檔案附件（不分割訊息洗版）
- 行為規則文件化至 AGENTS.md + discord-global-policy.md
- dialog-level 行為可調，system-level 行為需修改系統設定

### 跨平台協作
- LINE → OpenClaw → Claude Code inject/observe 模式已建立
- OpenClaw 可透過 inbox.jsonl 向 Claude Code 發送任務
- 無法從 LINE 端直接確認 Claude Code 執行狀態

### Gateway 記憶寫入（Phase 2, 2026-03-05）
- 方案選擇：混合式 C — hook 自動萃取 + skill 指導手動寫入
- memory-writer hook (message:sent)：確定性模式匹配，零 LLM 呼叫，零延遲
- SKILL.md Memory Write Protocol：教 agent 用 fs_write 寫入 atoms/staging
- staging → A7 staging-evaluator：occ≥3 自動晉升，>14d 未晉升自動刪除
- agent 有 fs_write 工具（tools.profile: "full" + fs.workspaceOnly: true）
- 之前寫入失敗原因：缺機制（非權限問題）

### Phase 3: 整合與已知限制（2026-03-05）
- `message:sent` 事件在 v2026.3.2 不會對 Discord channel agent 回應觸發 — 平台限制
- 替代方案：SKILL.md 廢棄 `memory/YYYY-MM-DD.md` 路徑 + memory-bridge.js preprocessor 掃描轉換
- memory-bridge.js 掃描 `memory/` 和 `.openclaw/workspace/memory/` 舊日誌，轉為 staging entries（首次執行：402 掃描 → 295 建立）
- Agent 仍會透過 edit tool 寫入 `memory/YYYY-MM-DD.md`（GPT 模型不一定遵循 SKILL.md），bridge 定期轉換作為補償
- 三個 memory 目錄：`memory/`（agent 日誌）、`.openclaw/memory/`（內部 DB）、`.openclaw/workspace/memory/`（舊條目）
- hook 安裝方式：`openclaw hooks install`（非 openclaw.json entries，那只控制 bundled hooks）
- atom-context-injector + memory-retriever 於 2026-03-05 首次安裝（之前只有原始碼，從未生效）
- Gateway 重啟後確認 7/7 hooks ready（含 atom-context-injector、memory-retriever、memory-writer）
- 注入驗證已確認成功（2026-03-05 21:25）：agent 正確引用 identity-map 真名「煜閎」+ discord-output-policy 規則
- 根因：`ctx.workspaceDir` 回傳專案根 `E:\OpenClawWorkSpace`，非 `.openclaw/workspace/`。修正為 `path.join(workspaceDir, ".openclaw", "workspace")`
- `.openclaw/workspace/` 是獨立 git repo（有自己的 .git/），父 repo 無法追蹤其檔案
- 跨頻道記憶限制：session 級指令（如「記住不喜歡繁體中文」）不跨頻道，需寫入 atom 才能跨頻道共享

### Hook 架構理解（2026-03-05）
- openclaw.json 的 `hooks` section 只控制 **bundled** hooks（openclaw-bundled 類型）
- 自訂 hooks 必須用 `openclaw hooks install <path>` 安裝到 `~/.openclaw/hooks/`
- `openclaw hooks list` 顯示所有已安裝 hooks 及狀態
- hook events: `gateway:startup`, `agent:bootstrap`, `command:new/reset`, `message:before/sent`, `agent_end`
- atom-context-injector (agent:bootstrap): 注入 identity map + person profile + global atoms 到 USER.md
- memory-retriever (message:before): 雙通道檢索 (A4 trigger + vector search) + fusion ranking，注入匹配 atoms
- memory-writer (agent_end + message:sent fallback): 確定性模式匹配萃取

### Phase 6: 跨頻道記憶寫入修復（2026-03-05）
- 根因 1: AGENTS.md line 91 指向 `memory/YYYY-MM-DD.md`，與 SKILL.md 矛盾 → agent 寫到錯誤位置
- 根因 2: memory-writer hook 監聽 `message:sent`（v2026.3.2 不觸發）→ 安全網失效
- 修復: AGENTS.md 改指向 `atoms/` + `staging/`，新增跨頻道寫入區塊含 fs_write 範例
- 修復: memory-writer 改用 `agent_end` 事件（保留 `message:sent` fallback）
- Extension API 只有 `api.registerTool()`，不支援 `api.registerHook()`（hook 必須在 workspace/hooks/ 實作）
- `preferences/` facet 未標準化，偏好寫入 `principles/`（AI 應遵循的規則）或 `interests/`

### vector-indexer Hybrid Search（2026-03-06）
- A16 search() 加入 keyword boost：extractQueryKeywords() 提取中英文關鍵詞，向量結果同時命中時 +0.1
- A16 search() 加入 self-healing：query 失敗 → resetConnection + retry，連續失敗計數器 ≥3 升級 error
- 參考來源：OpenClaw 社群 chromadb-memory skill 的 hybrid search 設計

## 行動

- 修改 OpenClaw 配置時：先讀本 atom 確認已有決策，避免重複踩坑
- 安全相關變更：必須遵循 config deny 原則，不依賴 prompt 級指令
- 升級 OpenClaw：用 `npm install -g openclaw@latest`，openclaw.json 用 merge 不要覆蓋
- 新增 plugin：必須加入 `plugins.allow` 明確列出
