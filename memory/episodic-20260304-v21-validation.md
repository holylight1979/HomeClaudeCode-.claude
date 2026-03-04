# Session: 2026-03-04 v2.1 活體驗證

- Scope: global
- Confidence: [臨]
- Type: episodic
- Trigger: session, episodic, guardian, cleanup, dashboard, v2.1
- Last-used: 2026-03-04
- Created: 2026-03-04
- Confirmations: 0
- TTL: 24d
- Expires-at: 2026-03-28

## 知識

- [臨] 舊 MCP server process 佔 port 3848 導致 v2.1 routes 和 cleanup 不生效
- [臨] 殺舊 process 後 heartbeat 15s 內自動 rebind，cleanup 一次清掉 13/15 state files
- [臨] sync_completed signal 正確寫入 ended_at，Tier 1 cleanup 生效
- [臨] Episodic tab / Health tab / Sessions tab 全部正常運作

## 行動

- session 自動摘要，TTL 24d 後自動淘汰
- 若需長期保留特定知識，應遷移至專屬 atom

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-04 | 手動建立 episodic atom（測試 dashboard parsing） | session:b732b796 |
