# Exercise 5 — CI/CD Code Review

**Lights up:** Scenario 5 (CI/CD). **Sample questions:** 10, 11, 12.
**Domains:** D1.6 (decomposition), D3.5/3.6 (iterative refinement, CI integration),
D4.1/4.5/4.6 (explicit criteria, batch, multi-pass review).

## What's here
- `review.py` — the review pipeline. Per-file local passes + a cross-file integration pass,
  with explicit criteria and forced structured output. One toggle: `DECOMPOSE`.
- `ci_review.sh` — the **headless** `claude -p ... --output-format json --json-schema` pattern
  a CI step runs (sample, not executed locally).
- `findings.schema.json` — the JSON schema the CI invocation constrains output to.

## Run
```bash
# from this folder — uv finds ../pyproject.toml and uses the ccaf-prep env (native arm64).
uv run python review.py
```
Then flip `DECOMPOSE = False` (top of `review.py`) and rerun to watch the cross-file bug get
missed. (If `claude-sonnet-4-6` isn't on your key, set `CLAUDE_MODEL` in the `.env`.)

## What maps to what (read while the output scrolls)

| You see in the output | Task Statement |
|---|---|
| per-file passes, each file in its OWN call | **D1.6** decomposition (avoid attention dilution) |
| a SEPARATE cross-file integration pass catches the contract mismatch | **D1.6 / D4.6** multi-pass |
| `cross-file contract bug caught? True` (decompose) vs `MISSED` (monolith) | **Q12** decompose, don't just "scale" |
| `CRITERIA = {security, correctness, resource-leak}` passed explicitly | **D4.1** explicit categorical criteria |
| every review runs in a FRESH message list (`system` = "INDEPENDENT reviewer") | **D4.6** independent instance > self-review |
| forced `tool_use` → `report_findings` JSON with severity/file/line/category | **D3.6** structured output CI can parse |
| `ci_review.sh`: `-p` / `--output-format json` / `--json-schema` | **D3.6 / Q10** headless flags |

## Anti-pattern experiments / distractors (the real learning)

1. **"Just use a bigger context window" (Q12, D1.6/D4.6).** Set `DECOMPOSE = False`: all files
   go into ONE prompt. The cross-file contract bug (a function returns a bare `bool` but the
   caller dereferences `result["ok"]`) typically gets **diluted and missed**. The fix the exam
   rewards is **decomposition** (per-file + integration), not a bigger model/context.
2. **Self-review (D4.6).** Reviewing inside the same conversation that wrote the code lets the
   model rationalize its own bugs. Here every review runs in a **fresh, independent** message
   list — model-independent of any "author reasoning."
3. **Vague criteria (D4.1, D3.5).** "Be conservative / find problems" produces false positives
   that erode trust. Pass **explicit categories** instead (see `CRITERIA`). Iterative
   refinement (D3.5) means concrete input/output examples + test-driven iteration, **not**
   longer prose instructions.
4. **Batch the blocking gate (Q11, D4.5).** Tempting: move the pre-merge review to the Batch
   API for the 50% discount. **Wrong** — Batches are async (≤24h, no SLA, no multi-turn tools)
   and fit **nightly/offline reports**. A pre-merge gate must be **synchronous** (`review.py`
   / `ci_review.sh`). See the note at the bottom of `ci_review.sh`.
5. **Invented CI flags (Q10, D3.6).** `CLAUDE_HEADLESS`, `--batch` don't exist. The real
   headless flags are `-p`/`--print`, `--output-format json`, `--json-schema`.

## Notes
- **D3.5 iterative refinement:** the cheapest way to improve a reviewer is concrete I/O
  examples and test-driven iteration on real diffs — not piling on prose.
- **D4.5 when batch IS right:** offline/nightly report generation across many files where a
  24h turnaround is fine and nothing is blocked waiting on it.

## After this exercise
Do **20–30 bank questions on D3 + D4**. If a CI/batch distractor fools you, rerun with the
toggle flipped before moving on.
