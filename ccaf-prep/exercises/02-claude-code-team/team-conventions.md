# Team conventions (imported by CLAUDE.md via @import)

Splitting these out keeps `CLAUDE.md` a thin index. A package maintainer can `@import` only
the standards relevant to their package instead of inheriting one monolithic file.

- Conventional Commits for messages (`feat:`, `fix:`, `chore:`).
- Use parameterized queries — never string-interpolate SQL.
- Public functions need a one-line docstring; keep diffs minimal and reviewable.
- Run the test suite before opening a PR.
