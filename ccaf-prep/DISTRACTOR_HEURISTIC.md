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

How that step is actually built (prompt instruction → second call → fresh-context subagent) and why a
*separate* evaluator beats in-context self-critique: [`SELF_CRITIQUE.md`](./SELF_CRITIQUE.md).

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

## Few-shot design — when few-shot *is* the answer, what makes it the *right* few-shot

Some questions pre-commit you to few-shot ("you decide to add few-shot examples…") and then test
whether you can **design** it. Watch for that stem: it fixes the method and quietly eliminates
otherwise-tempting options (e.g. editing the tool *descriptions*), so the choice is now *which
few-shot implementation*, not *whether few-shot*.

A few-shot example is a worked demonstration **you author of the ideal behavior**: a representative
*input* (a user message of the failing kind) paired with the *output you want* — the tool chosen plus
the reasoning. The output is the gold answer you want, **not** whatever the model previously produced
(that was the bug). Three properties separate the right answer from the plausible distractors:

1. **Targeted, not voluminous.** 4–6 examples aimed at the *failing* (ambiguous) cases beat 10–15
   examples of easy/unambiguous ones. More demonstrations of cases that already work ≠ improvement.
2. **Contrastive, not grouped.** Each example shows *why this choice over the plausible alternative* —
   the decision boundary. Grouping examples by category (all tool-A cases, then all tool-B cases)
   teaches each in isolation and never teaches the model to **discriminate**.
3. **Matched to the gap's shape.** Few-shot fits *patternable* gaps (tool sequencing, contrastive
   tool choice, multi-concern decomposition). For gaps that vary *per case* (response completeness),
   no fixed example set covers them → **self-critique / evaluator-optimizer** instead.

> One more edge: for *nuanced / ambiguous* selection, worked examples-with-reasoning also beat
> **declarative rules** ("use when / do not use when" in the tool description) — demonstrations
> transfer to fuzzy inputs better than rules do. This is *different* from the
> descriptions-beat-a-router lesson (D2.1), which is about *clearly separable* tools. Same scenario,
> different sub-problem → different winner.

**One surface, two root causes — diagnose before you pick the lever.** "Multi-concern requests are
failing" can mean two different things, and few-shot answers only one of them:

- failing on **speed / efficiency** (12+ calls, redundant data re-fetching, sequential investigation)
  → **restructure**: decompose + investigate in parallel + shared context, then synthesize. This is an
  *architecture* fix (native parallel tool use + the loop's accumulated context), **not** few-shot.
- failing on **accuracy** (addresses only one concern, mixes up parameters) → **few-shot**: a
  *patternable* reasoning gap; single-concern already works, so just teach the multi-concern pattern.

Ask *"is it failing on speed or on correctness?"* first — the words "multi-concern" alone don't tell
you, and the wrong reading picks few-shot when you needed to restructure (or vice versa).

---

## Concept deep-dives (index)

Focused write-ups that grew out of specific practice-exam questions. Each is its own file so it stays
tight and links cleanly; this table is the front door. Sorted by the domain the concept lives in.

| Concept | Domain | Where |
|---|---|---|
| The key question (native/deterministic vs moving part) + the 5 patterns | all | this file (top) · [`ANALYSIS.md`](./ANALYSIS.md) |
| Parallel tool use (default-on, round-trip math) **+ vs the Batch API** | D1 / D2 (vs D4) | [`exercises/01-support-agent/PARALLEL_TOOL_USE.md`](./exercises/01-support-agent/PARALLEL_TOOL_USE.md) |
| Multi-concern: same surface, two root causes (speed → restructure, accuracy → few-shot) | D1.4 | this file, *§ One surface, two root causes* |
| Few-shot design (targeted · contrastive · matched to the gap) | D2 / D4 | this file, *§ Few-shot design* |
| Self-critique / evaluator-optimizer (the cheap→rigorous spectrum) | D1 | [`SELF_CRITIQUE.md`](./SELF_CRITIQUE.md) |
| Graceful degradation / error propagation (preserve value + annotate gaps; retry at the right boundary) | D1 / D5 | [`GRACEFUL_DEGRADATION.md`](./GRACEFUL_DEGRADATION.md) |

> **Placement rule** (keeps these from scattering): a write-up that explains a *specific exercise's
> behavior* lives in that exercise's folder (e.g. `PARALLEL_TOOL_USE.md` next to Exercise 1's Case 1);
> a *general pattern* not demonstrated by any exercise lives here at the `ccaf-prep` root
> (`SELF_CRITIQUE.md`). Short discriminators stay inline in this file.
>
> **Private notes are not here.** Verbatim exam questions + my own answers live in git-ignored
> `personal/` (not redistributed). The docs above teach the *concept* only — no answer keys.
