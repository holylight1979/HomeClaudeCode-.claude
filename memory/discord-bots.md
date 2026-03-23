---
name: discord-bots
description: Wells 的兩個 Discord bot 帳號區分 + Claude Discord Plugin 設定踩坑
type: project
---

# Discord Bot 帳號區分

- **Claude Discord Plugin bot**：由 Claude Code 的 Discord plugin 啟動，access.json 設定在 `~/.claude/channels/discord/`
- **CatClaw bot**（ID: `1320597601506299985`）：Wells 自製的 CatClaw 系統啟動的 bot

**Why:** 同一個伺服器有兩隻 bot，需要分辨哪隻是哪個系統驅動的。
**How to apply:** 在 Discord 頻道收到訊息時，注意自己是 Claude Plugin bot，不要與 CatClaw bot 混淆。

# Claude Discord Plugin 設定

## 已啟用的頻道
- DM：allowlist 含 Wells（`480042204346449920`）
- 群組頻道 `1485277764205547630`：requireMention=false

## 踩坑
- [固] access.json 的 `groups` key 必須用**頻道 ID**（channel snowflake），不是伺服器 ID（guild snowflake）。用錯了 bot 不會回應也不報錯。
- [固] Claude Code session 關閉 = Discord plugin MCP server 斷線 = bot 離線。要持久運作必須保持 session 開著。
