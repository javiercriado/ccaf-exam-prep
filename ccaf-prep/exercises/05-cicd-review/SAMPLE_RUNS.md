# Sample runs — annotated reference transcripts

Representative output of `review.py`, annotated with the task statements each step proves — so you
can review the behavior without re-running. One section per **Study runbook step** in the
[`README`](./README.md#study-runbook-do-this-in-order).

> ⚠️ **Output is non-deterministic.** The model runs at default temperature, so finding wording and
> ordering vary between runs. The toy "codebase" (`PAYMENTS_PY` / `LEDGER_PY`) and the criteria are
> deterministic; the model's findings are not. **Step 2 (`DECOMPOSE=False`) is the model-dependent
> anti-pattern — and it was verified to reproduce here** (3/3 monolith runs found nothing). These
> transcripts are *representative*, not exact.
>
> Model: default `claude-haiku-4-5` unless `CLAUDE_MODEL` overrides it.

**How runs are filed.** Each section = one runbook step. Runs go in the `Run N` table, tagged
**caught** or **missed** (for the cross-file bug). To add a run: paste me the output, say the step
number, I append it under that section.

---

## Experiment 0 — Clean pass · Runbook step 1 (`DECOMPOSE=True`)

> **Run 1× (stable). Expected result:** per-file LOCAL passes catch the resource leak and the
> off-by-one; a SEPARATE integration pass catches the cross-file contract mismatch; the final line
> reads `cross-file contract bug caught? True`.

```
========================================================================
CODE REVIEW PIPELINE  [DECOMPOSE=True  MODEL=claude-haiku-4-5]
========================================================================

-- PER-FILE LOCAL PASSES (each file in its OWN call; no attention dilution) --
   [payments.py] local findings: 1
      -   high resource-leak  L3: File handle opened with open() is never closed ...
   [ledger.py] local findings: 1
      -   high correctness    L6: Off-by-one: charging 'amount - 1' instead of 'amount' ...

-- CROSS-FILE INTEGRATION PASS (data flow across files) --
   integration findings: 2
      -   high cross-file    payments.py L9: charge() returns a bare bool (True), but ledger.py expects a dict with 'ok'/'txn_id'
      -   high cross-file    ledger.py L8: settle() dereferences result['ok'] and result['txn_id'], but charge() returns a bare bool

========================================================================
cross-file contract bug caught? True   (decomposition found it)

-- STRUCTURED OUTPUT (what CI parses) --
{
  "tool": "claude-review",
  "decompose": true,
  "findings": [ ... 4 findings: resource-leak, correctness, 2x cross-file ... ]
}
```

- 🎯 **Each file reviewed in its OWN call** = no attention dilution; both local bugs caught (D1.6).
- 🎯 **A SEPARATE integration pass** catches the cross-file contract mismatch the local passes can't
  see (D4.6 multi-pass).
- 🎯 **Forced `report_findings` → JSON** with severity/file/line/category that CI can parse (D3.6).
- Every review ran in a **fresh, independent** message list — no author reasoning (D4.6).

| Run | local findings | integration findings | cross-file caught? | Verdict |
|---|---|---|---|---|
| 1 | 2 (leak, off-by-one) | 2 | True | caught |

---

## Experiment A — decompose vs. "bigger context window" · Runbook step 2 (`DECOMPOSE=False`)

> **Run 2–3×. Expected result:** all files jammed into ONE prompt → the cross-file contract bug is
> diluted and `cross-file contract bug caught? False`. (sample Q12)

**Observed (`claude-haiku-4-5`, 3 runs):** monolith mode reproduced the anti-pattern *strongly* —
every run returned **zero findings**, missing not just the cross-file bug but both local bugs too.

```
========================================================================
CODE REVIEW PIPELINE  [DECOMPOSE=False  MODEL=claude-haiku-4-5]
========================================================================

-- SINGLE BIG PROMPT (all files at once; the 'bigger context window' anti-pattern) --
   findings: 0

========================================================================
cross-file contract bug caught? False   (MISSED — diluted in one big prompt)

-- STRUCTURED OUTPUT (what CI parses) --
{
  "tool": "claude-review",
  "decompose": false,
  "findings": []
}
```

| Run | findings | cross-file caught? | Verdict |
|---|---|---|---|
| 1 | 0 | False | missed |
| 2 | 0 | False | missed |
| 3 | 0 | False | missed |

> **The lesson, made vivid.** Compare to Experiment 0: the *same model* on the *same code* caught
> four bugs when each file got its own call, and **zero** when they shared one prompt. Decomposition
> isn't a marginal optimization — it's what GUARANTEES the model's attention lands on each file. "Use
> a bigger context window" moves in exactly the wrong direction (D1.6/D4.6, Q12).

---

## Experiment CI — headless CI gate · Runbook step 3 (`ci_review.sh`)

> **Optional (needs the `claude` CLI in a git repo with a diff).** Read it even if you don't run it —
> the exam point is the **flags and the synchronicity**, not local execution.

`ci_review.sh` is the headless pattern a CI step runs:

- `-p` / `--print` — run headless, no interactive UI (Q10).
- `--output-format json` — a structured envelope CI can parse.
- `--json-schema findings.schema.json` — constrain the result to the shared schema.
- The gate is **synchronous** and blocks the merge button; it must **not** move to the Batch API
  (async, ≤24h, no SLA — that suits nightly/offline reports, sample Q11).
- The invented `CLAUDE_HEADLESS` / `--batch` flags do **not** exist.

| Run | ran locally? | high-severity findings | exit | Verdict |
|---|---|---|---|---|
| 1 | (pending) | (pending) | (pending) | (pending — run only if you have the CLI + a diff) |
