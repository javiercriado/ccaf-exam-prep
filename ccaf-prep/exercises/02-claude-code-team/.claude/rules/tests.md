---
# D3.3 — path-specific rule. This file loads ONLY when Claude edits a matching file,
# so the convention rides with the file TYPE regardless of which directory it sits in.
# That is the advantage over a subdirectory CLAUDE.md: test files are spread everywhere.
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/tests/**"
---

When editing tests: one behavior per test, name it `describe(unit) > it(should ...)`, assert on observable output (not internals), and never add a network or real-DB call — use the project fixtures.
