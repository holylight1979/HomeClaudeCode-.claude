# 通用工作流引擎

> 全域自動載入，適用於所有專案。專案特有知識由各專案根目錄 `CLAUDE.md` 定義。

---

## 一、_AIDocs 知識庫

### Session 啟動檢查

每個 session 第一次互動前，檢查專案根目錄是否有 `_AIDocs/`：

- **沒有** → 自動執行 `/init-project`
- **已有** → 開工前先讀 `_AIDocs/_INDEX.md` 確認已有哪些文件

### 工作中規則

1. 不確定的架構事實必須查文件或原始碼，禁止猜測
2. 修改核心結構、發現新認知、踩到陷阱 → 更新 `_AIDocs/*.md` + `_CHANGELOG.md`
3. 新增文件時同步更新 `_AIDocs/_INDEX.md`

---

## 二、原子記憶（兩層）

原子記憶分 **全域層** 和 **專案層**，每層各有 `MEMORY.md`（Atom Index + 高頻事實）。

### 載入順序

1. **全域 atoms** — `Read ~/.claude/memory/MEMORY.md`，比對 Trigger，命中則載入對應 atom 檔
2. **專案 atoms** — `Read` 專案對應的 auto-memory `MEMORY.md`，比對 Trigger，命中則載入

兩層都要做。全域層放跨專案共用知識（使用者偏好、通用決策），專案層放專案綁定知識（架構、坑點）。

### atom 格式

元資料（Scope/Confidence/Trigger/Last-used/Confirmations）+ 知識段落 + 行動段落 + 演化日誌。
完整規格：`~/.claude/memory/SPEC_Atomic_Memory_System.md`

### 決策記憶三層分類

| 符號 | 說明 | 引用行為 |
|------|------|---------|
| `[固]` | 跨多次對談確認，長期有效 | 直接引用 |
| `[觀]` | 已決策但可能演化 | 觸及時簡短確認 |
| `[臨]` | 單次決策 | 觸及時明確確認 |

### 記憶什麼 / 晉升 / 淘汰

- 使用者說「記住」「以後都這樣」→ 直接 `[固]`
- 使用者做了取捨（A 不做 B）→ `[臨]`
- 反覆出現的偏好 → `[觀]`，確認後晉升 `[固]`
- 晉升：`[臨]` 2+ sessions → `[觀]`；`[觀]` 4+ sessions → `[固]`
- 淘汰：超期 atom 移入 `_distant/{年}_{月}/`（遙遠記憶），不刪除

### 管理原則

- `MEMORY.md` 只放索引 + 高頻事實（≤30 行），細節放 atom 檔（≤200 行）
- `_CHANGELOG.md` 保留最近 ~8 筆，舊條目移至 `_CHANGELOG_ARCHIVE.md`
- 健檢工具：`python ~/.claude/tools/memory-audit.py`（格式驗證、過期分析、晉升建議、重複偵測）

---

## 三、工作結束同步

完成有意義的修改後，**根據情境判斷哪些步驟適用**，主動向使用者提出：

> 「這次修改涉及 N 個檔案，要我同步更新 {適用項目} 嗎？」

### 情境判斷（缺少的就跳過，不要提及）

| 條件 | 同步步驟 |
|------|---------|
| 有 `_AIDocs/` | → 追加 `_CHANGELOG.md`（超 8 筆觸發滾動淘汰） |
| 有新知識/決策/坑點 | → 更新 atom 檔（知識段落 + Last-used） |
| 有 `.git/` | → 秘密洩漏檢查 → `git add` → `git commit` → `git push` |
| 有 `.svn/` | → 秘密洩漏檢查 → `svn add`（新檔案）→ `svn commit` |
| 都沒有 | → 僅更新 memory atoms（如有需要） |

適用的步驟都要做完，不要只做一半。

### Workflow Guardian 自動監督

`~/.claude/hooks/workflow-guardian.py` 會在背景追蹤修改：
- **PostToolUse**：自動記錄 Edit/Write 修改的檔案
- **Stop 閘門**：若有未同步的修改，會阻止 Claude 結束並提醒
- **防無限迴圈**：最多阻止 2 次，第 3 次強制放行
- MCP tools（`workflow_signal`）：同步完成後發 `sync_completed` 解除閘門
- Dashboard：`http://127.0.0.1:3848`

---

## 四、對話管理

- 獨立子任務可新開對話（確保新知已寫入 MEMORY.md / _AIDocs）
- 有順序依賴的任務應在同一對話完成
- Context 壓縮過 / 任務告一段落 / 工具呼叫大量累積 → 主動提醒開新 session
- 已決策事項不重複分析，簡短提及即可；已有 _AIDocs 文件不重新掃碼

---

## 五、使用者偏好

- **回應語言**：繁體中文（技術術語可英文）
- **反對過度綁定**：框架層應薄，開發者要能理解底層
- **高可讀性**：一個檔案看完相關邏輯，不需跳轉多處
