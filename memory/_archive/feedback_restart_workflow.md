---
name: feedback-restart-workflow
description: CatClaw 編譯重啟完整流程：build → 寫 signal/RESTART（帶 CATCLAW_CHANNEL_ID）→ 確認 PM2 → 回報
type: feedback
---

編譯重啟流程必須一氣呵成，不可分步。

**Why:** 2026-03-22 連續犯錯：(1) 寫完 signal file 後沒主動確認和回報 (2) channelId 留空導致 bot 無法在 Discord 回報重啟。(3) 沒使用 pending-tasks 自動存檔，導致跨步驟時遺漏。

**How to apply:**
1. 重啟屬於 ≥3 步任務，開始前先寫 `_staging/pending-tasks.md`（遵守 session-management.md 規則）
2. `pnpm build` 編譯
3. 寫 `signal/RESTART`，channelId 從 `$CATCLAW_CHANNEL_ID` env var 讀取：
   ```bash
   echo "{\"channelId\":\"${CATCLAW_CHANNEL_ID}\",\"time\":\"$(date -u +%Y-%m-%dT%H:%M:%S%z)\"}" > signal/RESTART
   ```
4. sleep 5 → `npx pm2 status` 確認重啟
5. 主動回報結果（status、uptime、PID）
6. 步驟 2-5 合併在同一個 Bash 指令串中執行
7. 完成後刪除 pending-tasks.md
