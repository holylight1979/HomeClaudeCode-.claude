---
name: feedback-restart-workflow
description: CatClaw 編譯重啟後必須主動確認並回報結果，不可做完就停
type: feedback
---

編譯重啟流程（pnpm build → 寫 signal/RESTART）完成後，必須主動確認 PM2 狀態並回報重啟結果。

**Why:** 2026-03-21 session 中執行 build + 寫 signal file 後就停了，沒有確認重啟是否成功也沒回報，使用者必須自己追問。

**How to apply:** 任何涉及重啟/部署的操作，完成觸發動作後：
1. 等幾秒讓 PM2 偵測並重啟
2. 用 `npx pm2 status` 確認進程狀態
3. 主動回報結果（uptime、status）
