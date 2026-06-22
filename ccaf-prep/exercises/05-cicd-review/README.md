# Exercise 5 — CI/CD Code Review

**Lights up:** Scenario 5 (CI/CD). **Sample questions:** 10, 11, 12.
**Domains:** D1.6 (decomposition), D3.5/3.6 (iterative refinement, CI integration),
D4.1/4.5/4.6 (explicit criteria, batch, multi-pass review).

## Study runbook (do this in order)

Each step maps 1:1 to a section of [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md) (the *"Files as"* column).
Read the **Expected result** column *before* you run.

> ⚠️ **Read this first — the anti-pattern is model-dependent, but here it DID reproduce.**
> The `DECOMPOSE=False` step demonstrates a PRINCIPLE, not a guaranteed failure. Whether the monolith
> prompt actually misses the bug is model-dependent — so it was **verified by running**. On this toy +
> `claude-haiku-4-5` it reproduced *strongly*: **3/3 runs in monolith mode returned ZERO findings**
> (the cross-file contract bug *and* both local bugs were diluted away), while the decomposed run
> caught all of them. That is a stronger result than EX1's anti-patterns — but the lesson is the same:
> you **decompose to GUARANTEE attention per file**, not because one big prompt always fails. If your
> model happens to catch the bug in monolith mode, the principle is unchanged — a 2-file toy diluting
> to zero findings shows how fast attention erodes as the prompt grows.
>
> Separate the **MECHANISM** (deterministic: `DECOMPOSE=False` really collapses the per-file +
> integration passes into one prompt) from the **OUTCOME** (model-dependent: whether the bug is then
> missed — here, reliably yes).

**The one toggle, every step** — the rule is *change only `DECOMPOSE` from the clean baseline*.
Default is `DECOMPOSE = True` (top of `review.py`); set it back when done.

| Step | `DECOMPOSE` | What to do | Runs | Expected result — what it teaches | Files as |
|---|---|---|---|---|---|
| 1 | `True` | **Clean pass — change nothing.** Read *"What maps to what"* while it scrolls. | **1×** | Per-file LOCAL passes (each file in its own call) catch the resource leak + off-by-one; a SEPARATE integration pass catches the cross-file contract mismatch; `cross-file contract bug caught? True`. Forced `report_findings` emits CI-parseable JSON. (D1.6, D4.6, D4.1, D3.6) | Experiment 0 |
| 2 | **`False`** | **Experiment A — decompose vs. "bigger context window".** Rerun 2–3×, watch `cross-file contract bug caught?`. | **2–3×** | All files in ONE prompt → the cross-file bug is **diluted and MISSED** (observed `caught? False`, 0 findings, 3/3). Proof that the fix the exam rewards is **decomposition**, not a bigger model/context (sample Q12). | Experiment A |
| 3 | `True` | **Inspect (or run) `ci_review.sh`.** Read the headless flags; run it only if you have the `claude` CLI in a git repo with a diff. | optional | The CI gate is **headless** (`-p`/`--print`), **synchronous**, and emits schema-constrained JSON (`--output-format json --json-schema findings.schema.json`) so the pipeline decides pass/fail. The invented `CLAUDE_HEADLESS` / `--batch` flags don't exist. (D3.6, Q10) | Experiment CI |
| 4 | `True` | **Bank questions** — 20–30 on D3 + D4; re-read the matching experiment on any miss. | as needed | A miss tells you which *principle* didn't stick — re-read that experiment, not just re-run it. | — |

### How to record a run (so it lands in `SAMPLE_RUNS.md`)
Paste me the output and say **which step number** it's from (e.g. "step 2, run 3"). I file it under
that step's section, label it `Run 1 / Run 2 / …`, and tag whether it **caught** or **missed** the
cross-file bug — so the variation across runs is visible at a glance. Minimum I need: the
`CODE REVIEW PIPELINE [DECOMPOSE=…]` header and the `cross-file contract bug caught?` line.

Track *your* exam progress and misses in `ccaf-prep/personal/exam_log.md`, not here.

## What's here
- `review.py` — the review pipeline. Per-file local passes + a cross-file integration pass,
  with explicit criteria and forced structured output. One toggle: `DECOMPOSE`.
- `ci_review.sh` — the **headless** `claude -p ... --output-format json --json-schema` pattern
  a CI step runs (sample, not executed locally).
- `findings.schema.json` — the JSON schema the CI invocation constrains output to.

> **Teaching simplification.** `PAYMENTS_PY` and `LEDGER_PY` are **toy files with deliberately
> planted bugs** (a resource leak, an off-by-one, and a cross-file contract mismatch) — not real
> production code. The pipeline (per-file passes, integration pass, forced structured output) is real;
> the "codebase" is a fixture sized so one cheap pass shows decomposition catching what the monolith
> dilutes. (Same note lives in `review.py`.)

## Run
```bash
# from the repo root, cd into this exercise folder first:
cd ccaf-prep/exercises/05-cicd-review

# uv finds ../pyproject.toml and uses the ccaf-prep env; the script self-loads the
# repo-root .env via find_dotenv, so no export step is needed.
uv run python review.py
```
Then flip `DECOMPOSE = False` (top of `review.py`) and rerun to watch the cross-file bug get
missed. (Defaults to `claude-haiku-4-5`; set `CLAUDE_MODEL` in the `.env` to override.)

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

> The DECOMPOSE one is model-dependent but **verified to reproduce** here (see the ⚠️ box). The
> others are design distractors — recognize them, don't run them.

1. **"Just use a bigger context window" (Q12, D1.6/D4.6).** Set `DECOMPOSE = False`: all files
   go into ONE prompt. The cross-file contract bug (a function returns a bare `bool` but the
   caller dereferences `result["ok"]`) gets **diluted and missed** — on this toy + Haiku, the
   monolith pass returned **zero findings 3/3**. The fix the exam rewards is **decomposition**
   (per-file + integration), not a bigger model/context.
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
