# Team conventions (pulled into CLAUDE.md via the `@team-conventions.md` import)

Splitting these out keeps `CLAUDE.md` a thin index. A package maintainer can `@`-import only
the standards relevant to their package instead of inheriting one monolithic file. (The
directive is a bare `@path` — `@team-conventions.md` — not `@import team-conventions.md`.)

- Conventional Commits for messages (`feat:`, `fix:`, `chore:`).
- Use parameterized queries — never string-interpolate SQL.
- Public functions need a one-line docstring; keep diffs minimal and reviewable.
- Run the test suite before opening a PR.
