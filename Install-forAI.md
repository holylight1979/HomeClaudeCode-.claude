# Install-forAI — Claude Code 自訂擴充快速安裝指南

> **讀者：另一台電腦上的 Claude Code AI 助手**
> 此文件設計為 AI 可讀格式。請逐步執行以下操作，將本 repo 的自訂擴充合併到目標機器的 `~/.claude/` 中。

---

## 前置條件

- Claude Code 已安裝且可正常運作
- Python 3.8+（hooks 需要）
- Node.js 18+（MCP server 需要）
- `~/.claude/` 目錄已存在（Claude Code 首次啟動會自動建立）

---

## 安裝步驟

### Step 1: 複製自訂檔案

將以下檔案/目錄從 repo 複製到 `~/.claude/`：

```
hooks/workflow-guardian.py       → ~/.claude/hooks/workflow-guardian.py
tools/workflow-guardian-mcp/     → ~/.claude/tools/workflow-guardian-mcp/
workflow/config.json             → ~/.claude/workflow/config.json
commands/init-project.md         → ~/.claude/commands/init-project.md
memory/SPEC_Atomic_Memory_System.md → ~/.claude/memory/SPEC_Atomic_Memory_System.md
_AIDocs/                         → ~/.claude/_AIDocs/  (可選，僅作參考)
```

**不要覆蓋**：
- `memory/MEMORY.md` — 每台機器有自己的記憶索引
- `memory/decisions.md` — 包含機器特有的決策記錄
- `memory/preferences.md` — 可參考但應由使用者確認

### Step 2: 合併 CLAUDE.md

讀取 repo 中的 `CLAUDE.md`，**合併**（非覆蓋）到目標機器的 `~/.claude/CLAUDE.md`：

- 第一～四區塊（_AIDocs 知識庫、原子記憶、工作結束同步、對話管理）→ 直接採用
- 第五區塊（外部服務存取）→ **需自訂**：
  - `{{REDMINE_HOST}}` → 替換為實際 Redmine 主機位址（或刪除整段若不使用）
  - `$REDMINE_API_KEY` → 確保目標機器 `~/.bashrc` 有設定此環境變數
- 第六區塊（使用者偏好）→ 應由使用者確認是否適用

### Step 3: 合併 settings.json — hooks 區段

讀取目標機器的 `~/.claude/settings.json`，在 JSON 中新增或合併 `hooks` 欄位：

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 3 }] }],
    "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 3 }] }],
    "PreCompact": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5, "async": true }] }]
  }
}
```

**注意**：若目標機器已有 `hooks`，需手動合併而非覆蓋。

### Step 4: 合併 MCP server 註冊

在 `~/.claude.json`（注意：在 HOME 目錄，不在 `~/.claude/` 裡）的 `mcpServers` 中新增：

```json
{
  "workflow-guardian": {
    "type": "stdio",
    "command": "node",
    "args": ["{{HOME_PATH}}/.claude/tools/workflow-guardian-mcp/server.js"],
    "env": {}
  }
}
```

`{{HOME_PATH}}` 替換為目標機器的 HOME 絕對路徑（Windows: `C:\\Users\\USERNAME`，macOS/Linux: `/home/USERNAME`）。

### Step 5: 合併 settings.json — permissions 區段（可選）

以下權限與 Workflow Guardian 無直接關係，屬於使用者個人偏好。目標使用者可參考後自行決定：

```json
{
  "permissions": {
    "allow": [
      "Bash(svn status:*)", "Bash(svn diff:*)", "Bash(svn log:*)",
      "Bash(svn info:*)", "Bash(svn revert:*)",
      "Bash(git config:*)", "Bash(git commit:*)", "Bash(git push)",
      "Bash(git add:*)", "Bash(git init)", "Bash(git remote add:*)",
      "Bash(dotnet build:*)"
    ]
  }
}
```

### Step 6: 初始化記憶索引

若目標機器的 `~/.claude/memory/MEMORY.md` 尚未存在，建立最小版本：

```markdown
# Atom Index — Global

> 每個 session 啟動時，先讀此索引。
> 比對使用者訊息的 Trigger 欄，命中 → Read 對應 atom 檔。

| Atom | Path | Trigger |
|------|------|---------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, guardian, hooks |

---

## 高頻事實

- 使用者: {{USERNAME}} | 回應語言: 繁體中文
- [固] Workflow Guardian: hooks 驅動工作流監督 + Dashboard @ localhost:3848
```

### Step 7: 驗證

重啟 Claude Code（VS Code: `Ctrl+Shift+P` → `Reload Window`），然後：

1. 開啟 `http://127.0.0.1:3848` — 應看到 Dashboard
2. 編輯任意檔案 → Dashboard 應出現新 session 卡片
3. 嘗試結束對話 → Guardian 應阻止並提醒同步

---

## Placeholder 清單

安裝時需替換的佔位符：

| Placeholder | 說明 | 範例 |
|-------------|------|------|
| `{{REDMINE_HOST}}` | Redmine 主機位址 | `redmine.company.com` |
| `{{HOME_PATH}}` | 使用者 HOME 絕對路徑 | `C:\\Users\\john` 或 `/home/john` |
| `{{USERNAME}}` | 使用者名稱 | `john` |

---

## 系統概述（供 AI 理解上下文）

本擴充包含兩個核心系統：

1. **原子記憶**：跨 session 知識管理，兩層（全域/專案）、三級分類（[固]/[觀]/[臨]），索引式觸發載入
2. **Workflow Guardian**：hooks 事件驅動的工作流監督，自動追蹤修改、阻止未同步結束、提供 Dashboard 監控

詳見 `_AIDocs/Architecture.md` 和 `memory/SPEC_Atomic_Memory_System.md`。
