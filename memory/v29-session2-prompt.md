[續接] V2.9 記憶檢索強化 — Session 2/3

## 背景
Session 1 完成了 3 項工作，git push 995d2d7：
1. 刪除 `c--Projects-sgi-server/memory/`（冗餘子集）
2. Project-Aliases：`parse_project_aliases()` + cross-project alias 匹配 → 注入整份 MEMORY.md
3. Blind-Spot Reporter：keyword + vector + alias 全空時注入 `[Guardian:BlindSpot]` 警告

已驗證：BlindSpot 在 Session 1 結尾已實際觸發。

## 本階段目標

請先進入 Plan Mode (Shift+Tab)，讀完設計規格後再開始實作。

**1. Related-Edge Spreading（多跳檢索）**
- 設計規格：`~/.claude/memory/v3-design-spec.md`（§ Related-Edge Spreading）
- 現行 Related auto-loading：`workflow-guardian.py` L898-926（只載入 first-line summary）
- 改為：`spread_related()` 函式，depth=1（可配置），遍歷 Related 欄位
- Related atoms 降優先（排在 keyword/vector 結果後）
- 受 token budget 約束
- ~40 行

**2. ACT-R Activation Scoring（時間加權排序）**
- 設計規格：`~/.claude/memory/v3-design-spec.md`（§ ACT-R Activation Scoring）
- 公式：`B_i = ln(Σ t_k^{-0.5})`，t_k = 距第 k 次存取的秒數
- 每次 atom 被觸發 → 在 `{atom_name}.access.json` 追加 timestamp
- 注入排序改用 B_i 降序（取代原本的遍歷順序）
- 保留最近 50 筆 access entry
- `Confirmations` 欄位保留但語義改為累計存取次數
- ~50 行 + 每 atom 一個 .access.json

## 關鍵上下文
- 設計規格：`~/.claude/memory/v3-design-spec.md`
- 現行 hook：`~/.claude/hooks/workflow-guardian.py`
  - Related auto-loading：L898-926
  - Atom injection + budget：L870-896
  - Metadata update (Last-used, Confirmations)：L933-1004
  - `parse_memory_index()`：L165-197
  - `parse_project_aliases()`：L200-212（V2.9 S1 新增）
  - Cross-project + alias：L821-855
  - Blind-Spot Reporter：L1034-1042（V2.9 S1 新增）
- 現行 SPEC：`~/.claude/memory/SPEC_Atomic_Memory_System.md`
- Hook 3s timeout（UserPromptSubmit）

## 完成條件
1. atom 有 Related 欄位 → 相關 atom 被載入（depth=1）
2. 多次觸發的 atom 排序高於冷門 atom
3. `.access.json` 檔案正確記錄 timestamp
4. 既有 trigger match / vector search / alias 不受影響
5. 效能在 3s 內

完成後請執行：驗證 → 上 GIT → 產 Session 3 prompt（整合測試 + SPEC 更新 + 版號升級）
