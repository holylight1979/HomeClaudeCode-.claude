// ════════════════════════════════════════════════════════════════════
//  world-chat.js — 腦內世界「生物 LLM 對話」代理（被 server.js require，
//                  同進程生命週期：server.js 啟動它就在、關閉它就沒）。
//
//  職責：把瀏覽器(world.html)的對話請求轉發到 Ollama 原生 /api/chat。
//        backend 選擇與認證留在此端（單一來源、不外洩 token）；
//        model / prompt / options 由前端帶（免重啟即可調整對話風格）。
//
//  backend 取 config.vector_search.ollama_backends 中「已啟用且 priority 最小」者
//  ——各機環境不同（有 GPU 機的走遠端、無的走 local），選擇由 config 決定而非寫死。
//
//  零外部依賴，只用 Node 內建 http/https；server.js 內部 helper 透過 ctx 注入，
//  故本模組與 server.js 其餘程式解耦（只依賴 ctx 介面）。
// ════════════════════════════════════════════════════════════════════
"use strict";
const http = require("http");
const https = require("https");

const UPSTREAM_TIMEOUT_MS = 30000;       // 大模型暖機可能久，給足；前端另有自己的逾時+fallback
const MAX_BODY = 100 * 1024;             // 100KB 上限，防爆

/**
 * 從 config 挑對話用 backend：已啟用（enabled 未標視為啟用）且有 base_url 者中，
 * priority 數字最小的優先。無可用者回 null。
 */
function pickBackend(cfg) {
  const all = (cfg && cfg.vector_search && cfg.vector_search.ollama_backends) || {};
  const usable = Object.keys(all)
    .map((name) => ({ name, b: all[name] }))
    .filter((x) => x.b && x.b.base_url && x.b.enabled !== false)
    .sort((x, y) => (x.b.priority == null ? 99 : x.b.priority) - (y.b.priority == null ? 99 : y.b.priority));
  return usable.length ? usable[0] : null;
}

/**
 * 處理 POST /api/creature-chat。
 * @param req,res  Node http req/res
 * @param ctx      { loadConfig, jsonRes, WORKFLOW_DIR, fs, path }（由 server.js 注入）
 *
 * 前端 body：{ model, messages:[{role,content}...], options?, think? }
 * 回傳：{ content, eval_count, total_ms, model, backend } 或 { error }
 *
 * 前端指定的 model 若後端沒載入（Ollama 回 404 model not found），自動改用該 backend
 * 設定的 llm_model 重送一次——同一份 world.html 在不同機器（模型清單各異）都能對話，
 * 而非永遠退罐頭台詞。
 */
function handleCreatureChat(req, res, ctx) {
  let body = "";
  let aborted = false;
  req.on("data", (c) => {
    body += c;
    if (body.length > MAX_BODY) { aborted = true; ctx.jsonRes(res, 413, { error: "body too large" }); req.destroy(); }
  });
  req.on("end", () => {
    if (aborted) return;
    let payload;
    try { payload = JSON.parse(body || "{}"); } catch { return ctx.jsonRes(res, 400, { error: "bad json" }); }
    if (!Array.isArray(payload.messages) || !payload.messages.length) {
      return ctx.jsonRes(res, 400, { error: "messages[] required" });
    }

    const cfg = ctx.loadConfig();
    const picked = pickBackend(cfg);
    if (!picked) return ctx.jsonRes(res, 503, { error: "no enabled ollama backend with base_url in config" });
    const b = picked.b;

    // 認證：原生 Ollama API 通常免 token；僅在 backend 標 auth 時帶 Bearer
    let token = null;
    if (b.auth) {
      try { token = JSON.parse(ctx.fs.readFileSync(ctx.path.join(ctx.WORKFLOW_DIR, ".rdchat_token.json"), "utf-8")).token; } catch {}
    }

    const url = new URL(b.base_url.replace(/\/+$/, "") + "/api/chat");
    const isHttps = url.protocol === "https:";
    const mod = isHttps ? https : http;

    const send = (model, allowFallback) => {
      const upstreamBody = Buffer.from(JSON.stringify({
        model,
        messages: payload.messages,
        stream: false,
        think: payload.think === true,                  // 預設 false（casual 台詞不需 thinking → 快）
        options: payload.options || { num_predict: 64, temperature: 0.9 },
      }));

      const headers = { "Content-Type": "application/json", "Content-Length": upstreamBody.length };
      if (token) headers["Authorization"] = "Bearer " + token;

      const up = mod.request({
        hostname: url.hostname,
        port: url.port || (isHttps ? 443 : 80),
        path: url.pathname,
        method: "POST",
        headers,
        timeout: UPSTREAM_TIMEOUT_MS,
        rejectUnauthorized: false,
      }, (ur) => {
        let buf = "";
        ur.on("data", (d) => (buf += d));
        ur.on("end", () => {
          // 模型不在該 backend → 退回 config 的 llm_model 重送一次（只重試一次，防迴圈）
          if (ur.statusCode === 404 && allowFallback && b.llm_model && b.llm_model !== model) {
            return send(b.llm_model, false);
          }
          if (ur.statusCode !== 200) {
            return ctx.jsonRes(res, 502, { error: "upstream " + ur.statusCode, backend: picked.name, model, detail: buf.slice(0, 300) });
          }
          let j;
          try { j = JSON.parse(buf); } catch { return ctx.jsonRes(res, 502, { error: "upstream bad json" }); }
          ctx.jsonRes(res, 200, {
            content: (j.message && j.message.content) || "",
            eval_count: j.eval_count != null ? j.eval_count : null,
            total_ms: j.total_duration ? Math.round(j.total_duration / 1e6) : null,
            model,                                      // 實際生成用的模型（可能是 fallback 後的）
            backend: picked.name,
          });
        });
      });
      up.on("error", (e) => ctx.jsonRes(res, 502, { error: "upstream error: " + e.message, backend: picked.name }));
      up.on("timeout", () => { up.destroy(); ctx.jsonRes(res, 504, { error: "upstream timeout", backend: picked.name }); });
      up.write(upstreamBody);
      up.end();
    };

    send(payload.model || b.llm_model, true);
  });
  req.on("error", () => { if (!aborted) ctx.jsonRes(res, 400, { error: "request error" }); });
}

module.exports = { handleCreatureChat, pickBackend };
