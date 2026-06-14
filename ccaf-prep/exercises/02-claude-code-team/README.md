# Exercise 2 — Claude Code Team Configuration

**Lights up:** Scenario 2 (Dev Team), Scenario 4 (Platform). **Sample questions:** 4, 5, 6.
**Domains:** D3 (CLAUDE.md hierarchy, commands/skills, path rules, plan-vs-direct),
D2 (`.mcp.json`, built-in tools), D1.7 (sessions).

> This is a **configuration** exercise — the "code" is the set of `.claude/` files, not a
> Python script. The runnable part is the **commands to try** in a real Claude Code session.

## What's here
| File | Task Statement |
|---|---|
| `CLAUDE.md` | **D3.1** project memory + the user/project/directory **hierarchy** + `@import` |
| `team-conventions.md` | **D3.1** the `@import`ed module (keeps `CLAUDE.md` a thin index) |
| `.claude/rules/tests.md` | **D3.3** path-specific rule with `paths:` globs (loads only on matching files) |
| `.claude/commands/review-pr.md` | **D3.2** project-scoped slash command (`/review-pr`) |
| `.claude/skills/changelog/SKILL.md` | **D3.2** skill with `allowed-tools` + `context: fork` |
| `.mcp.json` | **D2.4** project-scoped MCP servers with `${ENV}` expansion (no secrets committed) |

## What maps to what (read each file's header comment)

| Concept | Where | The exam point |
|---|---|---|
| **D3.1** CLAUDE.md hierarchy | `CLAUDE.md` comment | user (`~/.claude/`, **not** VCS) vs project (committed) vs directory; `@import` for modularity |
| **D3.2** commands vs skills | `.claude/commands/`, `.claude/skills/` | `.claude/commands/` (project, VCS) vs `~/.claude/commands/` (personal). SKILL.md frontmatter (`allowed-tools`, `context: fork`) |
| **D3.3** path rules | `.claude/rules/tests.md` | `paths:` globs load a rule by **file type**, wherever those files live |
| **D2.4** MCP config | `.mcp.json` | project `.mcp.json` vs user `~/.claude.json`; `${ENV}` expansion; servers as `command`+`args` |
| **D2.5** built-in tools | `CLAUDE.md` body | **Grep**=content, **Glob**=paths, **Read/Write/Edit**; `Edit` fails on a non-unique match → fall back to Read+Write |
| **D3.4** plan vs direct | this README ↓ | large/architectural/multi-approach → **plan**; single well-scoped change → **direct** |
| **D1.7** sessions | this README ↓ | `--resume <name>`, `fork_session`, fresh+summary when results are stale |

## Commands to actually try (the "runnable" part)

```bash
# 1. D3.2 — run the project slash command (defined in .claude/commands/review-pr.md):
#    in a Claude Code session opened in a repo that has this .claude/ folder:
/review-pr                 # or:  /review-pr develop
/memory                    # D3.1 — see exactly which CLAUDE.md files are loaded right now

# 2. D1.7 — sessions:
claude --resume my-investigation     # continue a NAMED prior session
#   fork_session (Agent SDK) -> branch from a shared baseline to try A vs B independently

# 3. D2.4 — MCP: with this .mcp.json present, Claude Code offers the 'docs' + 'github' servers.
#    The GitHub token is read from $GITHUB_TOKEN at launch — it is NOT in the file.
```

**D3.4 — plan mode vs direct (sample Q5).** Use **plan mode** when the task is large,
architectural, or has multiple viable approaches (e.g. "split this monolith into
microservices") — you want a reviewed plan before edits, and an Explore subagent to map the
code first. Use **direct** for a single, well-scoped change ("rename this function, fix this
test"). Don't start direct and "switch if it gets complex" — that's the distractor.

## Anti-pattern experiments / distractors (the real learning)

1. **Team rules in the USER file (D3.1).** A teammate "isn't getting the conventions."
   Tempting fix: add them to `~/.claude/CLAUDE.md`. **Wrong** — user-level is per-machine and
   never shared via VCS. Team rules belong in the **project** `CLAUDE.md` (this file).
2. **`.claude/config.json` array for commands (D3.2, Q4).** The distractor invents a config
   array. **Wrong** — a slash command is a markdown file in **`.claude/commands/`**.
3. **Subdir CLAUDE.md for spread-out files (D3.3, Q6).** Test files live all over the tree, so
   a single directory `CLAUDE.md` can't cover them. **Wrong** approach — use a
   **`.claude/rules/`** file with `paths:` globs (see `tests.md`), which loads by file type.
4. **Direct-then-switch for architecture (D3.4, Q5).** Picking direct mode for a
   monolith→microservices migration and planning to switch later. **Wrong** — choose **plan
   mode up front** for architectural, multi-approach work.
5. **Secrets in `.mcp.json` (D2.4).** Hardcoding the GitHub token. **Wrong** — use `${ENV}`
   expansion; never commit secrets.

## After this exercise
Do **20–30 bank questions on D3** (+ a few D2.4/2.5). If a config distractor fools you, come
back and re-read the matching file's header comment before moving on.
