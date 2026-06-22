# Exercise 3 — Structured Extraction Pipeline

**Lights up:** Scenario (Document/Data Extraction). **Domains:** D4 (few-shot,
structured output, validation/retry), D2 (tool_choice), D5 (context trim,
confidence routing).

## Study runbook (do this in order)

Each step maps 1:1 to a section of [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md) (the *"Files as"* column).
Read the **Expected result** column *before* you run — it's what each step is meant to teach.

> ⚠️ **Read this first — one anti-pattern is model-dependent, two are deterministic.**
> On a capable model (`claude-haiku-4-5`) with this toy input:
> - **FEW_SHOT=False** (step 2) is the only genuinely *probabilistic* knob, and even it barely
>   moves: when run, the model still extracted every field correctly and only the aggregate
>   confidence wobbled (**0.72–0.75 vs 0.77** with few-shot on) — routing was identical. That is
>   **expected**, not a broken experiment. The lesson is the *principle*: few-shot is the rewarded
>   fix for **consistent format + ambiguous-case judgment**, and you adopt it even though a capable
>   model often copes without it — because "often copes" is not "reliably calibrated at scale."
> - **DEMO_RETRY** (step 3) and **CONF_THRESHOLD** (step 4) are **deterministic mechanisms** — flip
>   them and the behavior changes the *same way every run*. No model-dependence caveat needed there.
>
> Throughout, separate the **MECHANISM** (deterministic: the prompt structure / threshold really
> changes) from the **OUTCOME** (whether the model then slips — model-dependent, here usually fine).

**All three toggles, every step** — the rule is *change exactly one toggle from the clean baseline
per step*, so whatever you observe is attributable to that one change. Defaults are
`FEW_SHOT = True`, `DEMO_RETRY = True`, `CONF_THRESHOLD = 0.70` (all in `extract.py`); set them back
between steps.

| Step | `FEW_SHOT` | `DEMO_RETRY` | `CONF_THRESHOLD` | What to do | Runs | Expected result — what it teaches | Files as |
|---|---|---|---|---|---|---|---|
| 1 | `True` | `True` | `0.70` | **Clean pass — change nothing.** Read *"What maps to what"* (below) while it scrolls. | **1×** | Forced `tool_use` → valid JSON every time (D4.3); attempt 0's date fails the strict validator → one **retry with feedback** → attempt 1 fixes it (D4.4); `account_id` comes back `null` (not fabricated, D4.3); confidence routing flags `account_id` (0.0) to **HUMAN REVIEW** while the aggregate (~0.77) looks safe (D5.5). | Experiment 0 |
| 2 | **`False`** | `True` | `0.70` | **Experiment A — few-shot vs. instructions alone.** Rerun a few times and watch the `aggregate(mean)` and the flagged-field list. | **3–5×** | Most likely it still extracts correctly; the aggregate drifts a little (observed 0.72–0.75) but routing stays the same. The point is **not** to catch a failure — it's that few-shot is what makes format + ambiguous-case judgment *consistent* at scale, even when one capable run copes without it. (D4.2, distractor: "detailed prose instead of examples") | Experiment A |
| 3 | `True` | **`False`** | `0.70` | **Experiment B — when retry fires.** Rerun and watch the `attempt` lines. | **1×** | Deterministic: attempt 0 already produces a clean ISO date, so **no retry fires** ("after 0 retries"). Teaches that retry-with-feedback only helps when the info is *present but mis-formatted* — not when it is absent. (D4.4) | Experiment B |
| 4 | `True` | `True` | **`0.99`** then **`0.0`** | **Experiment C — the routing knob.** Set `0.99`, run; then `0.0`, run. | **1×** each | Deterministic arithmetic: at `0.99` **every** field (even `name` 0.98) routes to HUMAN REVIEW; at `0.0` **everything auto-accepts — including `account_id` at 0.0 confidence** (the danger of too low a gate). Teaches that the threshold trades automation rate vs. safety, and the aggregate hides the weak field. (D5.5) | Experiment C |
| 5 | `True` | `True` | `0.70` | **Bank questions** — 20–30 on D4 + D5; re-read the matching experiment's framing on any miss. | as needed | A miss tells you which *principle* didn't stick — re-read that experiment, not just re-run it. | — |

### How to record a run (so it lands in `SAMPLE_RUNS.md`)
Paste me the output and say **which step number** it's from (e.g. "step 2, run 3"). I file it
under that step's section, label it `Run 1 / Run 2 / …`, and tag whether it showed the **expected**
path or a slip — so the variation across runs is visible at a glance. Minimum I need: the header
line (it shows the toggle state) and the `CONFIDENCE routing` block (for steps 2/4) or the `attempt`
lines (for step 3).

Track *your* exam progress and misses in `ccaf-prep/personal/exam_log.md`, not here.

