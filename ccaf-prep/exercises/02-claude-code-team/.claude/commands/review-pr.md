---
description: Review the current branch diff against team conventions and post a findings summary.
argument-hint: "[base-branch]  (defaults to main)"
allowed-tools: Bash(git diff:*), Bash(git log:*), Read, Grep, Glob
---

# /review-pr — project-scoped slash command (D3.2, sample Q4)

This command lives in `.claude/commands/` so it is COMMITTED and shared with the whole team
via version control. (A personal-only variant would go in `~/.claude/commands/` instead.)
Invoke it with `/review-pr` (optionally `/review-pr develop`).

Review the diff of the current branch against `$ARGUMENTS` (default `main`):

1. `git diff $ARGUMENTS...HEAD` to get the changes.
2. Check each changed file against `CLAUDE.md` + `team-conventions.md` (and any matching
   `.claude/rules/` rule, e.g. test conventions for `*.test.*`).
3. Report findings grouped by severity (blocker / nit), each with `file:line` and a fix.
4. Be specific and conservative — flag real issues, not style opinions already covered by lint.
