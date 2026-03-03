# Atom Index — 識流專案

## 高頻事實

- 專案路徑: `E:\AI-Develop\consciousness-stream`
- 語言: TypeScript (ES2022, Node16 module)
- Runtime deps: @modelcontextprotocol/sdk, zod; devDeps: typescript, @types/node
- 架構: 九層管線引擎 (佛教八識 → AI Agent 處理管線)
- LLM 呼叫: full 模式 2 次, simplified 模式 1 次（Token 優化後）
- sparsa: 規則匹配（無 LLM）, mano+klista: 合併 1 次 LLM, paravtti+prabhsvara+kriya: 合併 1 次 LLM
- alaya/vasana: 純自動（無 LLM）
- 主入口: `src/pipeline.ts` → `runPipeline(input, config)`
- CLI: `src/cli.ts` → `consciousness-stream "任務"` (AnthropicLlm, --mode/--memory-root/--model)
- MCP: `src/mcp.ts` → stdio transport, tools: consciousness_stream + list_atoms
- Perception: `src/perception.ts` → FilePerceptionAdapter (CLI/MCP 共用)
- Skill: `~/.claude/commands/consciousness-stream.md` (5-step 結構化 prompt)
- 測試: 25 cases (pipeline 9 + cli 9 + mcp 7)
- 關聯專案: OpenClaw (`E:\OpenClawWorkSpace`)

## 開發進度

- [x] Phase 1: 核心管線引擎 (TypeScript Library) — 2026-03-01 完成
- [x] Phase 2: 增強 Claude Code Skill + CLI — 2026-03-01 完成
- [x] Phase 3: MCP Server — 2026-03-01 完成
- [x] Phase 4: OpenClaw 整合 — 2026-03-01 完成（keyword-only trigger）

## Atom 檔案表

| 檔案 | Trigger |
|------|---------|
| (待建立) | |
