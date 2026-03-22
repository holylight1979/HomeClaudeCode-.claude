# 自我迭代原則

- Scope: global
- Confidence: [固]
- Trigger: 自我迭代, self-iteration, 演進原則, 規則管理
- Last-used: 2026-03-13
- Confirmations: 1
- Type: knowledge
- Related: decisions, spec

## 適用範圍

自我迭代僅適用於**規則管理**（atom 的新增/修改/刪除）。不適用於回答使用者問題。

---

## 原則 1：品質函數

每次互動產生三類訊號，驅動規則權重調整：
- **正向（+）**：使用者確認 → 強化規則
- **負向（−）**：使用者糾正 → 修正或降權
- **中性（0）**：無回饋 → 維持現狀（間歇增強）

**執行主體：Hook 自動化**（workflow-guardian SessionEnd 自動計算）

**V2.16 自動化狀態**：`_self_iterate_atoms()` SessionEnd 掃描所有 atoms，計算衰減分數（`score = 0.5 * recency + 0.5 * usage`），低分 atoms（< 0.3）自動寫入 `_staging/archive-candidates.md` 供人工審閱。成熟 atom（Confirmations ≥ 20）中的 [臨] 自動升 [觀]。

---

## 原則 2：證據門檻

單次觀察只記錄為 [臨]，≥2 次獨立出現（跨 session）才考慮建立正式規則。

- 單一樣本可能是噪音，不足以建立模式
- [臨] ×2 確認 → 可考慮升 [觀]（需使用者同意）

**執行主體：Claude 決策**（寫入新 atom 時判斷是否已有先例）

**V2.16 自動化狀態**：成熟 atom（Confirmations ≥ 20）中的 [臨]→[觀] 已自動化（不需使用者確認）。低 Confirmations 的 atom 仍由 Claude 判斷。

---

## 原則 3：震盪偵測

同一規則在 3 session 內被修改 2+ 次 → 暫停修改，等待更多資訊。

- 反覆修改 = 系統不穩定，繼續調整只會加劇震盪
- 暫停後需使用者明確指示才恢復修改

**執行主體：Hook 自動化**（V2.16 後由 Hook 跨 Session 持久化）

**V2.16 自動化狀態**：`_save_oscillation_state()` SessionEnd 將偵測結果寫入 `workflow/oscillation_state.json`；`_load_oscillation_warnings()` SessionStart 注入 `[Guardian:Oscillation]` 警告。原本由 Claude 手動檢查演化日誌，現改為 Hook 自動追蹤。

---

## 定期檢閱

收到系統提醒時（每 ~6 sessions，config `review_interval` 可調）：掃描 episodic atoms → 收攏重複 → 晉升有價值知識 → 寫入 `workflow/last_review_marker.json`。

## 演化日誌

- 2026-03-10: 建立，8 條原則 × 跨學科理論背書
- 2026-03-13: V2.11 精簡 — 砍到 3 條可執行原則，移除所有理論背書
- 2026-03-22: V2.16 對照更新 — 每條原則加入自動化狀態說明
