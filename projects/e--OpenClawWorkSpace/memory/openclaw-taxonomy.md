# Atom: 人事時地物分類系統

- Scope: global
- Confidence: [固]
- Source: 2026-03-05 V2.3 升級 — taxonomy/categories.json 完整掃描
- Last-used: 2026-03-15
- Confirmations: 7
- Trigger: 人事時地物, 五大分類, taxonomy, 分類系統, categories.json, 子分類, atomPaths, noMemoryIntents
- Privacy: public

## 知識

### 系統概述

Gateway preprocessor 使用五大分類（人/事/時/地/物）+ 30 子分類來分類使用者意圖。
由 A15 intent-classifier（qwen3:1.7b）執行，結果影響 A17 fusion 排序（categoryAlignment +0.15）。

### 完整分類表

**人 (person) — 8 子分類**

| 子分類 | 關鍵詞 | atomPaths |
|--------|--------|-----------|
| identity | 誰、名字、ID、帳號 | persons/*/_profile.md |
| impression | 感覺、印象、氣氛 | persons/*/personality/ |
| behavior | 說話方式、風格、習慣 | persons/*/personality/ |
| traits | 性格、價值觀、MBTI | persons/*/personality/ |
| skills | 擅長、專業、技能 | persons/*/interests/ |
| role | 角色、權限、管理 | persons/*/relationships/ |
| relations | 關係、認識、朋友 | persons/*/relationships/ |
| preferences | 喜歡、偏好、方式 | persons/*/principles/ |

**事 (event) — 6 子分類**

| 子分類 | 關鍵詞 | atomPaths |
|--------|--------|-----------|
| decision | 決定、選擇、為什麼 | global/decisions.md |
| task | 任務、工作、進度 | events/ |
| conversation | 討論、共識、談到 | events/ |
| incident | 錯誤、問題、bug | global/pitfalls.md |
| milestone | 完成、發布、版本 | events/, _CHANGELOG.md |
| process | 流程、步驟、SOP | global/, skills/ |

**時 (time) — 5 子分類**

| 子分類 | 關鍵詞 | atomPaths |
|--------|--------|-----------|
| now | 現在、正在 | events/_active.md |
| recent | 最近、昨天 | — |
| periodic | 每週、經常 | — |
| historical | 以前、過去 | — |
| future | 計畫、未來 | — |

**地 (place) — 5 子分類**

| 子分類 | 關鍵詞 | atomPaths |
|--------|--------|-----------|
| platform | Discord、LINE | — |
| channel | 群組、DM | channels/ |
| workspace | 專案、repo | — |
| physical | 地點、位置 | — |
| network | URL、API、endpoint | — |

**物 (object) — 6 子分類**

| 子分類 | 關鍵詞 | atomPaths |
|--------|--------|-----------|
| tool | 工具、軟體、CLI | global/ |
| config | 設定、配置、參數 | global/decisions.md |
| concept | 概念、理論、方法 | global/ |
| artifact | 程式碼、檔案、產出 | — |
| resource | 資源、連結、參考 | global/ |
| entity | 硬體、裝置、伺服器 | global/decisions.md |

### noMemoryIntents（跳過記憶檢索）

- **greeting**: 你好、嗨、早安、hello、hi
- **casual_chat**: 哈哈、笑死、好喔
- **acknowledgment**: 好的、收到、謝謝

訊息≤5字 + 命中以上關鍵詞 → `need_memory=false`，不觸發 A4/A16 搜尋

### 分類系統自我演化

- `expandable: true` — 開啟自動擴展
- `autoExpandThreshold: 5` — 未分類累積 5 筆時建議新子分類
- 未分類記錄: `taxonomy/unclassified.jsonl`
- A15 分類信心度 < 0.4 時自動記錄到 unclassified

### 與 V2.3 Claude Code 的關係

| 面向 | Gateway (人事時地物) | V2.3 CC (trigger-based) |
|------|---------------------|------------------------|
| 分類引擎 | A15 qwen3:1.7b | workflow-guardian.py keyword match |
| 向量搜尋 | A16 LanceDB | ChromaDB (port 3849) |
| 排序公式 | A17 fusion (0.5+0.5) | Ranked search (weighted) |
| 分類數 | 5大類×30子分類 | trigger 關鍵詞匹配 |
| 交集 | additional_atom_dirs 讓 V2.3 索引 OpenClaw atoms | — |

兩套系統獨立運作，透過 `additional_atom_dirs` 橋接。

## 行動

- 新增 OpenClaw workspace atom 時：依人事時地物放入正確目錄
- 分類不準時：檢查 `taxonomy/unclassified.jsonl`，考慮擴充 categories.json
- 修改 categories.json 時：注意 atomPaths 映射，影響 A17 categoryAlignment
