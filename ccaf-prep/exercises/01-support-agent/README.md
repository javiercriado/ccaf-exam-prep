# Exercise 1 — Multi-Tool Support Agent with Escalation

**Lights up:** Scenario 1 (Customer Support). **Sample questions:** 1, 2, 3.
**Domains:** D1 (loop, enforcement), D2 (descriptions, structured errors), D5 (escalation, ambiguity).

## Study runbook (do this in order)

Each step maps 1:1 to a section of [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md) (the *"Files as"* column).
Read the **Expected result** column *before* you run — it's the specific thing each run is meant to
prove. The anti-pattern steps are non-deterministic, so a single run proves nothing; that's why
**Runs** says 3–5× — you run them until you *catch* the failure described.

| Step | What to do | Runs | Expected result — what you're trying to prove | Files as |
|---|---|---|---|---|
| 1 | **Clean pass — change nothing.** Run it, read *"What maps to what"* (below) while it scrolls. | **1×** | All three cases behave *correctly*: parallel tools in `turn 0`, gate allows the $240 refund but escalates the $900 one, structured validation error on the ambiguous "John Smith". This is the **right** pattern for each known trap. | Experiment 0 |
| 2 | **Experiment A — hook vs. prompt** (`ENFORCE = False`). Watch Case 2 ($900). | **3–5×** | At least one run where `turn 1` calls `process_refund({amount: 900})` instead of `escalate_to_human`. That one slip proves **prompt-only enforcement is probabilistic** — a gate would make it impossible. (distractor #2) | Experiment A |
| 3 | **Experiment B — descriptions vs. routing** (`GOOD_DESCRIPTIONS = False`; ask "check my order 12345"). | **2–3×** | At least one run where `turn 0` misroutes the order question to `get_customer` instead of `lookup_order`. Proves **bad descriptions cause misrouting** — the fix is better descriptions, not a routing classifier. (distractor #1) | Experiment B |
| 4 | **Experiment C — verify-first skip** (`ENFORCE = False`, give an order detail up front). | **3–5×** | A run where the model **skips `get_customer`** and goes straight to the order/refund. The skip is rare (~1 in 8), so several clean runs are expected — that rarity is the point: it's exactly why verification belongs in a gate, not a prompt. (sample Q1) | Experiment C |
| 5 | **Bank questions** — 20–30 on D1 + D2; re-run the matching experiment on any miss. | as needed | A miss tells you which experiment to re-run; re-running until you *see* the failure cements the reflex. | — |

> **Why several runs (steps 2 & 4)?** These study *probabilistic* failure: with the gate off, the
> prompt usually still behaves, and the bug only surfaces in a minority of runs. Running once and
> seeing correct behavior is the trap — it "proves" the prompt works. Running 3–5× and seeing it
> break *once* is the lesson (distractor pattern #2). **Reset the toggle to its default when done.**

### How to record a run (so it lands in `SAMPLE_RUNS.md`)
Paste me the output and say **which step number** it's from (e.g. "step 2, run 3"). I file it
under that step's section, label it `Run 1 / Run 2 / …`, and tag whether it showed the **correct**
path or the **anti-pattern** — so the variation across runs is visible at a glance. Minimum I need:
the `USER:` line (it shows the toggle state) and the `turn` lines for the case that matters —
**Case 2 ($900)** for A, the **order question** for B, **Case 1 (Maria)** for C.

Track *your* exam progress and misses in `ccaf-prep/personal/exam_log.md`, not here.

## What's here
- `tools.py` — 4 "MCP" tools (2 deliberately similar) with structured error responses.
- `agent.py` — the agentic loop printing `stop_reason`, plus the enforcement gate.

## Run
```bash
# from this folder — uv finds ../pyproject.toml and uses the ccaf-prep env.
# the script self-loads ../../claude-with-anthropic-api/.env, so no export step is needed.
uv run python agent.py
```
(If `claude-sonnet-4-6` isn't available on your key, set `CLAUDE_MODEL` in the `.env`, or
change `MODEL` in `agent.py`.)

## What maps to what (read while the output scrolls)

| You see in the output | Task Statement |
|---|---|
| `stop_reason=tool_use` → loop continues; `end_turn` → it stops | **D1.1** agentic loop |
| `MAX_TURNS` is a *safety backstop*, not the stop condition | **D1.1** anti-pattern avoided |
| tool results appended as `{"type":"tool_result", ...}` then re-sent | **D1.1** context accumulation |
| `GATE blocked process_refund` until `get_customer` ran | **D1.4 / Q1** prereq enforcement |
| `errorCategory` / `isRetryable` in every failure | **D2.2** structured errors |
| the two `*_desc` strings in `tools.py` | **D2.1 / Q2** descriptions drive selection |
| "2 customers named John Smith → ask for an identifier" | **D5.2** multi-match, don't guess |
| escalation carries a full `handoff_summary` | **D1.4** structured handoff |

## The 3 anti-pattern experiments (the real learning)

1. **Hook vs. prompt (Q1).** Set `ENFORCE = False` in `agent.py`, rerun the $900 case a
   few times. The SYSTEM prompt still says "refunds over $500 must be escalated," but with
   no gate the model will sometimes call `process_refund` anyway. → *Prompt = probabilistic,
   gate = deterministic.* This is distractor pattern #2.

2. **Descriptions vs. routing (Q2).** Set `GOOD_DESCRIPTIONS = False` in `tools.py`, ask an
   order question ("check my order 12345"). With minimal descriptions the model misroutes to
   `get_customer`. The fix the exam rewards is *better descriptions* — not a routing
   classifier (distractor pattern #1).

3. **Verify-first skip.** With `ENFORCE = False`, give it an order detail up front
   ("refund order 12345 for Maria"). Watch whether it skips `get_customer`. That 12%-skip
   behavior is exactly the failure in sample Q1.

## After this exercise
Do **20–30 bank questions on D1 + D2**. If you miss a pattern, come back and rerun the
matching experiment before moving to Exercise 4.
