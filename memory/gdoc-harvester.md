---
name: gdoc-harvester
description: Google Docs/Sheets 收割工具開發經驗 — Playwright + Chrome + cookie 同步
type: project
---

## Google Docs/Sheets Harvester 開發記錄

**位置**: `c:/tmp/gdoc-harvester/`
**目標**: 邊瀏覽邊收割 Google Docs/Sheets → Markdown/CSV → 未來推上公司 GitLab

### 踩坑記錄（按時序）

1. **Playwright Chromium 無法登入 Google** — Google 偵測自動化瀏覽器，拒絕登入
   - 解法: `channel="chrome"` 用本機 Chrome + `--disable-blink-features=AutomationControlled`

2. **Chrome profile lock 衝突** — 不能同時用同一個 profile
   - 解法: 複製 Chrome Default profile 的 Cookies/Login Data 等關鍵檔到獨立目錄
   - 注意: 複製前需要關閉本機 Chrome

3. **`context.request.get()` 不帶 browser cookies** — HTTP 400/401
   - 這是 Playwright 的設計限制，context.request 不共用 browser cookies

4. **`page.evaluate` + `fetch()` 被 CORS 擋** — Google export URL redirect 到不同域名
   - 瀏覽器 fetch 無法跨域跟隨 Google 的 redirect

5. **`page.goto()` export URL 觸發 download** — Playwright 報 "Download is starting" 錯誤
   - 解法: `accept_downloads=True` + `page.expect_download()` 攔截
   - 成功下載了 Doc，但 export page 的 session 可能跟使用者不同帳號

6. **export page session 不同步** — 用獨立 page 打開 docs.google.com，不一定登入了正確帳號
   - 最終解法: **aiohttp + browser cookies 同步**
     - `context.cookies()` 取得所有 cookies
     - 注入到 `aiohttp.CookieJar`
     - 用 `aiohttp.ClientSession` 直接 HTTP GET export URL
     - 每次偵測到新文件時重新同步 cookies

### 最終架構

- Playwright Chrome (persistent context) — 使用者瀏覽用
- `framenavigated` 事件偵測 Google Docs/Sheets URL
- `aiohttp` + browser cookies — 背景下載 export HTML/CSV
- `markdownify` — HTML → Markdown
- `BeautifulSoup` — 解析標題、提取內部連結
- Dashboard (`http://127.0.0.1:8787`) — 即時顯示收割進度
- 連結深度追蹤 — 自動爬取文件內的 Google 連結

### 待修

- 同一份文件重複偵測（不同 URL 相同 doc_id 但有些是不同文件卻同名）
- Sheet export 部分帳號權限問題
- 檔名去重邏輯（目前用 `_1`, `_2` 後綴）

**Why:** 使用者要把散落在 Google Drive 的公司文件整理到 GitLab
**How to apply:** 後續改進此工具或做成 skill `/harvest` 時參考
