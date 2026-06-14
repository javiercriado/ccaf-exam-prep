---
name: changelog
description: Generate or update CHANGELOG.md from the commits since the last release tag. Use when the user asks to "update the changelog", "write release notes", or cut a release. Produces verbose git output, so it runs in a forked context to keep the main session clean.
allowed-tools: Bash(git log:*), Bash(git tag:*), Read, Edit, Write
argument-hint: "[next-version]  e.g. 1.4.0"
context: fork
---

# changelog skill (D3.2)

Project-scoped skill (shared via VCS because it lives in `.claude/skills/`). A personal variant
would go in `~/.claude/skills/` under a *different* name so it doesn't shadow this one for teammates.

Frontmatter doing the work here:
- `allowed-tools` — restricts this skill to git reads + file writes. It CANNOT run destructive
  shell commands, even though the main session might be allowed to (least privilege, D2.3-style).
- `context: fork` — runs in an isolated sub-agent. The noisy `git log` walk and draft iterations
  stay out of the main conversation; only the final CHANGELOG summary returns.
- `argument-hint` — prompts the developer for the target version if they invoke with no args.

## Steps
1. `git describe --tags --abbrev=0` to find the last release tag.
2. `git log <tag>..HEAD --pretty=...` to collect commits.
3. Group by Conventional-Commit type (Features / Fixes / Chores) under a `## $ARGUMENTS` heading.
4. Edit `CHANGELOG.md` (prepend the new section). Return only the rendered section to the caller.
