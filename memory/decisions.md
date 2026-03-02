# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, 設定, config, 記住, guardian, hooks, MCP
- Last-used: 2026-03-02
- Confirmations: 1

## 知識

- [固] 版控同步支援 Git 和 SVN，自動偵測 .git/ 或 .svn/
- [固] MCP servers 已啟用: computer-use, browser-use, playwright, openclaw-notify, workflow-guardian
- [固] OpenClaw 的 atoms/ 目錄僅歸屬 OpenClaw，不作為 Claude Code 全域 atom 來源
- [固] Workflow Guardian：hooks 事件驅動的工作流監督系統，自動追蹤修改、Stop 閘門阻止未同步結束
- [固] 工作結束同步須根據情境判斷適用步驟（有 _AIDocs 才更新 _CHANGELOG，有 .git/.svn 才版控）

## 行動

- 工作結束同步時，先判斷情境（_AIDocs? .git? .svn?），只提及適用的步驟
- 同步完成後透過 MCP `workflow_signal("sync_completed")` 通知 Guardian 解除閘門
