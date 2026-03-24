---
name: feedback-no-test-to-svn
description: 測試/新手作業的程式碼禁止上傳 SVN — 使用者明確糾正
type: feedback
---

測試用、新手作業、練習用途的程式碼不可以上傳 SVN repo。

**Why:** 使用者明確指出過，測試用檔案不應進入版控。r10854 誤上傳 WndForm_UITutorial（新手作業 S2）+ ClaudeEditorHelper 後被使用者退版。

**How to apply:** 執行「上GIT」/「上SVN」前，判斷異動檔案是否屬於測試/練習/新手作業性質。如果是 → 不加入 svn add，或向使用者確認哪些可以上。ClaudeEditorHelper.cs 等工具類是否可上傳也需確認。
