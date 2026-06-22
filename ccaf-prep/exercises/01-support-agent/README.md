# Exercise 1 — Multi-Tool Support Agent with Escalation

**Lights up:** Scenario 1 (Customer Support). **Sample questions:** 1, 2, 3.
**Domains:** D1 (loop, enforcement), D2 (descriptions, structured errors), D5 (escalation, ambiguity).

## Study runbook (do this in order)

Each step maps 1:1 to a section of [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md) (the *"Files as"* column).
Read the **Expected result** column *before* you run — it's what each step is meant to teach.

> ⚠️ **Read this first — the anti-patterns are model-dependent and often DON'T reproduce.**
> On a capable model (`claude-haiku-4-5`) with these toy inputs, every anti-pattern below behaved
> *correctly* when run: Experiment A escalated the $900 refund **5/5** with the gate off; Experiment B
> routed the order question correctly **without** good descriptions. That is **expected** — not a bug
> in the exercise — and it is the real exam lesson:
>
> **A prompt that "usually works" is exactly why it's the wrong choice for irreversible / money
> operations.** No number of green runs proves a 0% failure rate, and a refund can't be un-paid. So you
> gate deterministically (`ENFORCE=True`) **regardless of how reliable the prompt looks** — "worked 5/5
> on a toy" is not "cannot fail across millions of real refunds." Watching the prompt *behave* and
> gating it anyway is a **stronger** lesson than watching it break. (Want to witness a slip anyway? Each
> experiment notes how to raise the pressure — see `SAMPLE_RUNS.md`.)

**Both toggles, every step** — the rule is *change exactly one toggle from the clean baseline per
step*, so whatever you observe is attributable to that one change. Defaults are
`ENFORCE = True` (`agent.py`) and `GOOD_DESCRIPTIONS = True` (`tools.py`); set them back between steps.

| Step | `ENFORCE` | `GOOD_DESCRIPTIONS` | What to do | Runs | Expected result — what it teaches | Files as |
|---|---|---|---|---|---|---|
| 1 | `True` | `True` | **Clean pass — change nothing.** Read *"What maps to what"* (below) while it scrolls. | **1×** | All three cases behave *correctly*: parallel tools in `turn 0`, gate allows the $240 refund but escalates the $900 one, structured validation error on the ambiguous "John Smith". The **right** pattern for each known trap. | Experiment 0 |
| 2 | **`False`** | `True` | **Experiment A — gate vs. prompt.** On the $900 case watch *two* things: does it still escalate (>$500), and does it still verify before refunding? | **3–5×** | Most likely it keeps behaving (mine: 5/5 escalated, always verified first). The point is **not** to catch a failure — it's to internalize that with the gate off *nothing guarantees* this; only `ENFORCE=True` does. The toy rarely slips; production scale eventually will. To force a visible slip, swap in the adversarial prompt in [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md#experiment-a--hook-vs-prompt--runbook-step-2-enforcefalse). (distractor #2) | Experiment A |
| 3 | `True` | **`False`** | **Experiment B — descriptions vs. routing.** Ask "check my order 12345". | **2–3×** | Most likely it still routes to `lookup_order` — the tool *names* + schemas already disambiguate, so descriptions are redundant here. The lesson holds regardless: when tools genuinely overlap, the fix the exam rewards is **better descriptions**, not a routing classifier. (distractor #1) | Experiment B |
| 4 | `True` | `True` | **Bank questions** — 20–30 on D1 + D2; re-read the matching experiment's framing on any miss. | as needed | A miss tells you which *principle* didn't stick — re-read that experiment, not just re-run it. | — |

> **Old "Experiment C" is folded into A.** The verify-before-refund skip shares Experiment A's exact
> toggle state (`ENFORCE=False`) — it's the same run, just a second thing to watch (does it call
> `get_customer` *before* the refund?). Like the escalation, it rarely slips on this toy: same lesson,
> same gate. **Reset both toggles to their defaults (`ENFORCE = True`, `GOOD_DESCRIPTIONS = True`) when done.**

### How to record a run (so it lands in `SAMPLE_RUNS.md`)
Paste me the output and say **which step number** it's from (e.g. "step 2, run 3"). I file it
under that step's section, label it `Run 1 / Run 2 / …`, and tag whether it showed the **correct**
path or the **anti-pattern** — so the variation across runs is visible at a glance. Minimum I need:
the `USER:` line (it shows the toggle state) and the `turn` lines for the case that matters —
**Case 2 ($900)** for A, the **order question** for B.

Track *your* exam progress and misses in `ccaf-prep/personal/exam_log.md`, not here.

## What's here
- `tools.py` — 4 "MCP" tools (2 deliberately similar) with structured error responses.
- `agent.py` — the agentic loop printing `stop_reason`, plus the enforcement gate.

## Run
```bash
# from the repo root, cd into this exercise folder first:
cd ccaf-prep/exercises/01-support-agent

# uv finds ../pyproject.toml and uses the ccaf-prep env; the script self-loads the
# repo-root .env via find_dotenv, so no export step is needed.
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

> **One simplification to keep straight:** the test messages ("I'm John Smith, customer C001")
> are *real* Messages API user turns — that part isn't faked. What's simplified is the **trust
> model**: a real agent never treats a self-asserted name/ID from chat as proof of identity (it
> uses an authenticated session). Here `get_customer` is a look-up doubling as "verification" so
> the **D1.4 verify-before-refund gate** is demonstrable in one file. The gate is the real lesson;
> "a typed name counts as verified" is the shortcut.

## The anti-pattern experiments (the real learning)

> These teach a **principle**, not a guaranteed failure. On a capable model + toy input the
> anti-pattern usually *won't* reproduce — and that's the point (see the ⚠️ box up top). The exam
> rewards choosing the deterministic option *regardless* of how well the prompt happens to behave.

1. **Gate vs. prompt (Q1).** Set `ENFORCE = False` in `agent.py`, rerun the $900 case. The SYSTEM
   prompt still says "refunds over $500 must be escalated" and "verify before any refund" — but with
   no gate, nothing *guarantees* the model obeys. On a capable model it almost always behaves (mine:
   5/5 escalated, always verified first), so to actually see a slip, raise the pressure with the
   adversarial prompt in `SAMPLE_RUNS.md`. → *Prompt = probabilistic even when it usually works; gate
   = deterministic.* For irreversible/money operations you pick the gate **because** "usually works"
   can't be promised. That gap is distractor pattern #2. (This also covers the old "verify-first
   skip" — same `ENFORCE=False` state, a second thing to watch.)

2. **Descriptions vs. routing (Q2).** Set `GOOD_DESCRIPTIONS = False` in `tools.py`, ask an order
   question ("check my order 12345"). On a capable model it usually still routes correctly — the tool
   *names* (`get_customer` vs `lookup_order`) and schemas disambiguate on their own. Descriptions
   matter most when tools genuinely overlap; even then the fix the exam rewards is *better
   descriptions*, not a routing classifier (distractor pattern #1).

## After this exercise
Do **20–30 bank questions on D1 + D2**. If you miss a pattern, come back and rerun the
matching experiment before moving to Exercise 4.
