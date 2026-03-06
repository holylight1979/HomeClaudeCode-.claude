# Claude Code 跨 Session 記憶系統

Claude Code 每次 session 都是白紙——上次的決策、踩過的坑、你的偏好，全部歸零。
我做了一套基於 hooks 的記憶層來解決這個問題，分享給大家。

---

## 它做什麼

- **自動記住**：架構決策、使用者偏好、踩過的坑，存成 Markdown atom 檔案
- **自動注入**：下次 session 輸入相關 prompt 時，自動載入對應知識（keyword + 語意搜尋）
- **自動演進**：知識三層分類 `[臨]→[觀]→[固]`，重複出現的知識自動晉升，過期的自動歸檔
- **不改 Claude Code 本體**：純 hooks + Python 腳本

## 運作方式

一支 Python 腳本掛在 Claude Code 的 6 個 hook event 上：

- `SessionStart` — 載入記憶索引
- `UserPromptSubmit` — 比對關鍵字 + 向量搜尋，注入相關 atom
- `PostToolUse` — 追蹤修改的檔案
- `Stop` — 有未同步修改就擋住，提醒你 commit
- `SessionEnd` — 自動產生 session 摘要，萃取知識

語意搜尋用本地 Ollama（qwen3-embedding + qwen3:1.7b），零額外雲端 token。
Token overhead 約 200K context 的 1.5-2.5%。

## 安裝

**GitHub**: https://github.com/holylight1979/MyClaudeCode-.claude

### 你要先自己裝好的

1. **Ollama** — https://ollama.com 下載安裝（Claude Code 沒辦法幫你裝這個）
2. **Python 3.8+**

### 剩下的交給 Claude Code

Clone repo 後，開 Claude Code 貼這句：
```
請讀 ~/.claude/Install-forAI.md 並按步驟幫我安裝原子記憶系統。
先檢查我的硬體環境（CPU、RAM、GPU），再決定要拉哪些 Ollama model 和用哪個 Vector DB。
```

它會根據你的環境選擇合適的 model size、裝 Python 套件、設定 hooks 和 config、初始化記憶索引並驗證。

架構細節、流程圖、FAQ 都在 `README.md`。
