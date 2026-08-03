# CCAF Study Plan (English)

Plan for the **Claude Certified Architect – Foundations** exam.
Supersedes `../Mi_Plan_Estudio_CCAF.md` (kept for reference). Read order:
1. [`ANALYSIS.md`](./ANALYSIS.md) — scope, what to skip, decisions.
2. [`MAPPING.md`](./MAPPING.md) — the abstract→concrete index (use constantly).
3. This file — the schedule.

## Starting point
- ✅ Courses done: Building with the Claude API (D4), Claude Code in Action (D3),
  Intro to MCP (D2), Intro to Agent Skills (D3).
- ✅ Boilerplate built: `claude-with-anthropic-api/{cli_project, queries, app_starter}`.
- ✅ Read exam guide scenarios (p.1–4), skimmed rest.
- ⏳ Skilljar: Practice Exam (pending), real exam (pending).

## Exam facts (memorize)
- 60 questions, 120 min, 4 of 6 scenarios chosen at random.
- Pass = **720/1000** scaled. No penalty for guessing → **never leave blanks**.
- **Mix of multiple-choice and multiple-response** — each item states how many to select. No partial
  credit on Select-2 (need all correct, no extras). Delivered via **Pearson VUE** (not Skilljar).
- Weights: **D1 27% · D3 20% · D4 20% · D2 18% · D5 15%**.
- Retake waits 14 / 30 / 90 days, up to 4 attempts / rolling 12 mo. See `../CERT_ROADMAP.md`.

---

## Phase A — Learn each task statement through the notebooks (2–4 days)
Don't re-read the guide linearly. Work through the **per-domain notebooks in
`notebooks/`** — each task statement gets: the verbatim guide quote, a plain-English
unpacking, a **runnable** cell that makes the concept observable, the anti-pattern as
code, and a pointer to the matching line in your own course code. Run every code cell.
- Read order by weight: D1 → D3 → D4 → D2 → D5.
- Keep `MAPPING.md` open as the index; the notebook is where you actually learn.
- Do the **12 sample questions** actively: cover the answer, write why each of the 3
  distractors is wrong, then reveal. (Highest-value hour of Phase A.)
- Read the **In-Scope / Out-of-Scope appendix**. Cross off your RAG/embeddings notebooks.

Notebook status: `D1_agentic_loops.ipynb` ✅ all of §1.1–1.7 done. D2–D5 pending.
Exercise folders: all five built — `exercises/01-support-agent/` … `exercises/05-cicd-review/`.

## Phase B — Pair-build, minimal + anti-pattern (core, ~5–8 days) ⭐
For each exercise: I scaffold the **correct** version *and* the **anti-pattern**; you
run both, watch the anti-pattern fail, then do **20–30 bank questions** for that
exercise's domains. If you miss a pattern → back to the exercise before advancing.

| # | Exercise (folder) | Domains | Lights up | Bank Qs after |
|---|---|---|---|---|
| 1 | `exercises/01-support-agent/` | D1+D2+D5 | S1 | D1+D2 |
| 2 | `exercises/02-claude-code-team/` | D3+D2 | S2, S4 | D3 |
| 3 | `exercises/03-extraction-pipeline/` | D4+D5 | S6 | D4 |
| 4 | `exercises/04-multi-agent-research/` | D1+D2+D5 | S3 | D1+D5 |
| 5 | `exercises/05-cicd-review/` | D3+D4 | S5 | D3 |

Build order = exam weight: **1 → 4 → (3 ∥ 5) → 2**. (D1 first and most; Ex4 cements
the Agent SDK vocabulary — `Task`, `allowedTools`, `fork_session`.)

Each exercise folder has a `README.md` with: the build steps, the **task-statement
tags** on each part, how to run, and the **anti-pattern experiments** to try.

## Phase C — Validation (2–3 days)
1. `notebooks/practice_exam_A.ipynb` — our **33-question, all-6-scenario simulacrum** (single-answer
   + Select-2), under real conditions: timed, no notes, no extra material. (Replaces the retired
   Skilljar practice exam.)
2. For every miss: find the Task Statement in `MAPPING.md`, re-read it, note which
   distractor pattern fooled you (each answer's `Tag:` line names it).
3. Time permitting: 100–150 bank questions for distractor-recognition reps.

## Phase D — Day before
Light review of the **5 distractor patterns only** (see `ANALYSIS.md`). Rest. Nothing new.

## Phase E — Right after you pass (days, not months)
Do **not** let the material go cold before starting the next credential. Re-reviewing
already-studied domains after a ~2-month gap cost several hours across several days on this
exam — the single most avoidable expense in the whole kit. Within days of passing, run the
**delta-first** workflow in [`CERT_ROADMAP.md`](./CERT_ROADMAP.md): drop the new exam guide into
`reference/`, gap-analyse its task statements against the existing D1–D5 notebooks
(covered / partial / new), and build only the **new** rows. Freshness is the asset, and it is
perishable.

---

## Day-of rules
- No notes / second monitor. Assume strict proctoring (camera + screen share); confirm the exact
  rules in the **Pearson VUE** confirmation email (the exams moved off Skilljar in July 2026).
- No guess penalty — and the platform **requires an answer before it lets you advance**, so you
  cannot leave one blank and circle back. Lock a best guess first, *then* mark for review.

## Resources
- `reference/exam_guide.txt` — full guide text (extracted from the PDF; **v1.0 · Effective July 2026 · CCAR-F**).
- `reference/course_catalog.txt` — Academy catalog.
- The official PDF is the authoritative source: **v1.0 · Effective July 2026 · exam code CCAR-F**
  (content unchanged vs v0.1 Feb 2025 — v1.0 only added multi-response items + logistics).
- docs.anthropic.com — Agent SDK / Claude Code / MCP / Claude API reference.
- 618-question bank + third-party sites — secondary recognition practice only.
