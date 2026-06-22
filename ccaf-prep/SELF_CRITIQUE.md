# Self-critique / evaluator-optimizer — the pattern Exercise 1 doesn't show

> Exercise 1's code doesn't demonstrate this one (there's no draft→critique→revise step in
> `exercises/01-support-agent/agent.py`). It's the right fix when **response quality varies
> case-by-case** — the gap that few-shot *can't* cover. Companion to the self-critique caveat in
> [`DISTRACTOR_HEURISTIC.md`](./DISTRACTOR_HEURISTIC.md).

## The question it answers

*"Response completeness varies per case — sometimes a policy detail is missing, sometimes a timeline,
sometimes next steps. How do you improve quality without adding human review?"* → **Add a self-critique
/ evaluator step.** Not few-shot (the gaps differ every time, so a fixed example set can't anticipate
them); a critique step **reasons about *this* response's completeness**, so it generalizes to gaps you
never enumerated.

## How it's actually built — a spectrum (cheap → rigorous)

All three are valid. The exam tests the *pattern*, not the wiring; the choice below is a real-world
rigor/cost decision.

| # | How it's built | API calls | Tradeoff |
|---|---|---|---|
| 1 | **Prompt instruction, one pass.** System prompt says *"Draft a reply, then critique it against [completeness criteria], then output the revised final."* The model does draft→critique→revise in one generation. | 1 | Cheapest. Weakest — the model is **anchored** to its own draft and tends to bless it. |
| 2 | **Explicit second call (evaluator-optimizer loop).** Call 1 produces the draft; call 2 (same model, *evaluator* prompt + rubric) scores it and returns gaps; call 3 revises. Loop until it passes or hits a max-iterations cap. | 2–N | Stronger — the evaluator turn reasons *about* the draft. Costs more. |
| 3 | **Separate subagent / fresh context.** Spawn a verifier subagent with its own completeness guidelines, hand it the draft, it returns structured feedback, the main agent revises, *then* sends to the user. | 2+ | Most rigorous. A **fresh-context** evaluator catches more because it isn't anchored to the main agent's reasoning. |

**Key insight:** a *separate* evaluator (level 2 with a clean evaluator prompt, or level 3 with a
subagent) generally beats in-context self-critique (level 1) — same-context critique suffers from the
model confirming its own work. So "route it to a subagent that verifies against guidelines and feeds
back" is the **strongest** pattern, not overkill.

## It's a real, named pattern with real implementations

- **Claude API / Agent SDK:** "evaluator-optimizer" is a documented agent workflow — a generator and
  an evaluator in a loop, each a prompt (optionally *different* models: cheap generator + stronger
  evaluator, or vice-versa).
- **Managed Agents has it built in:** `user.define_outcome` with a **rubric** runs a server-side
  iterate→grade→revise loop where a **separate grader (independent context window)** scores each draft
  against your criteria and feeds per-criterion gaps back. That's literally level 3, managed for you.

## Few-shot vs self-critique — which fits the gap's shape?

This is the discrimination the exam rewards (see `DISTRACTOR_HEURISTIC.md`):

| Gap shape | Fix |
|---|---|
| **Patternable** — same reasoning step missing every time (tool sequencing, multi-concern decomposition) | **Few-shot** examples |
| **Variable per case** — different things missing each time (response completeness) | **Self-critique / evaluator-optimizer** |

Few-shot encodes a *fixed* set of cases; self-critique *reasons per response*. When nothing fixed can
cover the gap, the per-response evaluation wins — that's why it's the answer here even though it *adds*
a step (the one place the "prefer the lighter option" heuristic correctly inverts).

## For exam day

The exam answer is just *"add a self-critique step"* — it does **not** prescribe prompt-vs-subagent.
Recognizing **self-critique / evaluator-optimizer is the right pattern for per-case-variable gaps**
(vs few-shot for patternable ones) is the entire test. Don't over-think the wiring under time
pressure — levels 1–3 are an implementation detail, not what's being graded.
