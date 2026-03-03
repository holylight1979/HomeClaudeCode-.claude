# Gateway controlUi 路由研究 (2026-03-04)

> Scope: OpenClaw Gateway Dashboard + LINE webhook 路由衝突
> Source: OpenClaw 2026.3.1 source code + GitHub issues + docs

## 核心問題：controlUi SPA 攔截 LINE webhook

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

## 解法選項

| 方案 | 做法 | 優缺 |
|------|------|------|
| **升級 2026.3.2** | `npm i -g openclaw@2026.3.2` | 最佳解，根本修復路由順序 |
| **設 basePath** | `controlUi.basePath: "/ui"` | 2026.3.1 可用的 workaround，Dashboard 改從 `/ui` 存取 |
| **關閉 controlUi** | `controlUi.enabled: false` | 犧牲 Dashboard（目前的狀態） |

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
- [Webhook 405 Fix Blog](https://openclaw-setup.me/blog/usage-tips/openclaw-webhook-405-method-not-allowed-fix/)
- Source: `dist/gateway-cli-tzSO700C.js` lines 16915 (controlUi handler), 19045 (routing chain)
