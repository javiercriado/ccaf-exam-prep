# The Distractor Heuristic — two axes for picking the right answer

> A companion to the **5 distractor patterns** in [`ANALYSIS.md`](./ANALYSIS.md). Where that
> section *names* the traps, this doc gives you a **single question to ask** when two options
> both look correct. The CCAF exam is ~80% distractor discrimination — this is the reflex it tests.

## The key question

When two options both "work," the wrong one is almost always the **heavier** one. Ask two things:

### Axis A — Native capability, or a new moving part?
Does this option use something the tool/model **already has** — a CLI flag, parallel tool use,
existing frontmatter — or does it **add something new** that has to be maintained and can fail:
a second LLM call, a preprocessing model, a bespoke composite tool, an invented feature?

> **"Native" also means "actually exists."** Options that lean on a flag or frontmatter key you
> can't quite remember seeing (`override: true`, `--batch`, `CLAUDE_HEADLESS`) are often bait —
> distractor pattern #4 (nonexistent features).

### Axis B — Deterministic, or relying on the model to behave?
Does this option **guarantee** the behavior by construction — a programmatic gate, a JSON schema,
a hook — or does it **ask the model nicely** via a prompt instruction?

**The correct answer tends to be native and/or deterministic. The distractor is the version with
moving parts.**

## The shapes, illustrated

| Problem shape | Distractor (heavier) | Correct (native / deterministic) |
|---|---|---|
| Need structured output from a CLI | Add a second LLM call to summarize narrative → JSON | `--output-format json` + `--json-schema` (native, guarantees well-formed JSON) |
| Too many sequential tool round-trips | Build composite `get_x_with_y` tools (new tool per combination) | Prompt the model to batch tool requests in one turn (it natively requests several at once) |
| Agent mishandles multi-part requests, but nails single ones | A separate preprocessing model to decompose the message | Few-shot examples in the prompt (lean; the capability already works) |
| Conventions must apply on every matching file | A skill the model must choose to load | A **rule** with a glob (automatic + deterministic by path) |
| Customize a teammate's shared skill | `override: true` frontmatter (doesn't exist) | Personal skill with a **different name** (`/my-x`) |
| Agent skips a required verification step | Strengthen the system prompt to say it's mandatory | A **programmatic prerequisite** that blocks the downstream tool until verification ran |

The last row is the canonical Axis-B case: a **gate/hook beats an instruction** because it holds
regardless of how the model behaves. (Same lesson as enforcement-by-hook, not by prompt.)

## The caveat that stops you over-applying it

The rule is **not** "always pick the simplest option." Sometimes the correct answer *adds* a step:

> **Inconsistent, case-by-case-variable output** (e.g. response completeness that varies per case):
> the right fix is a **self-critique / evaluator-optimizer** step — which adds a pass — over
> few-shot examples that can only cover a fixed set of cases.

Why doesn't the added step lose on Axis A? Because no lean option actually solves it: a handful of
canned examples can't cover gaps that differ every time. **When nothing lightweight genuinely solves
the problem, the pattern that fits the problem's shape wins.**

### Refined rule

> Between two options that both "work," prefer the one that **uses an existing capability** or
> **guarantees the outcome by construction** — *unless* the problem's shape genuinely needs a
> pattern (self-critique for per-case-variable gaps). The distractor is usually the **heavier
> version of something a native option already does.**

And the corollary for prompting technique: **few-shot fits *patternable* gaps** (tool sequencing,
contrastive tool choice); **self-critique fits *variable-per-case* gaps**. Same question either way —
*which option fits the shape of the problem?*
