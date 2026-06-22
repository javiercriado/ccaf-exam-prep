# Proactive task decomposition — partition the work before delegating

> When parallel agents redundantly investigate the same things (overlapping findings; token usage spikes
> with no added breadth or depth), the root cause is usually **unclear task boundaries** — the
> coordinator delegated without partitioning the work. Fix it **at decomposition time, before
> delegation**, and keep parallelism. A D1 (orchestration) pattern; the coordinator's *decomposition* is
> the thing to fix (distractor pattern #3). Companion to [`HUB_AND_SPOKE.md`](./HUB_AND_SPOKE.md) and
> [`GRACEFUL_DEGRADATION.md`](./GRACEFUL_DEGRADATION.md).

## The principle

A coordinator's core job is to **decompose a task into non-overlapping subtasks** and hand each agent a
distinct scope. Redundant work across agents is a **decomposition failure**, not an agent failure — each
agent did reasonable work; the coordinator never drew the boundaries. So the fix belongs **up front, at
the coordinator, before any agent starts**: partition the space (by subtopic *or by source type*) and
delegate distinct slices.

> The multi-agent face of distractor pattern #3: when parallel agents collide, **suspect the
> coordinator's decomposition, not the subagents.**

## Why "before delegation" beats the alternatives

The redundant-overlap problem has a tempting fix at each *later* stage — all weaker than partitioning up
front:

| When the fix acts | Shape | Why it's weaker |
|---|---|---|
| **Before delegation** (partition) ✅ | Coordinator assigns distinct subtopics / source types, then delegates | Removes overlap *at the source*, **keeps full parallelism**, no wasted tokens, no extra machinery. Root-cause fix. |
| **During** (shared state) | Agents log their focus so others dynamically avoid it | Reactive + racy: agents still start overlapping and course-correct mid-flight; adds a coordination mechanism (a moving part) to do what a clean upfront split does for free. |
| **After** (post-hoc dedup) | Let both finish, then deduplicate before synthesis | The wasted tokens are **already spent** — dedup cleans the *findings* but not the *cost*, which was the stated problem. Symptom, not cause. |
| **Instead** (serialize) | Make one agent wait and use the other's output as context | **Throws away parallelism** to avoid duplication — over-correction; serializes work that was genuinely parallel. |

## Partition by subtopic *or by source type* — the nuance that resolves the doubt

"Both agents overlap" can feel artificial when the agents pull from *different sources* (e.g. the web vs
internal documents) — covering the same subtopic from two sources is often desirable **triangulation,
not waste**. Resolution: proactive partitioning can split by **source type**, not only by subtopic.
Assign "web-facing agent → web sources, document agent → internal documents" and you **keep both
sources** (the coverage you want) while removing the *redundant subtopic chasing* (the waste you don't).
The upfront-partition fix is flexible enough to preserve legitimate multi-source coverage — it doesn't
force you to drop a source.

So when a scenario *stipulates* the overlap is wasteful (tokens up, breadth/depth flat), take that as
given; the fix is to draw boundaries, and "by source type" is how you keep genuinely-different sources.

## The discriminator

When parallel agents duplicate work, ask: **does the fix draw clear boundaries *before* work starts, or
react / clean up / serialize *after*?** Proactive partitioning at the coordinator wins — the root-cause
fix that preserves parallelism. Reactive coordination, post-hoc dedup, and serialization each either add
a moving part, pay the waste anyway, or kill the parallelism you wanted.
