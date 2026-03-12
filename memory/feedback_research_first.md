---
name: feedback_research_first
description: 修復失敗超過門檻次數時，必須主動搜尋網路知識輔助推論，不要持續試錯
type: feedback
---

修復同一個技術問題連續失敗時，必須主動搜尋網路知識來驗證/推翻推論、找到正確解法。

**門檻規則：**
- **有使用者共同開發/測試時**：修復失敗 **≥2 次** → 主動詢問是否搜尋網路
- **獨立作業（無即時測試回饋）時**：修復失敗 **≥3 次** → 直接搜尋網路，不需再問

**Why:** Sheet export 400 問題反覆試錯多輪（context.request.get → page.goto → download race），每次都靠猜測改 code，浪費大量 token 和使用者時間。最終是搜尋網路後才發現 Google export redirect 到 googleusercontent.com、需要正確 Referer 等關鍵資訊，一次就找到 gviz/tq 端點解法。

**How to apply:**
- 碰到框架/API 行為不如預期 → 先 WebSearch 查官方文件 + GitHub issues + Stack Overflow
- 特別是第三方工具（Playwright、Selenium、各種 SDK）的邊界行為
- 修復失敗計數器：每次 fix 後測試仍失敗 → +1，成功 → 歸零
- 達到門檻時的搜尋策略：多角度搜尋（≥3 個不同 query），不要只搜一次
- 查到後再決定方案，不要靠猜測寫 code → 跑 → 失敗 → 改 → 再跑的循環
