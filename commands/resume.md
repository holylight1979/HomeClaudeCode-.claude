# /resume — 自動續接 Session

你即將執行「自動續接」流程：生成下一階段的續接 prompt，然後在 VS Code 開啟新的 Claude Code session 並自動貼上執行。

## 輸入

$ARGUMENTS

## Step 1: 收集當前工作狀態

掃描以下來源，彙整「目前做到哪」：

1. **Todo list**：檢查是否有未完成的 todo items
2. **最近的 git 變更**：`git status` + `git log --oneline -5`
3. **進行中的工作單元**：掃描 atoms 中標記為 🔄 的工作單元
4. **使用者提供的 $ARGUMENTS**：如果有明確的下一步指示，優先採用

彙整為：
- **已完成**：本 session 完成了什麼（1-3 句）
- **下一步**：接下來要做什麼（具體步驟）
- **關鍵上下文**：新 session 需要知道的檔案路徑、決策、注意事項

## Step 2: 生成續接 Prompt

根據 Step 1 的彙整，生成一個**自包含**的續接 prompt。格式：

```
[續接] {任務名稱}

## 背景
{1-3 句說明這個任務的來龍去脈}

## 已完成
{上一個 session 做完的事，條列}

## 本階段目標
{這個 session 要完成的具體步驟，條列}

## 關鍵上下文
- 相關檔案：{路徑列表}
- 注意事項：{任何新 session 需要知道的坑點或決策}

## 完成條件
{怎樣算完成，包括驗證方式}

完成後請執行：驗證 → 上 GIT → 如有下一階段則再次 /resume
```

**重要**：prompt 必須自包含——新 session 不會有當前 session 的 context，所以所有必要資訊都要寫進去。

## Step 3: 確認

將生成的 prompt 顯示給使用者，詢問：

> 「續接 prompt 已準備好。要我自動開新 session 並執行嗎？（Y/直接 Enter 確認，或修改後告訴我）」

等待使用者確認。如果使用者要修改，根據回饋調整後再次確認。

## Step 4: 自動化執行

使用者確認後，依序執行以下 MCP 自動化步驟：

### 4.1 複製 prompt 到剪貼簿
使用 `mcp__MCPControl__set_clipboard_content` 將續接 prompt 存入剪貼簿。

### 4.2 開啟新 Claude Code Session（獨立視窗）

**注意**：必須用 "Open in New Window"（獨立視窗），不要用 "Open in New Tab"。
原因：New Tab 會與當前 session 的側邊欄共存，造成輸入框焦點衝突，prompt 會貼到錯誤的面板。

1. `mcp__MCPControl__press_key_combination` → `["ctrl", "shift", "p"]`（開啟 Command Palette）
2. `mcp__MCPControl__type_text` → `"Claude Code: Open in New Window"`
3. `mcp__MCPControl__press_key` → `"enter"`
4. 等待 5 秒讓新視窗載入完成

### 4.3 截圖確認新 session 已開啟
使用 `mcp__MCPControl__get_screenshot` 截圖確認：
- 新的獨立 VS Code 視窗已開啟
- Claude Code 歡迎畫面可見
- 輸入框可見且為空（顯示 "ctrl esc to focus or unfocus Claude"）

如果截圖顯示新 session 未正確開啟，嘗試備用方案：
- 備用方案：`Ctrl+Shift+P` → 輸入 "Claude Code: Open in New Tab" → Enter（需額外處理焦點）

### 4.4 貼上 prompt
1. 點擊新視窗中 Claude Code 輸入框（大約在視窗底部中央，y≈553）
2. `mcp__MCPControl__press_key_combination` → `["ctrl", "v"]`

### 4.5 截圖確認 prompt 已貼上
截圖確認 prompt 內容已出現在輸入框中。如果貼到了編輯器而非輸入框，Ctrl+Z 撤銷後重新點擊輸入框再貼上。

### 4.6 按下 Enter 開始執行
`mcp__MCPControl__press_key` → `"enter"`

### 4.7 最終確認
等待 5 秒後截圖，確認新 session 已開始處理（Claude 有回應或顯示 "thinking"）。

## Step 5: 回報

回到原 session，告知使用者：

> 「✅ 新 session 已啟動，續接 prompt 已自動貼上執行。你可以切換到新視窗查看進度。」

如果自動化過程中任何步驟失敗，改為手動模式：
> 「⚠ 自動開啟失敗。續接 prompt 已複製到剪貼簿，請手動開新 session 後 Ctrl+V 貼上。」
