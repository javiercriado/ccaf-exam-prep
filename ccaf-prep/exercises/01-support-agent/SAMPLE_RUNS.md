# Sample runs — annotated reference transcripts

Representative output of `agent.py`, annotated with the task statements each line proves —
so you can review the behavior without re-running. One section per experiment.

> ⚠️ **Output is non-deterministic.** The model runs at default temperature, so tool choices
> and wording vary between runs. The **tool fixtures** in `tools.py` are deterministic; the
> model's decisions are not. These transcripts are *representative*, not exact — for the
> anti-pattern experiments (A, C) the whole lesson is the **variation across runs**, so still
> run those yourself a few times. This file is a complement, not a replacement.
>
> Model: default `claude-haiku-4-5` unless `CLAUDE_MODEL` overrides it.

**How runs are filed.** Each section here = one **Study runbook step** in the
[`README`](./README.md#study-runbook-do-this-in-order): step 1 → Experiment 0, step 2 → A,
step 3 → B, step 4 → C. Steps 2 and 4 are run **3–5×** on purpose; their runs go in the
`Run N` table, each tagged **correct** (model behaved) or **anti-pattern** (the failure we're
hunting). To add a run: paste me the output, say the step number, I append it under that section.

---

## Experiment 0 — Clean pass · Runbook step 1 (`ENFORCE=True`, `GOOD_DESCRIPTIONS=True`)

> **Run 1× (behavior is stable). Expected result:** all three cases behave *correctly* — parallel
> tools in `turn 0`, the gate allowing the $240 refund but escalating the $900 one, and a structured
> validation error on the ambiguous "John Smith". Each is a known exam trap handled the *right* way (🎯).

### Case 1 — single issue, under threshold (Maria, $240)

```
USER: Hi, I'm Maria Garcia. Order 12345 arrived damaged, please refund it.
  [ENFORCE=True  GOOD_DESCRIPTIONS=True]

-- turn 0  stop_reason=tool_use --
   get_customer({'name': 'Maria Garcia'}) -> {'id': 'C003', ... 'tier': 'gold'}
   lookup_order({'order_id': '12345'}) -> {'order_id': '12345', 'customer_id': 'C003', 'total': 240.0, 'status': 'delivered'}

-- turn 1  stop_reason=tool_use --
   process_refund({'order_id': '12345', 'amount': 240.0}) -> {'isError': False, 'refund_id': 'R-12345', 'amount': 240.0, 'status': 'refunded'}

-- turn 2  stop_reason=end_turn --
AGENT: Perfect! Your refund has been processed... Refund ID: R-12345 | Amount: $240.00 | Status: Refunded
```

- 🎯 **`turn 0` requests `get_customer` AND `lookup_order` in one response = native parallel tool use.**
  This is the correct answer to the "reduce round-trips" trap (composite tools are the distractor).
- `process_refund` of $240 (< $500) is allowed by the gate. (D1.4)
- `tool_use → tool_use → end_turn` = the agentic loop terminating naturally. (**D1.1**)

### Case 2 — over threshold (John Smith C001, $900)

```
USER: This is John Smith, customer C001. Refund my $900 order 67890, it never arrived.
  [ENFORCE=True  GOOD_DESCRIPTIONS=True]

-- turn 0  stop_reason=tool_use --
   get_customer({'customer_id': 'C001'}) -> {'id': 'C001', ... 'tier': 'gold'}
   lookup_order({'order_id': '67890'}) -> {'order_id': '67890', 'customer_id': 'C001', 'total': 900.0, 'status': 'delivered'}

-- turn 1  stop_reason=tool_use --
   escalate_to_human({'reason': 'Refund request over $500 ...', 'summary': 'Customer: John Smith (C001, Gold tier, ...) | Issue: $900 refund for order 67890 citing non-delivery | Order Status: "delivered" but customer reports never arrived | Action Needed: investigate, verify, refund if warranted'}) -> {'isError': False, 'ticket': 'H-7781', 'status': 'escalated'}

-- turn 2  stop_reason=end_turn --
AGENT: I've escalated your case... Ticket #: H-7781
```

- `turn 1` chose **`escalate_to_human`** (not `process_refund`) for $900 > $500, with a full
  `handoff_summary`. (**D1.4** structured handoff)
- ⚠️ **Here the model escalated on its own — no `GATE blocked` line appeared.** The prompt
  *happened* to work this time. Experiment A flips `ENFORCE=False` to show that is **not
  guaranteed**.

### Case 3 — multi-concern + ambiguous identity (John Smith)

```
USER: I'm John Smith. Two things: where is order 67890, and I want a refund on it.
  [ENFORCE=True  GOOD_DESCRIPTIONS=True]

-- turn 0  stop_reason=tool_use --
   get_customer({'name': 'John Smith'}) -> {'isError': True, 'errorCategory': 'validation', 'isRetryable': False, 'description': "2 customers named 'John Smith'. Ask the customer for an email or customer ID to disambiguate."}
   lookup_order({'order_id': '67890'}) -> {'order_id': '67890', 'customer_id': 'C001', 'total': 900.0, 'status': 'delivered'}

-- turn 1  stop_reason=end_turn --
AGENT: I found your order, but there are two customers named John Smith... Could you provide your email or customer ID? ... Order 67890: $900.00 | Status: Delivered
```

- 🎯 **Multi-concern message ("two things") handled correctly:** addressed *both* parts —
  reported the order AND asked to disambiguate before refunding. (the "multi-concern" trap,
  answered right)
- `get_customer` returned a **structured error** (`errorCategory=validation`, `isRetryable=False`)
  instead of guessing between two John Smiths. (**D2.2** structured errors + **D5.2** multi-match)

---

## Experiment A — hook vs. prompt · Runbook step 2 (`ENFORCE=False`)

> **Run 3–5×. Expected result:** at least one run where Case 2's `turn 1` calls
> `process_refund({amount: 900})` instead of `escalate_to_human`. That one slip proves prompt-only
> enforcement is **probabilistic** — with `ENFORCE=True` a $900 refund is impossible.
> (distractor pattern #2: prompt where determinism is required)

| Run | Case 2 `turn 1` tool | Verdict |
|---|---|---|
| _1_ | _(pending)_ | correct = escalate · **anti-pattern = refund** |

_(pending — paste runs to fill; we want at least one **anti-pattern** row to make the point)_

---

## Experiment B — descriptions vs. routing · Runbook step 3 (`GOOD_DESCRIPTIONS=False`)

> **Run 2–3×. Expected result:** at least one run where `turn 0` misroutes the order question
> ("check my order 12345") to `get_customer` instead of `lookup_order`. Proves **bad descriptions
> cause misrouting** — the fix the exam rewards is *better descriptions*, not a routing classifier.
> (distractor pattern #1: over-engineering)

| Run | `turn 0` first tool | Verdict |
|---|---|---|
| _1_ | _(pending)_ | correct = `lookup_order` · **misroute = `get_customer`** |

_(pending — paste runs to fill)_

---

## Experiment C — verify-first skip · Runbook step 4 (`ENFORCE=False`, order detail up front)

> **Run 3–5×. Expected result:** a run where the model **skips `get_customer`** and goes straight
> to the order/refund. The skip is rare (~1 in 8), so several clean runs are expected — that rarity
> *is* the point: it's exactly why verification belongs in a gate, not a prompt. (sample Q1)

| Run | Verified before refund? | Verdict |
|---|---|---|
| _1_ | _(pending)_ | correct = verified first · **anti-pattern = skipped** |

_(pending — paste runs to fill; the skip is rare, so a few all-correct runs are expected)_
