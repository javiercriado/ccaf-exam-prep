# Graceful degradation & error propagation in multi-agent systems

> When an upstream step **partially** fails (some sources succeed, some time out), what should a
> downstream agent do? The right move is **graceful degradation with transparency** — and the thing
> you "propagate" is not the error and not a retry, but the **coverage / uncertainty information**.
> A D1 (orchestration) + D5 (reliability) pattern. Companion to the distractor patterns in
> [`ANALYSIS.md`](./ANALYSIS.md).

## The principle

A partial failure is **not** a total failure. The goal is to **preserve the value of the work that
succeeded** while **making the gaps explicit**, so downstream consumers (other agents, or the end user)
can judge confidence and decide what to trust. Producing a result *and annotating what's missing* beats
both throwing the result away and hiding the gap.

> **"Error propagation" ≠ propagate the error.** In a pipeline, the useful thing to pass downstream is
> *structured knowledge of what's covered vs. missing* (a coverage annotation, a confidence flag), not
> a raw failure that halts the chain, and not a silent omission that hides it.

## The four responses to a partial failure (spectrum)

| Response | What it does | Why it's wrong (or right) |
|---|---|---|
| **Fail everything** | Return an error upstream → full retry or task failure | **Over-reaction.** Discards all the completed work (the sources that *did* succeed, the analysis that *did* run) over a partial gap. |
| **Hide the gap** | Proceed using only what succeeded, with no indication anything is missing | **Under-reaction.** Loses transparency — downstream can't tell the output is partial, so it can't calibrate confidence. Silent degradation. |
| **Retry from downstream** | A *late-stage* agent reaches backward and asks an earlier stage to retry the failed step before continuing | **Wrong component / wrong stage** (distractor pattern #3). Retry-with-backoff is a *good* strategy — but it belongs at the **error boundary** (the coordinator ↔ the failing subagent, *when* the failure occurred), not driven by a consumer that runs after that decision was already made. Often paired with an "ensure complete coverage before proceeding" tell — the over-engineering assumption that you must have *everything* before producing *anything*. |
| **Degrade gracefully + annotate** | Produce output from what succeeded **and** mark which parts are well-supported vs. which have gaps from unavailable inputs | ✅ **Correct.** Preserves completed value *and* propagates uncertainty so informed confidence decisions can be made downstream. |

## The discriminator

When two options both "handle" the partial failure, ask:

> **Does it (a) preserve the completed work, AND (b) make the gaps explicit for a downstream confidence
> decision?**

Only graceful-degradation-with-transparency does both. "Fail everything" fails (a); "hide the gap"
fails (b); "retry from downstream" fixes the problem in the wrong place (and may never terminate if the
flaky inputs keep timing out).

## Two traps worth naming

1. **Whose job is the retry?** Retrying a flaky step is owned by whoever sits at the **error boundary**
   — the coordinator deciding about the subagent that failed, *at the moment of failure*. A downstream
   stage (synthesis, reporting) demanding an upstream retry inverts control flow and re-opens a closed
   decision. Same lesson as "blame the coordinator's decomposition, not the subagents" — **locate the
   decision at the right component.**
2. **"Complete coverage before proceeding" is usually a tell.** Some inputs legitimately fail and may
   keep failing; blocking all output on 100% completeness is the wrong tradeoff. Ship the supported
   findings, flag the gaps, move on.

## Where it generalizes

This isn't multi-agent-only. Any pipeline with partial inputs follows it:

- A single agent whose tool returns a partial result → **return the partial + annotate** what's missing
  (structured `is_error` on the failed call, success on the rest), not a blanket failure.
- A report generator missing one data source → produce the report with a "coverage" / "data gaps"
  note, not a blank page or a silent omission.

Same shape every time: **keep the value, surface the uncertainty, fix failures at the boundary where
they happen.**
