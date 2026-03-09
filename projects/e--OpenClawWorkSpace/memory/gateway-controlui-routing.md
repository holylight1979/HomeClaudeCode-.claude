# Atom: Gateway controlUi 路由研究

- Scope: global
- Confidence: [固]
- Source: 2026-03-04 holylight — OpenClaw 2026.3.1 source code + GitHub issues + docs
- Last-used: 2026-03-06
- Confirmations: 4
- Trigger: controlUi 路由衝突、Dashboard Not Found、405、SPA catch-all、basePath、升級 2026.3.2、LINE webhook 404、controlUi basePath
- Privacy: public

## 知識

### 核心問題：controlUi SPA 攔截 LINE webhook

### HTTP Request 路由鏈（port 18789）

Gateway `handleRequest()` 處理順序（`dist/gateway-cli-tzSO700C.js` line 19045）：

1. Hooks (`handleHooksRequest`)
2. Tools invoke (`handleToolsInvokeHttpRequest`)
3. Slack (`handleSlackHttpRequest`)
4. OpenAI Responses / Chat Completions
5. Canvas Host
6. **Control UI** ← 問題在這裡
7. **Plugin HTTP Routes**（LINE webhook 在這裡）
8. Gateway Probe
9. 404 fallback

### 為什麼 controlUi 會擋 LINE webhook

controlUi handler (`handleControlUiHttpRequest`, line 16915) 只排除：
- `/plugins/*`
- `/api/*`

但 LINE webhook 路徑是 `/line/webhook`（不以 `/plugins/` 開頭），所以：
- POST `/line/webhook` → controlUi 攔截 → **405 Method Not Allowed**
- GET `/line/webhook` → controlUi 攔截 → 回傳 SPA index.html

### 2026.3.1 已知 bug（GitHub issue #31448）

> "Control UI 的 method guard 在 basePath exclusion 之前執行，SPA catch-all 攔截所有非 /plugins/ /api/ 的路徑"

### 2026.3.2 修復

- Plugin HTTP routes 現在在 Control UI SPA catch-all 之前執行
- POST 請求不再被 SPA catch-all 攔截
- npm: `openclaw@2026.3.2`（目前已發布穩定版）

## 2026.3.2 仍需 basePath（2026-03-04 實測）

即使升級到 2026.3.2，預設 `basePath: "/"` 仍會導致：
- `/health` GET 回 HTML（SPA catch-all）而非 JSON
- LINE webhook route 在 health-monitor stale-socket 重啟後 404（route 丟失）
- 設 `basePath: "/ui"` 後一切正常：`/health` 回 JSON、`/line/webhook` 正確 401（簽名驗證）

**結論**：`basePath: "/ui"` 不只是 2026.3.1 workaround，在 2026.3.2 也是必要設定。

## 解法選項

| 方案 | 做法 | 優缺 |
|------|------|------|
| **設 basePath（採用）** | `controlUi.basePath: "/ui"` | **必要**。即使 2026.3.2 也需要，Dashboard 從 `/ui` 存取 |
| **關閉 controlUi** | `controlUi.enabled: false` | 犧牲 Dashboard |

## controlUi 完整設定 schema

```json
"gateway": {
  "controlUi": {
    "enabled": true,           // 預設 true
    "basePath": "/",           // URL 前綴（設 "/ui" 可避免衝突）
    "root": null,              // 自訂 assets 路徑（一般不需要）
    "allowedOrigins": [],      // 非 loopback 時必填
    "allowInsecureAuth": false,
    "dangerouslyDisableDeviceAuth": false
  }
}
```

## controlUi assets 位置

`C:\Users\holyl\AppData\Roaming\npm\node_modules\openclaw\dist\control-ui\`

`resolveControlUiRootSync()` 搜尋順序：
1. `{execDir}/control-ui`
2. `{moduleDir}/control-ui` + parent paths
3. `{argv1Dir}/dist/control-ui`
4. `{packageRoot}/dist/control-ui`
5. `{cwd}/dist/control-ui`

## 參考連結

- [Dashboard Docs](https://docs.openclaw.ai/web/dashboard)
- [Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference)
- [Troubleshooting](https://docs.openclaw.ai/gateway/troubleshooting)
- [GitHub #31448: controlUi route priority bug](https://github.com/openclaw/openclaw/issues/31448)
- [GitHub #32435: controlUi breaks webhook POST routing](https://github.com/openclaw/openclaw/issues/32435)
- [GitHub #32584: LINE webhook returns 404](https://github.com/openclaw/openclaw/issues/32584)
- [GitHub #26478: LINE provider auto-restart loop](https://github.com/openclaw/openclaw/issues/26478)
- [GitHub #28622: Health monitor stale channel polling](https://github.com/openclaw/openclaw/issues/28622)
- [Webhook 405 Fix Blog](https://openclaw-setup.me/blog/usage-tips/openclaw-webhook-405-method-not-allowed-fix/)
- Source: `dist/gateway-cli-tzSO700C.js` lines 16915 (controlUi handler), 19045 (routing chain)
