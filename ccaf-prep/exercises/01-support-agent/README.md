# Exercise 1 — Multi-Tool Support Agent with Escalation

**Lights up:** Scenario 1 (Customer Support). **Sample questions:** 1, 2, 3.
**Domains:** D1 (loop, enforcement), D2 (descriptions, structured errors), D5 (escalation, ambiguity).

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
