# Atom: OpenClaw 安裝與啟動指南

- Scope: global
- Confidence: [固]
- Source: 2026-03-05 V2.3 升級全面掃描
- Last-used: 2026-03-05
- Trigger: 安裝 OpenClaw, 啟動 Gateway, 啟動服務, 環境設定, 首次設定, 重新部署, 服務啟停, start-gateway, OpenClawPanel
- Privacy: public

## 知識

### 前置需求

| 項目 | 版本/設定 | 備註 |
|------|----------|------|
| Node.js | v24+ | Gateway 執行環境 |
| .NET 9 | SDK + Runtime | OpenClawPanel + OpenClawDesktop |
| Ollama | 安裝路徑: `/c/Users/holyl/AppData/Local/Programs/Ollama/ollama.exe`（不在 bash PATH） | 本地 LLM |
| qwen3 models | `ollama pull qwen3:1.7b && ollama pull qwen3-embedding:0.6b && ollama pull qwen3:0.6b` | 三個模型 |
| ngrok | WinGet 安裝: `winget install ngrok.ngrok` + authtoken | LINE webhook |
| OpenClaw | `npm install -g openclaw@2026.3.2`（非原始碼建置） | 全域安裝 |

### 環境變數

| 變數 | 值 | 重要性 |
|------|-----|--------|
| `OPENCLAW_CONFIG_PATH` | `E:\OpenClawWorkSpace\.openclaw\openclaw.json` | **必要** — 不設則讀 user-level 精簡版，channels 不載入 |

### 啟動順序（SOP）

1. **Ollama**: 開機自動啟動（系統服務），確認 `curl http://127.0.0.1:11434`
2. **Gateway**: 執行 `E:\OpenClawWorkSpace\.openclaw\start-gateway.bat`（已含 OPENCLAW_CONFIG_PATH）
   - 冷啟動需 7~11 秒，health check 15s polling
3. **ngrok**: `ngrok http 18789 --traffic-policy-file=".openclaw/ngrok-policy.yml"`
   - 免費方案 URL 不固定，重啟需更新 LINE Console webhook URL
   - traffic-policy 自動注入 Bearer token（Gateway 強制 auth）
4. **Bridge**: port 3847（可選，Claude Code↔OpenClaw 通訊用）

**快捷啟動**: OpenClawPanel（.NET 9 WinForms），一鍵啟停 Gateway/Bridge/ngrok

### 關鍵設定檔

| 檔案 | 位置 | 用途 |
|------|------|------|
| openclaw.json | `.openclaw/openclaw.json` | 完整設定（Gateway + channels + agents） |
| user-level config | `~/.openclaw/openclaw.json` | 精簡設定（commands + gateway.mode/port/auth） |
| auth-profiles.json | `~/.openclaw/agents/main/agent/auth-profiles.json` | OpenAI Codex OAuth token（**必須存在**） |
| ngrok-policy.yml | `.openclaw/ngrok-policy.yml` | LINE webhook auth 注入 |
| start-gateway.bat | `.openclaw/start-gateway.bat` | 啟動腳本（含 env var） |

### 雙 config 合併規則

- Workspace config（完整版）+ User-level config（精簡版）= merge
- **禁止**在 user-level 放 `channels.discord`（merge 干擾→deadlock）
- 新增/修改 channels、plugins、agents → 只改 workspace config

### auth-profiles.json

- 路徑: `~/.openclaw/agents/main/agent/auth-profiles.json`
- 內容: OpenAI Codex OAuth token
- Gateway 啟動時載入，修改後**必須重啟 Gateway**
- 備份: `E:\OpenClawWorkSpace - 複製`（災難復原用）

### Port 對照

| Port | 服務 | 用途 |
|------|------|------|
| 18789 | Gateway | WebSocket + webhook + REST API |
| 18791 | Browser control | CDP-based 瀏覽器控制 |
| 18792 | CDP port | Gateway 內部，每次啟動都開 |
| 3847 | Bridge | Claude Code↔OpenClaw 中繼 |
| 11434 | Ollama | 本地 LLM API |
| 3848 | V2.3 Dashboard | Workflow Guardian 監控 |
| 3849 | V2.3 Vector Service | ChromaDB 向量搜尋 |

## 行動

- 首次部署：依啟動順序 SOP 逐步執行
- Gateway 啟動失敗：檢查 OPENCLAW_CONFIG_PATH → auth-profiles.json → port 衝突
- LINE webhook 不通：確認 ngrok URL 已更新 + traffic-policy 注入正確
- channels 不載入：確認 OPENCLAW_CONFIG_PATH 指向完整版 config
