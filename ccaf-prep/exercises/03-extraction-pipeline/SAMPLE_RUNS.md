# Sample runs — annotated reference transcripts

Representative output of `extract.py`, annotated with the task statements each step proves — so you
can review the behavior without re-running. One section per **Study runbook step** in the
[`README`](./README.md#study-runbook-do-this-in-order).

> ⚠️ **Output is non-deterministic.** The model runs at default temperature, so confidence numbers
> and wording vary between runs. The **tool fixtures** (few-shot turns, `MESSY_INPUT`, the validator)
> are deterministic; the model's per-field confidence is not. These transcripts are *representative*,
> not exact. Of the four steps, only **step 2 (FEW_SHOT=False)** is genuinely probabilistic — and on
> this toy it barely moves (see below). Steps 3 and 4 are deterministic mechanisms.
>
> Model: default `claude-haiku-4-5` unless `CLAUDE_MODEL` overrides it.

**How runs are filed.** Each section = one runbook step. Runs go in the `Run N` table, tagged
**expected** (behaved as the column predicts) or **slip** (the rare deviation). To add a run: paste
me the output, say the step number, I append it under that section.

---

## Experiment 0 — Clean pass · Runbook step 1 (`FEW_SHOT=True`, `DEMO_RETRY=True`, `CONF_THRESHOLD=0.70`)

> **Run 1× (behavior is stable). Expected result:** forced `tool_use` → valid JSON; attempt 0's date
> is deliberately corrupted so the D4.4 validator fails and **one retry with feedback** fixes it;
> `account_id` returns `null` (not fabricated); the routing block flags only `account_id` to HUMAN
> REVIEW while the aggregate looks safe.

```
======================================================================
EX3 extraction pipeline   [FEW_SHOT=True  MODEL=claude-haiku-4-5]
INPUT: ugh hi, Maria Garcia here. need a refund — it was two-fifty (250-ish), bought it on march 5 2024. order arrived smashed.
======================================================================
  [attempt 0] FORCED tool_use -> stop_reason=tool_use  (JSON syntactically valid by construction)
  VALIDATION failed: ["'date' must be strict YYYY-MM-DD, got 'Mar 5 2024'."] -> retrying with feedback
  [attempt 1] FORCED tool_use -> stop_reason=tool_use  (JSON syntactically valid by construction)

EXTRACTED (after 1 retry):
  {"name": "Maria Garcia", "amount": 250, "date": "2024-03-05", "account_id": null, "reason": "order arrived smashed"}
  account_id is null (correctly NOT fabricated)

  CONFIDENCE routing (threshold 0.7):
    aggregate(mean) = 0.77  <- can HIDE a weak field (D5.5)
    AUTO-ACCEPT : ['name', 'amount', 'date', 'reason']
    HUMAN REVIEW: [('account_id', 0.0)]

  TRIMMED for downstream (dropped raw 'confidence' blob): {'name': 'Maria Garcia', 'amount': 250, 'date': '2024-03-05', 'account_id': None, 'reason': 'order arrived smashed'}
```

- 🎯 **`FORCED tool_use` → JSON valid every time (D4.3).** No `json.loads` try/except is needed; the
  tool schema guarantees *syntactic* validity. Semantic correctness is a separate problem.
- 🎯 **One retry fires (D4.4).** `DEMO_RETRY` corrupts attempt 0's date to `Mar 5 2024`; the strict
  validator rejects it, the error is appended as an `is_error` tool_result, and attempt 1 self-corrects.
- 🎯 **`account_id` is `null`, not invented (D4.3).** The field is nullable and the source omits it.
- 🎯 **Aggregate (0.77) hides the weak field (D5.5).** Mean looks safe; per-field routing still sends
  `account_id` (0.0) to human review.

| Run | retries | `account_id` | aggregate | flagged | Verdict |
|---|---|---|---|---|---|
| 1 | 1 | `null` | 0.77 | `account_id` | expected |

---

## Experiment A — few-shot vs. instructions alone · Runbook step 2 (`FEW_SHOT=False`)

> **Run 3–5×. Expected result:** ideally a run where the missing examples visibly degrade judgment
> (a mis-normalized amount, a wrong date, or wildly different confidence). In practice, on this toy
> the model still extracts everything correctly — only the **aggregate confidence drifts a little**.

**Observed (`claude-haiku-4-5`, 4 runs):** all 4 extracted correctly; the aggregate wobbled in a
narrow band (0.72–0.75, vs 0.77 with few-shot on) and the flagged-field list never changed.

```
======================================================================
EX3 extraction pipeline   [FEW_SHOT=False  MODEL=claude-haiku-4-5]
INPUT: ugh hi, Maria Garcia here. need a refund — it was two-fifty (250-ish), bought it on march 5 2024. order arrived smashed.
======================================================================
  [attempt 0] FORCED tool_use -> stop_reason=tool_use  (JSON syntactically valid by construction)
  VALIDATION failed: ["'date' must be strict YYYY-MM-DD, got 'Mar 5 2024'."] -> retrying with feedback
  [attempt 1] FORCED tool_use -> stop_reason=tool_use  (JSON syntactically valid by construction)

EXTRACTED (after 1 retry):
  {"name": "Maria Garcia", "amount": 250, "date": "2024-03-05", "reason": "item arrived smashed", "account_id": null}
  account_id is null (correctly NOT fabricated)

  CONFIDENCE routing (threshold 0.7):
    aggregate(mean) = 0.72  <- can HIDE a weak field (D5.5)
    AUTO-ACCEPT : ['name', 'amount', 'date', 'reason']
    HUMAN REVIEW: [('account_id', 0.0)]
```

| Run | aggregate | flagged | extracted amount | Verdict |
|---|---|---|---|---|
| 1 | 0.75 | `account_id` | 250 | expected (mild drift) |
| 2 | 0.73 | `account_id` | 250 | expected (mild drift) |
| 3 | 0.74 | `account_id` | 250 | expected (mild drift) |
| 4 | 0.72 | `account_id` | 250 | expected (mild drift) |

> **This *is* the lesson.** A capable model with a clear SYSTEM prompt usually copes on one toy
> message, so few-shot looks optional. It is not — its value is **consistency of format and
> ambiguous-case judgment across many, varied documents**, which one green run can't prove. You adopt
> few-shot for the same reason you gate a refund in EX1: "usually fine" ≠ "reliable at scale."

---

## Experiment B — when retry fires · Runbook step 3 (`DEMO_RETRY=False`)

> **Run 1× (deterministic). Expected result:** with the attempt-0 corruption disabled, the model
> nails the ISO date on the first try, so the D4.4 retry path **does not fire** — "after 0 retries".

**Observed (`claude-haiku-4-5`):** attempt 0 passed; no `VALIDATION failed` line; 0 retries.

```
  [attempt 0] FORCED tool_use -> stop_reason=tool_use  (JSON syntactically valid by construction)
EXTRACTED (after 0 retries):
```

> **Mechanism, not luck.** `DEMO_RETRY=True` exists *only* to make the feedback loop observable by
> forcing a present-but-mis-formatted error. Turning it off removes the manufactured error, so attempt
> 0 passes. The teaching point: retry helps when info is **present but mis-formatted**; it cannot
> conjure **absent** info (that's `null` + human review).

| Run | retries | Verdict |
|---|---|---|
| 1 | 0 | expected (no retry) |

---

## Experiment C — the routing knob · Runbook step 4 (`CONF_THRESHOLD` 0.99, then 0.0)

> **Run 1× each (deterministic arithmetic). Expected result:** the threshold is a pure comparison
> (`conf[field] >= CONF_THRESHOLD`). Raise it and more fields flip to HUMAN REVIEW; drop it to 0.0 and
> everything auto-accepts — *including the 0.0-confidence `account_id`*, which is the danger.

**Observed (`claude-haiku-4-5`):**

```
# CONF_THRESHOLD = 0.99
    aggregate(mean) = 0.76  <- can HIDE a weak field (D5.5)
    AUTO-ACCEPT : []
    HUMAN REVIEW: [('name', 0.98), ('amount', 0.92), ('date', 0.97), ('account_id', 0.0), ('reason', 0.95)]

# CONF_THRESHOLD = 0.0
    aggregate(mean) = 0.76  <- can HIDE a weak field (D5.5)
    AUTO-ACCEPT : ['name', 'amount', 'date', 'account_id', 'reason']
    HUMAN REVIEW: []
```

> **The knob trades automation rate vs. safety.** At `0.99` even `name` (0.98) is held for review —
> over-cautious. At `0.0` the `account_id` the model itself scored **0.0** gets auto-accepted — exactly
> the silent-bad-data failure D5.5 warns about. The default 0.70 sits between: automate the confident
> fields, escalate the weak one. The aggregate (~0.76) is unchanged across all three — proof it can't
> tell you where the routing line should fall.

| Run | threshold | AUTO-ACCEPT | HUMAN REVIEW | Verdict |
|---|---|---|---|---|
| 1 | 0.99 | (none) | all 5 fields | expected (over-cautious) |
| 2 | 0.0 | all 5 fields | (none) | expected (danger: 0.0-conf field auto-accepted) |
