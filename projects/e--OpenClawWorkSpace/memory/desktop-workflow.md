# Atom: 桌面自動化運作流（Desktop Workflow Patterns）

- Scope: Claude Code 桌面操作通用
- Confidence: [觀]
- Source: 2026-02-28 holylight — LINE 監測任務實戰歸納
- Last-used: 2026-03-05
- Confirmations: 1
- Trigger: 需要操作畫面、切換視窗、監測其他 session、GUI 自動化任務
- Privacy: 無敏感資料

---

## 一、位置快取（Position Cache）

> **原則**：首次操作用 screenshot+OCR 定位，確認後快取座標。
> 後續操作直接用快取座標，僅在操作失敗時重新定位。

### VS Code Claude Code Extension

| 元素 | 座標 (abs) | 備註 |
|------|-----------|------|
| 左側 session tab | ~(1380, 123) | 偏左點擊，避開 X 關閉鈕 |
| 右側 session tab | ~(1600, 123) | 第二個 tab |
| 左 tab X 關閉鈕 | ~(1547, 123) | **危險區域，絕對避開** |
| session 輸入框 | ~(1300, 875) | placeholder: "Queue another message..." |
| 聚焦輸入框快捷鍵 | `Ctrl+Escape` | 比點擊更可靠，切換 focus/unfocus |
| 面板內容區域 | ~(1250, 500) | 捲動目標位置 |

### LINE Desktop (3WITH-AI)

| 元素 | 座標 (abs) | 備註 |
|------|-----------|------|
| 聊天輸入框 | ~(150, 930) | placeholder: "輸入訊息" |
| 視窗標題 | "3WITH-AI" | focus_window 用 |

### 注意事項

- 座標會因視窗位置/大小改變而失效
- **Session tab 位置**取決於 tab 文字長度和數量
- 每次 session 開始時，應做一次全螢幕截圖校準

---

## 二、核心工作流 SOP

### A. 切換 Claude Code Session Tab

```
1. focus_window("Visual Studio Code")
2. mouse_click(目標 tab 座標)
3. screenshot 確認（看 tab 高亮狀態 + 內容區域）
```

### B. 在其他 Session 輸入訊息

```
1. 切換到目標 tab（SOP A）
2. key_press("ctrl+escape")  ← 聚焦輸入框，比 mouse_click 可靠
3. screenshot 確認 placeholder 變成 "Queue another message..."
4. key_type("訊息內容")
5. screenshot 確認文字已輸入
6. key_press("enter")
```

### C. LINE 發送訊息

```
1. focus_window("3WITH-AI")
2. mouse_click(輸入框座標)
3. key_type("訊息內容")
4. screenshot 確認文字正確
5. key_press("enter")
```

### D. 監測迴圈（Monitoring Loop）

```
1. 切到目標 session tab
2. mouse_scroll(amount=50, 目標區域) ← 大量捲動到底部
3. screenshot 讀取最新內容
4. 判斷：有新請求？
   - 有 → 執行對應動作 → 回到步驟 1
   - 無 → 切回自己的 tab → wait(60000) → 回到步驟 1
```

---

## 三、優化策略（待實作）

### Strategy 1: 短期記憶模式（Screenshot Cache）

**問題**：每次監測都重新截圖+OCR 整個畫面，浪費時間
**方案**：

- 記住「上次截圖的內容摘要」（文字 hash 或關鍵特徵）
- 下次只截關鍵區域（如最底部 200px）做差異比對
- 內容沒變 → 跳過，不做完整分析
- 內容有變 → 才截完整畫面詳細分析

**實作方式**：
```
上次摘要 = "Calculating..."
本次截圖 → 狀態文字 = "Calculating..."
相同 → skip（省下大量 token）
不同 → 完整截圖分析
```

### Strategy 2: 差異檢測（Differential Check）

**問題**：每次都全面重新掃描，重複計算已知位置
**方案**：

- 首次操作：完整 OCR 建立「畫面地圖」
- 後續操作：只截小區域確認「狀態指標」
  - Claude Code: 底部 ~100px（看 "Generating..." / "Thinking..." / 完成文字）
  - LINE: 最後一則訊息區域
- 狀態指標變化時才觸發完整分析

**關鍵狀態指標位置**：
| 指標 | 截圖區域 | 判斷 |
|------|---------|------|
| Claude Code 活動狀態 | (1000, 820, 460, 60) | "Generating/Thinking/Simmering..." = 工作中 |
| Claude Code 最新輸出 | (1000, 400, 460, 400) | 看有無 "請從 LINE 發" 等關鍵字 |
| LINE 最新訊息 | (0, 700, 300, 100) | 確認訊息發送成功 |

### Strategy 3: 位置自適應（Adaptive Positioning）

**問題**：硬編碼座標容易因視窗調整而失效
**方案**：

- 每個 session 首次操作時做「校準截圖」
- 用 OCR 找到錨點文字（如 tab 文字、placeholder 文字）
- 從錨點反推精確座標
- 快取座標，操作失敗時自動重新校準

**校準流程**：
```
1. get_screen_size() → 確認解析度
2. screenshot_with_ocr(全螢幕) → 建立座標地圖
3. 找到已知文字的座標 → 計算偏移
4. 快取所有 UI 元素位置
5. 後續操作直接用快取
```

### Strategy 4: 智能捲動（Smart Scroll）

**問題**：固定 scroll amount 可能不夠或過多
**方案**：

- 首次大量捲動 (amount=50) 確保到底部
- 後續監測只需小量捲動 (amount=5-10) 看增量內容
- 如果內容沒有增長（同一個狀態文字），不需捲動

---

## 四、踩坑記錄

| 坑點 | 解法 |
|------|------|
| VS Code 是 Electron，get_ui_tree 看不到內部元素 | 純靠 screenshot+OCR 視覺辨識 |
| Claude Code 輸入框 click 不聚焦 | 用 `Ctrl+Escape` 快捷鍵聚焦 |
| 自己的 tool call 輸出會出現在自己的 session | 切 tab 後立即截圖，避免被自己的輸出干擾 |
| LINE 輸入框位置隨視窗高度變化 | 用 OCR 找 "輸入訊息" 文字定位 |
| Tab 座標因文字長度不同而偏移 | 首次用 screenshot 確認，之後快取 |
| 大量捲動後位置感丟失 | 每次捲動後截圖確認當前位置 |

---

## 五、工具選擇指南

| 場景 | 最佳工具 | 說明 |
|------|---------|------|
| 找 UI 元素位置 | screenshot_with_ocr | OCR 回傳座標，可直接用 |
| 確認畫面狀態 | screenshot (jpeg, q=70) | 快速、省 token |
| 精確文字定位 | screenshot_with_ocr | 需要座標時用 |
| 原生 Windows 程式 | get_ui_tree + click_element | UI Automation 最可靠 |
| Electron/Web 程式 | screenshot + mouse_click | UI Automation 無效 |
| 輸入文字 | key_type | 支援 Unicode |
| 快捷鍵 | key_press | 如 "ctrl+escape", "enter" |
| 等待 | wait(ms) | 監測迴圈用 |

## 演化日誌

- 2026-02-28 [臨→觀] 首次實戰：12 輪 LINE 監測任務，建立完整 SOP + 優化規劃
