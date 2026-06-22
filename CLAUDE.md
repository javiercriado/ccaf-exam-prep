# CLAUDE.md

## What this is
A personal **CCAF (Claude Certified Architect – Foundations)** exam-prep kit, plus the official
Anthropic Academy course code it builds on. Notebooks teach each exam concept by making **real
Claude API calls** (Messages API or Claude Agent SDK), mapped 1:1 to the official exam guide.

## Layout
- **`ccaf-prep/`** — the study kit (a self-contained `uv` project):
  - `notebooks/` — one notebook per domain (`D1_…`–`D5_…`) + `mock_exam_and_review.ipynb`.
    `notebooks/README.md` = study order. Each domain: one section per task statement.
  - `exercises/01-support-agent/ … 05-cicd-review/` — five cross-domain runnable builds; each has its own README.
  - `MAPPING.md` — abstract task statement → concrete `file:line` → sample question (the index).
  - `STUDY_PLAN.md` — full schedule + rationale. `reference/` — where the user drops `exam_guide.txt` (git-ignored).
- **`claude-with-anthropic-api/`** — official Anthropic course notebooks/exercises (prerequisite; notebooks cite it).
- **`.claude/skills/ccaf-notebook/SKILL.md`** — the notebook authoring standard (see Conventions).

## Setup & run
- Install: `cd ccaf-prep && uv sync` (creates `ccaf-prep/.venv`, native arm64).
- **Run via `uv run python …` from `ccaf-prep/`** — bare `python3` lacks `anthropic`/`claude_agent_sdk`.
  Exercises: `cd ccaf-prep/exercises/01-support-agent && uv run python agent.py`.
- One `.env` at the **repo root** (`/Users/javier/Code/anthropic-courses/.env`), auto-discovered via `find_dotenv`. Needs `ANTHROPIC_API_KEY`.
- Model **defaults to `claude-haiku-4-5`** (cheapest — cost is deliberate); override anywhere with `CLAUDE_MODEL` in `.env`.
- Notebook outputs are git-stripped: enable once per clone — `cd ccaf-prep && uv run nbstripout --install --attributes ../.gitattributes`.

## Conventions
- **Language: all repo content is English** — the *single* exception is `README.es.md` (root), the Spanish
  translation of `README.md`; keep the EN/ES pair in sync when either changes. No other file is authored in
  Spanish; translate any Spanish gloss to English. (User-facing chat replies follow the user's language.)
- **Teach the mechanism for real.** When a section's lesson is a Claude decision, it must make a real model
  call — never a Python `if`/`switch` standing in for Claude. Deterministic fixtures *behind* tools are fine.
- **Never `permission_mode="bypassPermissions"`** — use `"default"` + explicit `allowed_tools`.
- **Keep calls cheap**: Haiku, small `max_tokens`, tiny toy fixtures, one call per concept.
- Full authoring standard (6-part section anatomy, verbatim-quote rule, verify-before-done): **`.claude/skills/ccaf-notebook/SKILL.md`** — don't duplicate it here.
- **Practice-exam clarifications → two tiers, kept apart.** When a tricky exam question yields a lesson, split it:
  - **Shareable *concept*** (the principle/mechanism, **no answer keys**) → tracked repo. Placement rule:
    explains a *specific exercise's behavior* → that exercise's folder (e.g.
    `exercises/01-support-agent/PARALLEL_TOOL_USE.md`); a *general pattern* not tied to an exercise →
    `ccaf-prep/` root (e.g. `SELF_CRITIQUE.md`); a *short discriminator* → inline in `DISTRACTOR_HEURISTIC.md`.
  - **Private *worked example*** (verbatim exam question + the user's answer + screenshot ref) →
    git-ignored `personal/` **only** — exam content is not redistributed. Screenshots live in git-ignored
    `archive/screenshots/`.
  - **Index:** the *Concept deep-dives* table in `DISTRACTOR_HEURISTIC.md` is the front door — register every
    new shareable concept doc there (sorted by domain). Don't consolidate into one big file or file per domain.

## Status (verify against `README.md`'s table before relying)
- Notebooks: **D1 ✅, D2 ✅, D5 ✅** hand-validated; **D3 🧪** built/generated, not yet hand-reviewed; **D4 ⏳** not built.
- Exercises: **01 ✅ hand-reviewed**; **02–05 🧪 built and runnable, not yet hand-reviewed**.
- Study/build order is dependency-driven: **D1 → D2 → D5 → D3 → D4**.
