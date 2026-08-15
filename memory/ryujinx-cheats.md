# Ryujinx 金手指/模組系統

- Scope: global
- Confidence: [固]
- Trigger: ryujinx, 龍神, switch模擬器, cheats, 金手指, 模組, mods, TID, BID, BuildID, enabled.txt, atmosphere cheat, exefs, romfs, 人中之龍
- Last-used: 2026-04-11
- Confirmations: 1
- Related: hardware

## 知識

### Portable 模式資料夾結構

- [固] 在 Ryujinx 執行檔同層建立名為 `portable` 的資料夾（大小寫敏感）即啟用 portable 模式；所有使用者資料改存此目錄而非 `%AppData%`
- [固] 使用者的環境：`c:\G_A_M_E\Ryujinx-switch\portable\`
- [固] 模組/金手指路徑：`portable\mods\contents\{TitleID 小寫}\` — 例：Yakuza Kiwami 的 TID 是 `0100C9801FEE6000`，資料夾寫作 `0100c9801fee6000`
- [固] 每個遊戲資料夾可含多個子資料夾：`cheats\`（金手指）、`exefs\`（程式碼 patch）、`romfs\`（資源檔覆蓋）

### Cheats 檔案規則

- [固] 檔名必須是「遊戲該版本 BuildID」的前 16 字元大寫 hex + `.txt`，例：`53F407A2CFBF5202.txt`
- [固] BuildID 綁定特定遊戲版本 — 更新遊戲 → BuildID 改變 → 原 cheat 檔失效，需換對應新 BuildID 的碼
- [固] 檔案同目錄可並存多個 `.txt`（不同 BuildID，對應不同版本）；Ryujinx 只會載入與當前啟動遊戲 BuildID 相符的那一個
- [固] 檔名不能有任何前後綴（`off_xxx.txt` 會被忽略，這是常見的停用方法之一）

### Cheat 檔內部格式（Atmosphere DMNT 規格）

- [固] 每個 cheat 用 `[區段名]` 開頭（方括號），下方接若干行 16 進位機器碼；區段名 case-sensitive，可含中日英文字符與空格
- [固] 機器碼格式：`LLLLLLLL XXXXXXXX YYYYYYYY`，第一 nibble (L[0]) 是 opcode 類型
  - `0x0` Store Static Value to Memory（最常見的「寫固定值到位址」）
  - `0x1` Begin Conditional Block / `0x2` End Conditional
  - `0x3` Start/End Loop
  - `0x4` Load Register with Static Value（`400R0000 VVVVVVVV VVVVVVVV`）
  - `0x5` Load Register with Memory Value
  - `0x6` Store Static to Register Memory
  - `0x8` Keypress Conditional
  - `0x9` Arithmetic
  - `0xA` Store Register to Memory Address
  - `0xC`-`0xF` 擴展寬度指令（64 個額外 opcode）
- [固] `04000000 AAAAAAAA VVVVVVVV` = 寫 32-bit 值 V 到位址 A（main region 偏移）
- [固] `04010000 AAAAAAAA VVVVVVVV` = 寫到 heap region（偏移 A）
- [固] `master code` 通常是整個 cheat pack 的底層 hook/trampoline 安裝碼，許多其他 cheat 依賴它（尤其是用 `04010000` 的條件寫入）— **啟用任何 04010000 型 cheat 時務必同時啟用 master code**，否則可能崩潰
- [固] Cheat 執行順序：依 `.txt` 中的檔案順序，後寫入的值會覆蓋前面同位址的寫入

### enabled.txt 機制（Ryujinx 獨有，非 Atmosphere 標準）

- [固] 同目錄的 `enabled.txt` 決定哪些 cheat section 實際啟用；不在清單內的 section 雖會被解析但不會執行
- [固] 格式：每行一條 `{BuildID16}-<{區段名} Cheat>`
  - BuildID 大寫 hex 16 字元
  - 中間是 `-<`
  - 區段名必須與 `.txt` 內 `[...]` 的內容完全一致（case-sensitive、空格和符號都要相同）
  - 結尾固定是 ` Cheat>`（空格 + Cheat + 右角括號，這是 Ryujinx 自動附加的後綴）
- [固] 範例：section `[max money]` 對應 enabled 行 `53F407A2CFBF5202-<max money Cheat>`
- [固] 同一個 `enabled.txt` 可同時列多個不同 BuildID 的啟用項（支援多版本共存）
- [觀] 使用者可在 Ryujinx GUI 右鍵遊戲 → Manage Cheats 切換，GUI 會自動寫 `enabled.txt`；手動編輯也有效

### 停用 cheat 的方法

- [固] 方法 A：從 `enabled.txt` 移除該行
- [固] 方法 B：將整個 cheat 檔改名加前綴（如 `off_xxx.txt`）讓 Ryujinx 忽略整檔
- [固] 方法 C：在 `.txt` 裡刪除該 `[section]` 段落

### Ryujinx 分支現況（2026-04）

- [固] 原版 Ryujinx 於 2024-10-01 被迫停止開發
- [固] 主要延續 fork：**Ryubing**（https://git.ryujinx.app/ryubing/ryujinx） — 使用者目前版本 1.3.3
- [固] 其他 fork：`ryujinx-mirror/ryujinx`、`Kenji-NX`
- [觀] Ryubing 1.3.3 支援 BotW 1.8.x、TotK 1.4.x；mod/cheat loader 沿用原版機制未改動

### 使用者環境既有遊戲（2026-04 掃描）

- [觀] `portable\mods\contents\` 下已有 8 個遊戲資料夾：Yakuza Kiwami、BotW/Age of Calamity (01002b00111a2000)、Mario (01006000040c2000)、Xenoblade 3 (010074f013262000)、TotK (0100f2c0115b6000)、另 3 個待識別
- [觀] 多數遊戲的 `enabled.txt` 格式一致驗證了上述規範

### 常見陷阱

- [固] **前 AI session 幻覺 cheat 碼**：曾在 Yakuza Kiwami 5202.txt 寫入 7 條假碼，位址用 `00AABBCC` / `00BBDD11` / `00CCEE22` / `00DDFFAA` / `00EE11BB` 等「ABCD 模式」佔位符 — 這種位址一眼可辨認為假。真實位址分布隨機且與函式偏移相關
- [固] cheat 無法實作「關閉動態解析度」「鎖定 FPS」這類渲染管線設定 — 那是 graphics driver/engine 層級，需要 exefs patch 或 runtime mod，不能用記憶體寫入碼實現。看到這類「cheat」一律警覺是假貨
- [固] `{master code}` 用大括號寫 — 不是合法 Atmosphere 格式；section 必須用 `[]` 方括號。大括號會被當成前一 section 的延續
- [觀] 避免同時啟用互斥的 cheat（例：60/90/120 FPS 三種同時開會衝突）

### 可信來源（cheat 搜尋優先順序）

- [固] **CheatSlips**（https://www.cheatslips.com/）— 最大宗 Switch cheat 庫，依遊戲 + BuildID 分版本
- [固] **GBAtemp thread 520293**（"Cheat Codes AMS and Sx Os, Add and Request"）— 社群貢獻主戰場
- [觀] GitHub `ADEMOLA200/Switch-Emulator-Mod-Database` — 大雜燴，覆蓋不全
- [固] GameFAQs 通常沒有 hex cheat，只有遊戲內密技

## 行動

- 使用者說「幫我找 XX 遊戲的 cheat」→ 先查 CheatSlips 對應 TID/BID，次查 GBAtemp
- 找到後務必比對使用者當前的 BuildID，不相符的絕不能用（即使遊戲名對）
- 寫入 `.txt` 時：刪除舊的可疑內容前先 backup（或起碼保留真實 section）；section 名嚴格用 `[]`
- 寫入 `enabled.txt` 時：確認每行 section 名與 `.txt` 中 `[]` 內完全一致
- 看到位址出現 `AABBCC`、`BBDDFF`、`DDFFAA` 等字母 pattern → 立即判定為幻覺假碼
- 使用者要啟用 04010000 類 cheat → 同時必須啟用該 pack 的 `master code`
