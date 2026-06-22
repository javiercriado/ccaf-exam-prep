---
description: Turn a tricky CCAF practice-exam question into a shareable concept doc + a private worked-example, following the CLAUDE.md two-tier convention.
argument-hint: <screenshot-path-or-question-text> (my answer: X)
---

You are capturing the lesson from a CCAF practice-exam question the user found tricky.
Follow the **Practice-exam clarifications** convention in `CLAUDE.md` (two tiers kept apart:
shareable *concept* vs private *worked-example*) and register outputs in the
`ccaf-prep/DISTRACTOR_HEURISTIC.md` index. **Never leak an exam answer key into a tracked file.**

## Input
`$ARGUMENTS` — a screenshot path (usually under `archive/screenshots/`, Read it as an image) and/or
pasted question text, plus the user's chosen answer (e.g. "my answer: D"). If the question text or the
user's answer is missing, ask once before proceeding.

## Steps
1. **Read the question.** If given a screenshot path, Read it (it renders the image). Capture verbatim:
   the scenario tag, the stem, every option, the user's pick, and the correct answer + rationale if the
   screenshot reveals them.
2. **Diagnose.** Identify the scenario + domain(s) (D1–D5). State the correct answer and *why*; for each
   distractor name which of the 5 patterns it is (over-engineering · prompt-when-determinism-needed ·
   blaming/assigning the wrong component · nonexistent feature · correlation-vs-causation) and the single
   discriminator ("which option is native/deterministic, or fits the problem's *shape*?").
3. **Write the shareable CONCEPT** (English, **no answer keys**, framed around the principle — never quote
   the verbatim question or its option letters). Apply the CLAUDE.md placement rule:
   - extends an existing concept → edit that doc, or a section of `DISTRACTOR_HEURISTIC.md`;
   - general pattern, not tied to an exercise → new file at `ccaf-prep/` root;
   - explains a *specific exercise's* behavior → file in that exercise's folder;
   - a one-liner → inline discriminator in `DISTRACTOR_HEURISTIC.md`.
4. **Register** any *new* shareable concept doc in the *Concept deep-dives* table in
   `DISTRACTOR_HEURISTIC.md` (sorted by domain). Do not consolidate into one big file or file-per-domain.
5. **Write the private WORKED-EXAMPLE** in `ccaf-prep/personal/` (git-ignored — this tier *may* quote
   everything): a markdown file (or append to a related one) with the **verbatim** question + options,
   the user's answer vs the correct one, a screenshot reference, and a 2–3 line "why I missed / why this
   is right." Mirror the style of the existing `personal/` notes.
6. **Log if relevant:** for a new attempt or a notable miss, add a line to `personal/exam_log.md`.
7. **Report** what you created/edited, grouped by tier (shareable vs private), and explicitly confirm no
   exam answer key landed in a tracked file.

Tracked content is English; `personal/` may be Spanish or English per the user. **Do not commit** —
leave the changes for the user to review.
