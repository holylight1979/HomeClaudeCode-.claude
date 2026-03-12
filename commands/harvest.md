# /harvest — Google Docs/Sheets 收割工具

> 啟動 Playwright Chrome 瀏覽器，邊瀏覽邊自動收割 Google Docs/Sheets 為 Markdown/CSV。
> 全域 Skill，工具位於 `c:/tmp/gdoc-harvester/`。

---

## 參數

- `$ARGUMENTS` 可傳入：
  - `--depth N` — 連結追蹤深度（預設 1）
  - `--output DIR` — 輸出目錄（預設 `c:/tmp/gdoc-harvester/output`）
  - `--fresh` — 重新複製 Chrome 登入狀態（需先關閉 Chrome）

---

## 執行流程

### Step 1: 環境檢查

1. 確認 Python 依賴已安裝：

```bash
python -c "import playwright, markdownify, bs4, aiohttp, yarl" 2>&1
```

- 若失敗 → `python -m pip install playwright markdownify beautifulsoup4 aiohttp yarl`
- 確認 Playwright Chrome 已安裝：`python -m playwright install chrome`

2. 確認工具檔案存在：

```bash
ls c:/tmp/gdoc-harvester/harvester.py c:/tmp/gdoc-harvester/dashboard.py
```

- 若不存在 → 告知使用者工具檔案遺失，需要重建

### Step 2: 提醒使用者

告知使用者：

> 即將啟動收割瀏覽器。
> - 如果傳了 `--fresh`，請先**關閉所有 Chrome 視窗**
> - 瀏覽器會開出 Dashboard tab + Google Docs 首頁
> - 正常瀏覽 Google Docs/Sheets，工具自動擷取
> - 關閉瀏覽的 tab（保留 Dashboard）即結束收割

### Step 3: 背景啟動

```bash
cd c:/tmp/gdoc-harvester && python harvester.py $ARGUMENTS 2>&1
```

- 使用 `run_in_background: true` 啟動，讓使用者可以繼續對話
- 定期用 `TaskOutput` 檢查狀態（使用者詢問時）

### Step 4: 結束後報告

收割結束後（使用者關閉瀏覽器），讀取輸出：

1. 列出 `c:/tmp/gdoc-harvester/output/` 的新檔案
2. 報告統計：幾份 Docs、幾份 Sheets、幾個錯誤
3. 若有 `_overflow_links.md`，提醒使用者有超出深度限制的連結
4. 詢問使用者是否要：
   - 增加深度重跑
   - 清理重複檔案
   - 推上 GitLab

---

## 已知限制

- 首次使用需關閉 Chrome 以複製 cookies
- 部分 Google Workspace 文件可能因帳號權限不同而匯出失敗
- Sheet export 依賴 aiohttp + browser cookie 同步，偶爾需重新同步
- 同一文件被多次導航可能產生重複檔案（`_1`, `_2` 後綴）
