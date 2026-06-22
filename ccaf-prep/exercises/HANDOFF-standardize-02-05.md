# Handoff — apply the "Exercise 1 documentation standard" to exercises 02–05

> Working doc for a fresh Claude Code session. Not exam material — delete or git-ignore when done.
> Paste the **Task** block below into a new session (it's self-contained); the rest is rationale.

---

## Task

Apply the "Exercise 1 documentation standard" to CCAF prep exercises 02–05.

REPO: /Users/javier/Code/anthropic-courses  (CCAF exam-prep kit).
First READ the reference template — exercise 01, already upgraded:
  ccaf-prep/exercises/01-support-agent/README.md
  ccaf-prep/exercises/01-support-agent/SAMPLE_RUNS.md
  ccaf-prep/exercises/01-support-agent/agent.py   (toggle comments, ⚠️ disclaimer, teaching-simplification note)
  ccaf-prep/exercises/01-support-agent/tools.py

THE STANDARD (what 01 now has, to replicate where applicable):
1. README "## Study runbook (do this in order)" as a TABLE. Columns:
   Step | <one column per toggle, showing its value each step> | What to do | Runs |
   Expected result — what it teaches | Files as.
   Above the table: list toggle DEFAULTS + the rule "change exactly ONE toggle from the clean
   baseline per step, reset between steps."
2. An explicit "Expected result — what it teaches" for every step.
3. **HONESTY ABOUT MODEL-DEPENDENCE (the most important learning — see rationale below).**
   Anti-pattern toggles demonstrate a PRINCIPLE, not a guaranteed failure. On a capable model
   (`claude-haiku-4-5`) + toy input, the bad outcome often will NOT reproduce. So:
   - VERIFY actual behavior by running (cheap Haiku). Record what you actually saw.
   - Where it does NOT reproduce, say so plainly and teach the principle ("the prompt usually
     works, which is exactly why you don't rely on it for irreversible ops"). Do NOT assert an
     outcome the reader won't see, and do NOT invent "~1 in N" reproduction rates.
   - Add a ⚠️ disclaimer box (mirror 01's) at the top of the runbook saying the anti-patterns are
     model-dependent and that correct behavior is the expected, honest result.
   - Distinguish the MECHANISM (deterministic: the input/structure really changes) from the
     OUTCOME (model-dependent: whether the model then slips). If a slip can be forced by raising
     pressure / harder input, note how — but keep the default fixtures clean.
4. A SAMPLE_RUNS.md (for exercises that produce script output): one section per runbook step, each
   led by an "Expected/Observed result" blurb, with a "Run N" scaffold table left "(pending)" for
   the user to fill (or filled with the correct rows you actually observed). Non-determinism +
   model-dependence caveat at top. Cross-link each README step ↔ its SAMPLE_RUNS section.
5. A "How to record a run" block in the README: user pastes output + step number → file it under
   that section's table, tagged correct vs. anti-pattern.
6. "## Run" block: LEAD with `cd ccaf-prep/exercises/<folder>` from repo root, then the command.
   Fix any stale ".env" comment to "repo-root .env via find_dotenv".
7. Teaching-simplification callouts wherever a fixture/mock could be mistaken for real behavior —
   in BOTH the code comment and the README.

HARD CONSTRAINTS:
- DO NOT change code logic or toggle DEFAULT values. Only docs, comments, READMEs, new
  SAMPLE_RUNS.md files.
- English only. Match the existing terse house style.
- Do NOT touch exercise 01.
- Do NOT edit the root README.md / README.es.md / CLAUDE.md status tables — the repo owner
  maintains those to avoid a merge conflict with a parallel session.
- After editing, `uv run python -m py_compile <each .py>` to confirm no syntax breakage.
  Running real API calls to verify behavior IS encouraged (cheap Haiku) so your "Observed" notes
  are honest — but leave any rows you didn't run as "(pending)".
- Commit ONLY if the user explicitly asks.

PER-EXERCISE SPECIFICS (from a survey — verify line numbers yourself):

EX2 (02-claude-code-team) — CONFIG ONLY. No Python, no toggles, no script output.
  - Build a Study-runbook table WITHOUT toggle columns: each step walks one config artifact
    (CLAUDE.md hierarchy + @import of team-conventions.md; /review-pr command;
    .claude/rules/tests.md globs; changelog SKILL.md frontmatter; .mcp.json ${ENV} expansion),
    each with an "Expected result — what it teaches."
  - Keep the run interactive (its section is "Commands to actually try"). Instead of a `cd`,
    clarify WHERE to open Claude Code (a repo containing this .claude/ folder).
  - No SAMPLE_RUNS.md (no script output) — skip it.
  - Teaching-simplification: .mcp.json ${ENV} placeholders are not real secrets.
  - Model-dependence note does NOT apply (no model calls) — omit the ⚠️ box here.

EX3 (03-extraction-pipeline) — extract.py, REAL API. FULL treatment.
  - Toggles: FEW_SHOT (~line 38, default True), DEMO_RETRY (~line 138, default True),
    CONF_THRESHOLD (~line 148, default 0.70 — a numeric knob, not a baseline boolean).
  - FEW_SHOT=False is the closest thing to a genuinely probabilistic step (confidence + flagged-
    field list wobble between runs). VERIFY this still reproduces on the current model; if it does,
    use 3–5× framing; if it now behaves, use the honest principle framing instead.
  - DEMO_RETRY=False (retry won't fire) and CONF_THRESHOLD changes (routing flips) are mechanism-
    deterministic → "1×", shows every run.
  - Teaching-simplification: few-shot examples are canned; MESSY_INPUT is a toy hardcoded msg.
  - Create SAMPLE_RUNS.md; add the `cd` to the Run block.

EX4 (04-multi-agent-research) — coordinator_sdk.py (real Agent SDK) + coordinator.py
  (real API, MOCKED facts). FULL treatment.
  - Toggles (coordinator.py): DYNAMIC_SELECTION (~line 42, default True),
    PASS_CONTEXT (~line 43, default True). The MECHANISM is deterministic (pipeline really changes /
    subagent really gets no context) → "1×". But whether the blinded subagent produces a WORSE
    answer is model-dependent — frame honestly: the toggle proves context isn't inherited unless
    passed, not that the output is always visibly broken.
  - Two entrypoints — runbook covers both: a step running coordinator_sdk.py (observe real Task
    delegation, ~$0.04 on Haiku), then toggle steps on coordinator.py.
  - STRONG teaching-simplification (mirror 01's identity note): verify_fact() returns self-asserted
    {"verified": True, "note": "checksum ok (toy)"} — fake verification, not real fact-checking.
    web_search/load_document/landmark_lookup return hardcoded _FACTS; one figure is deliberately
    conflicting (37.0M vs 41.0M) to demo provenance. Annotate in code + README.
  - cd fix (two run commands). Create SAMPLE_RUNS.md.

EX5 (05-cicd-review) — review.py + ci_review.sh + findings.schema.json, REAL API. FULL treatment.
  - Toggle: DECOMPOSE (review.py ~line 44, default True). MECHANISM deterministic (DECOMPOSE=False
    really jams all files into one prompt). OUTCOME (the cross-file contract bug being missed) is
    MODEL-DEPENDENT — VERIFY by running 2–3×: if Haiku reliably misses it, say so; if it still
    catches it, use the honest principle framing ("decompose to GUARANTEE attention per file, not
    because one prompt always fails"). Do not overstate.
  - Add a runbook step that runs ci_review.sh to watch headless
    `claude -p ... --output-format json --json-schema` emit schema-valid findings (D3.6).
  - Teaching-simplification: PAYMENTS_PY / LEDGER_PY are toy planted bugs, not real code.
  - cd fix. Create SAMPLE_RUNS.md.

Deliver a short per-exercise summary of what changed. Ask the repo owner before committing.

---

## Why this standard exists (rationale, for the operator — not needed in the Task block)

Exercise 1 was originally built on "build the wrong version and watch it fail ~1 in 20"
(see `ccaf-prep/ANALYSIS.md`). When the owner actually ran the toggles on `claude-haiku-4-5`:

- Experiment A (`ENFORCE=False`, $900 refund): escalated correctly **5/5** — no slip.
- Experiment B (`GOOD_DESCRIPTIONS=False`): routed correctly — the tool *names* + schemas
  disambiguate without descriptions.
- Experiment C (verify-skip): shares A's toggle state; same non-reproduction. Folded into A.

The resolution was NOT to engineer the failures into existence (that means crippling tool names or
adding adversarial fixtures = artificial). It was to **reframe honestly**: the anti-pattern teaches
a *decision principle*. The exam rewards choosing the deterministic option (gate, JSON schema,
decomposition) **regardless of how reliably the prompt happens to behave** — because you can't prove
a 0% failure rate and some operations (refunds, money) are irreversible. "It worked 5/5 on a toy and
you STILL gate it" is a stronger lesson than "watch it break." Carry that framing into 02–05; don't
fake failures to make a toggle look dramatic.
