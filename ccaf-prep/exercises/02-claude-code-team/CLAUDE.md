<!--
  EX2 — PROJECT memory file (D3.1).

  Hierarchy (most-shared at the bottom is loaded LAST, overriding the layers above it):
    1. user-level   ~/.claude/CLAUDE.md      -> YOUR machine only. NOT shared via VCS.
                                                Put personal style prefs here, never team rules.
    2. project      ./CLAUDE.md  (THIS FILE) -> committed, shared with every teammate.
                                                Root CLAUDE.md OR .claude/CLAUDE.md both work.
    3. directory    <subdir>/CLAUDE.md       -> loaded only when working inside that subtree.
                                                Good for one package's local conventions.

  Diagnose-this (guide 3.1): "a new teammate isn't getting the rules" almost always means the
  rules live in someone's USER-level file instead of here. Team rules MUST be project-scoped.
  Run /memory in Claude Code to see exactly which memory files are currently loaded.

  @import keeps this file modular: the line below pulls in team-conventions.md so this file
  stays a thin index instead of a monolith.
-->

# Project memory — CCAF EX2 (Claude Code team config)

This is a configuration-only exercise: a realistic shared `.claude/` setup for a team repo.

@import ./team-conventions.md

## Always-loaded standards (universal, vs. on-demand skills)

- Default model id is `claude-sonnet-4-6` (best speed/intelligence balance). The *most
  capable* model is `claude-opus-4-8`; pick Opus for the hardest reasoning, Sonnet otherwise.
- Prefer the built-in tools deliberately: **Grep** for content, **Glob** for paths,
  **Read/Write/Edit** for files (D2.5). Don't read whole trees up front.
- Topic rules that should load only for certain files live in `.claude/rules/` with `paths:`
  globs (D3.3) — not in a deeply-nested directory CLAUDE.md.

> CLAUDE.md = always loaded, universal. Skills (`.claude/skills/`) = invoked on demand for a
> specific workflow. Put standards here; put task workflows there.
