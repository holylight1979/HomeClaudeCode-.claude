# MUD GM Project Memory

## Project Overview
- C MUD server (Merc derivative, Big5/Traditional Chinese) being ported to C#
- Original source: `SRC/` directory (C files, Big5 encoded)
- C# port: `MUD-Arion-CSharp/MudGM/Src/` directory (UTF-8)
- Tracking progress via `MUD-Arion-CSharp/TODO.md`

## Key Architecture Notes
- C# uses partial classes: `CommModule` (COMM.C.cs + CommHelpers.cs + NetCore.cs), `DbModule` (DB.C.cs + DB.C.Extra.cs + DB.C.GM.cs)
- Function pointers (spec_fun, spell_fun, attack_fun) stored as string names in C# - needs runtime dispatch
- Types split across: MercTypes.cs, MercStubs.cs, MercConstants.cs, DbStubs.cs
- MERC.H.cs, MERC.cs, MERC2.cs are all stubs (empty TODO comments)

## Full Verification v3 (2026-02-18) — ALL 24 files verified from scratch
- See `MUD-Arion-CSharp/VERIFICATION-REPORT.md` (third edition)
- **0 FATAL**, **4 CRITICAL** (all fixed), **33 MEDIUM** (2 fixed, 31 noted), **25+ LOW**
- All 23 C source files + MERC.H fully re-verified function-by-function (~780+ functions)
- `dotnet build` passes: 0 errors 0 warnings
- CRITICAL fixes: issetplr bit semantics, stop_fighting update_pos, CheckChild ACT_BORN_CHILD, DoSocihouse save_char_obj
- MEDIUM fixes: do_slookup Format args, CONST.C placeholder skill_level
- Prior F3-F13 and C1-C13 issues all resolved (fixed/non-bug/confirmed)
- HANDLER.C stop_fighting missing update_pos was **NEW discovery** (not in any prior report)
- FightModule.update_pos changed from private to internal (for HandlerModule access)

## Encoding
- Original uses Big5 encoding for Chinese text — MUST use `cp950` (not `big5`) codec in Python
- `\xF9xx` range (e.g. 裏 U+88CF = \xF9\xD8) only decodable with cp950
- C# uses Encoding.GetEncoding(950) for network I/O
- Big5 tilde (0x7E as second byte) protection missing in fread_string

## CStr 字串集中化 (Completed 2026-02-13)
- All Chinese strings centralized in `MUD-Arion-CSharp/MudGM/Src/CStr.cs`
- 4,198 CStr references across 15 source files, 0 remaining hardcoded Chinese
- Tools in `.claude/tools/`: `big5_extract.py`, `cstr_add_missing.py`, `cstr_replacer.py`
- See `.claude/tools/README.md` for workflow docs
- CLAUDE.md updated with tool instructions for new file porting