## What's here
- `extract.py` — one extraction tool with a JSON `input_schema`, called with a
  **forced** `tool_choice`, wrapped in a validation-retry loop and a
  confidence-routing + context-trim post-step. Everything is observable via
  `print()`.

> **Teaching simplification.** The few-shot examples (`FEW_SHOT_TURNS`) are **canned**
> demonstrations and `MESSY_INPUT` is one **hardcoded toy** support message — both stand in for a
> real labelled example set and a real document stream. The *mechanisms* (forced tool_use,
> validate-retry, confidence routing) are real; only the data is a fixture, so one cheap call
> teaches each concept.

## Run
```bash
# from the repo root, cd into this exercise folder first:
cd ccaf-prep/exercises/03-extraction-pipeline

# uv finds ../pyproject.toml and uses the ccaf-prep env; the script self-loads the
# repo-root .env via find_dotenv, so no export step is needed.
uv run python extract.py
```
(Defaults to `claude-haiku-4-5`; set `CLAUDE_MODEL` in the `.env` to override.)

## What maps to what (read while the output scrolls)

| You see in the output | Task Statement |
|---|---|
| `FORCED tool_use -> ... (JSON syntactically valid by construction)` | **D4.3** tool_use guarantees *syntactic* validity (no parse errors), **not** semantic correctness |
| `tool_choice={"type":"tool","name":"record_refund_request"}` in the call | **D2.3** forced specific tool (auto / any / forced shown in the docstring) |
| `account_id is null (correctly NOT fabricated)` | **D4.3** nullable field — absent in source → `null`, not invented |
| `[FEW_SHOT=True]` header + the 2 example turns prepended | **D4.2** few-shot for consistent format + ambiguous-case judgment |
| `VALIDATION failed: [...] -> retrying with feedback` then `attempt 1` | **D4.4** retry-with-error-feedback (the error is appended as an `is_error` tool_result) |
| `CONFIDENCE routing ... AUTO-ACCEPT / HUMAN REVIEW` | **D5.5** field-level confidence routing |
| `aggregate(mean) ≈ 0.8 <- can HIDE a weak field` | **D5.5** an aggregate score masks a weak field |
| `TRIMMED for downstream (dropped raw 'confidence' blob)` | **D5.1** trim verbose context, keep structured fields |

## The anti-pattern experiments / distractors (the real learning)

> These teach a **principle**. The FEW_SHOT one is model-dependent (usually copes on this toy — see
> the ⚠️ box); the DEMO_RETRY and CONF_THRESHOLD ones are deterministic mechanisms.

1. **"A strict schema fixes semantic errors" — FALSE (D4.3).** The
   `FORCED tool_use` line proves the JSON is *syntactically* valid every time —
   you will never get a parse error. But that says nothing about whether `amount`
   matches the source or a value landed in the right field. Syntax is guaranteed;
   *semantics* are caught downstream by the D4.4 validator and D5.5 confidence —
   not by the schema. The distractor answer "tighten the schema to fix wrong
   values" is wrong.

2. **Retrying when the info is ABSENT — useless (D4.4).** The retry here succeeds
   only because the date IS in the source, just mis-formatted (`Mar 5 2024` →
   `2024-03-05`) — a format/structural error. Read the `NOTE` in `force_extract`:
   if a field were simply *not in the message* (like `account_id`), no number of
   retries would conjure it. The right move for absent info is `null` + human
   review, **not** a loop. To feel the retry mechanics, leave `DEMO_RETRY = True`
   (it corrupts only attempt 0's date so the loop fires every run); flip it
   `False` to see attempt 0 already pass when the model nails the format.

3. **Detailed instructions ALONE instead of few-shot (D4.2).** Set
   `FEW_SHOT = False` and rerun a few times. The base `SYSTEM` prompt still spells
   out the rules, so on this toy a capable model still extracts correctly — only the
   per-field confidence calibration drifts a little (observed `aggregate(mean)`
   0.72–0.75 vs 0.77; the flagged-field list held steady). Few-shot is the rewarded
   fix for *consistent format + ambiguous-case judgment*, not more prose — and you
   adopt it for reliability *across* documents, not because one run breaks.

4. **Trusting a healthy AGGREGATE while a field is weak (D5.5).** The routing block
   prints the mean confidence next to the per-field breakdown. Here four fields
   (name, amount, date, reason) score ~0.95+, so the mean lands ~0.8 — above the
   0.70 line, looks safe to automate — yet `account_id` is at `0.0` and gets routed
   to HUMAN REVIEW. The exam distractor "~97% aggregate accuracy → safe to automate"
   ignores that one field/segment can be terrible; you must inspect *by field*, not
   the average, before reducing review.

## After this exercise
Do **20–30 bank questions on D4 + D5**. If you miss a structured-output or
confidence pattern, rerun the matching experiment above before moving on.
