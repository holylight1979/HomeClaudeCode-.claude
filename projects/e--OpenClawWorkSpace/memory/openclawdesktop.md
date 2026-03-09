# Atom: OpenClawDesktop — 桌面自動化 MCP Server

- Scope: global
- Confidence: [觀]
- Source: 2026-02-28 holylight — 新建專案
- Last-used: 2026-03-05
- Confirmations: 4
- Trigger: 涉及桌面自動化 MCP、截圖、UI Automation、SendInput、DPI 問題、desktop automation、OpenClawDesktop
- Privacy: public

## 知識

- 專案路徑: `E:\OpenClawWorkSpace\OpenClawDesktop\`
- 技術: .NET 9.0 (`net9.0-windows10.0.19041.0`)、C# Console App
- MCP SDK: `ModelContextProtocol` 1.0.0 NuGet（官方 C# SDK）
- NuGet: ModelContextProtocol, Microsoft.Extensions.Hosting, System.Drawing.Common, Interop.UIAutomationClient
- 取代 3 個舊 MCP: computer-control-mcp (Python), MCPControl (Node), desktop-automation (Node)
- MCP 名稱: `desktop`（`.mcp.json` 裡的 key）
- DPI: `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` 啟動時設定
- 輸入: Win32 `SendInput` P/Invoke，`MOUSEEVENTF_ABSOLUTE` 正規化座標
- 截圖: Win32 `BitBlt` (GDI)，支援全螢幕/區域，預設 JPEG q90 + maxWidth 1280 自動縮放（避免 context limit 截斷）
- OCR: WinRT `Windows.Media.Ocr`（內建，不需外部 binary）
- UI Automation: `Interop.UIAutomationClient` NuGet（namespace: `Interop.UIAutomationClient`，不是 `UIAutomationClient`）
- Tool 回傳圖片: `IEnumerable<AIContent>` + `DataContent("data:image/png;base64,...")`
- Tool 註冊: `[McpServerToolType]` 類 + `[McpServerTool]` 方法 + DI 參數注入
- 剪貼簿: 需跑在 STA thread（`ClipboardService` 內部自建 STA thread）
- Publish: `dotnet publish -c Release -r win-x64 --self-contained false` → 30MB 單一 exe

## 工具清單（26 個）

| 分類 | 工具 |
|------|------|
| 螢幕 | screenshot, screenshot_with_ocr |
| 滑鼠 | mouse_move, mouse_click, mouse_drag, mouse_scroll, get_cursor_position |
| 鍵盤 | key_press, key_type, key_hold |
| 視窗 | list_windows, get_active_window, focus_window, resize_window, move_window, minimize_window, restore_window |
| UI 自動化 | get_ui_tree, find_element, click_element, get_element_value, set_element_value |
| 剪貼簿 | get_clipboard, set_clipboard |
| 工具 | get_screen_size, wait |

## 實作進度

- [x] Phase 1: 基礎建設
- [x] Phase 2: 輸入與截圖
- [x] Phase 3: 視窗管理
- [x] Phase 4: UI Automation
- [x] Phase 5: OCR 與剪貼簿
- [x] Phase 6: 收尾與部署

## 行動

- 修改 OpenClawDesktop 時，先確認 NativeStructs / P/Invoke 宣告是否齊全
- Interop.UIAutomationClient namespace 是 `Interop.UIAutomationClient`（帶 Interop 前綴）
- 部署: `.mcp.json` 用 `dotnet run --project ... -c Release`
- logging 必須走 stderr（stdout 是 MCP JSON-RPC 通道）
- 啟用需重啟 Claude Code session
- **運作流 SOP** → 見 `desktop-workflow.md`（位置快取、監測迴圈、優化策略）
- Electron 程式（VS Code）的 UI Automation tree 看不到內部元素 → 用 screenshot+OCR
- Claude Code 輸入框用 `Ctrl+Escape` 聚焦比 mouse_click 更可靠

## 演化日誌

- 2026-02-28 [臨→觀] 新建專案，全 6 Phase 完成，26 工具，0 error 0 warning
- 2026-03-03 screenshot 預設 JPEG q90 + maxWidth 1280 自動縮放 + ReencodeImage；解決 output_exceeded_context_limit
