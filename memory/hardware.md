# 硬體配置與升級取向

- Scope: global
- Confidence: [固]
- Trigger: 硬體, 電腦, 升級, hardware, PC, GPU, CPU, 顯卡, 記憶體, RAM, 主機板
- Last-used: 2026-08-15
- Confirmations: 40

- Related: ryujinx-cheats

## 知識

### 現有配置（2026-03）

- CPU: Intel i7-3770 (4C/8T, LGA 1155, 2012)
- 主板: ASUS BM6875 (B75 晶片組，商用私規機殼)
- RAM: 16GB DDR3-1600 (8+4+4GB, Kingston/Samsung 混插)
- GPU: NVIDIA GeForce GTX 1650 4GB
- 儲存: Crucial MX500 1TB SSD + BX500 1TB SSD + WD 1TB HDD
- PSU: 350W (商用機)
- OS: Windows 10 Pro (OEM)
- 限制: 機殼私規（無法裝標準 mATX）、PSU 缺 PCIe 供電、無 NVMe、CPU 不支援 AVX2（LanceDB 仍可用但無 SIMD 加速）

### 升級取向（使用者確認的方向）

- 用途: AI 開發 + Ollama 本地 LLM 推論 + 遊戲 + 一般工作
- 核心要求: **近幾年內不會被淘汰**
- 平台選擇: AM5 (B650 + DDR5)，因 AMD 承諾支援到 2027+，未來可升 Zen 5/6
- GPU 傾向: 大 VRAM 單卡優先（多 GPU 在消費端不實際）
- 推薦方案: Ryzen 5 7600 + B650M + DDR5-5600 32GB + RTX 4060 Ti 16GB (~NT$44,000-50,000)
- 必換: PSU (650W+)、機殼 (私規→標準 mATX)、NVMe SSD
- 可沿用: 2x SATA SSD + HDD + 螢幕周邊

### Ollama VRAM 對照（qwen3 Q4_K_M）

- 0.6B: 2.2GB | 4B: 5.2GB | 8B: 7.5GB | 14B: 12GB | 32B: 25GB
- 16GB VRAM 可舒適跑 14B；24GB+ 才能跑 32B

### 多 GPU/CPU 分析結論

- Ollama 多 GPU: 可合併 VRAM 但效能不成比例（Pipeline Parallelism，序列式）
- NVLink: RTX 3090 是最後一代消費卡支援，4090/5090 已移除
- 多 CPU: 消費者市場無雙 socket，Threadripper PRO 成本過高
- Mac Studio M3/M4 Ultra 96GB 是替代路線（統一記憶體跑大模型）

### 升級後可解鎖的軟體升級

- **Ollama 本地模型升級**: 現有 GTX 1650 4GB 只能跑 qwen3 0.6B embedding；升級 16GB+ VRAM 後可跑 qwen3 14B 作為本地推論主力，大幅提升 hook 語意處理品質
- **Vector DB 升級**: 現用 LanceDB（ChromaDB 已棄用）；AM5 Zen 4 支援 AVX-512，LanceDB SIMD 加速更完整
- **記憶系統本地 LLM 升級**: 目前 hook 用 qwen3:1.7b 做語意處理；VRAM 夠大後可升級到 qwen3:8b 或 14b，意圖分類和知識萃取品質會顯著提升

## 行動

- 討論硬體/升級時，載入此 atom 作為基準，不需重新收集系統資訊
- 升級完成後更新此 atom（新配置取代舊配置）
- 升級完成後評估：ChromaDB → LanceDB、Ollama 本地模型升級路徑

## 演化日誌

- 2026-03-05: 初建。完整分析現有配置 + 5 個 Tier 升級方案。使用者確認方向：AM5 + 大 VRAM 單卡。
