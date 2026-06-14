# Exercise 3 — Structured Extraction Pipeline

**Lights up:** Scenario (Document/Data Extraction). **Domains:** D4 (few-shot,
structured output, validation/retry), D2 (tool_choice), D5 (context trim,
confidence routing).

## What's here
- `extract.py` — one extraction tool with a JSON `input_schema`, called with a
  **forced** `tool_choice`, wrapped in a validation-retry loop and a
  confidence-routing + context-trim post-step. Everything is observable via
  `print()`.

## Run
```bash
# from this folder — uv finds ../pyproject.toml and uses the ccaf-prep env (native arm64).
uv run python extract.py
```
Key + model are loaded ROBUSTLY by the script from
`../../claude-with-anthropic-api/.env` (`ANTHROPIC_API_KEY`, optional
`CLAUDE_MODEL`; falls back to `claude-sonnet-4-6`). No need to export anything.

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
   out the rules, but without the 2 worked examples the model's per-field
   confidence calibration and judgment on the ambiguous bits (spelled-out
   "two-fifty", missing account id) get noisier — you can watch the
   `aggregate(mean)` and the flagged-field list wobble between runs. Few-shot is
   the rewarded fix for *consistent format + ambiguous-case judgment*, not more
   prose.

4. **Trusting a healthy AGGREGATE while a field is weak (D5.5).** The routing block
   prints the mean confidence next to the per-field breakdown. Here four fields
   (name, amount, date, reason) score ~0.95+, so the mean lands ~0.8 — above the
   0.70 line, looks safe to automate — yet `account_id` is at `0.0` and gets routed
   to HUMAN REVIEW. The exam distractor "~97% aggregate accuracy → safe to automate"
   ignores that one field/segment can be terrible; you must inspect *by field*, not
   the average, before reducing review.

## Toggles to flip
| Toggle | In | Effect |
|---|---|---|
| `FEW_SHOT` | `extract.py` top | `False` removes the 2 example turns → noisier judgment/confidence (D4.2) |
| `DEMO_RETRY` | `extract.py` top | `False` stops forcing the attempt-0 format error → retry may not fire (D4.4) |
| `CONF_THRESHOLD` | `extract.py` | raise/lower to change which fields route to human review (D5.5) |

## After this exercise
Do **20–30 bank questions on D4 + D5**. If you miss a structured-output or
confidence pattern, rerun the matching experiment above before moving on.
