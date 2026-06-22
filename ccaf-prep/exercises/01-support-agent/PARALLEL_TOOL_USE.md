# Parallel tool use — how Case 1's `turn 0` works

> The mechanism behind the 🎯 in [`SAMPLE_RUNS.md`](./SAMPLE_RUNS.md) Case 1: why `get_customer` and
> `lookup_order` come back **in the same `turn 0`**, and why that's the answer to the "reduce
> round-trips" trap (composite tools are the distractor). Verified against the Claude API reference
> (tool-use concepts), not just observed.

## What "parallel tool use" actually is

A single assistant response can contain **multiple `tool_use` blocks**. That's parallel tool use: the
model *requests* several tools at once, in one turn, so you can resolve them all before the next API
call. In Case 1, `turn 0` carries two `tool_use` blocks (`get_customer` + `lookup_order`).

It is **on by default**. You don't configure or enable it:

- Pass `tools=[...]` (names, descriptions, input schemas) + the prompt. That's it.
- There's a flag to turn it **off**, not on: `tool_choice={..., "disable_parallel_tool_use": true}`
  forces at most one tool per turn. Default = parallel allowed.
- The model **decides** whether to batch — "default-on" means *permitted*, not *guaranteed*. A prompt
  can nudge it ("if several independent lookups are needed, request them together"). That nudge — over
  a native, already-on capability — is the correct fix for too many round-trips, **not** building
  composite `get_x_with_y` tools (a new tool to maintain per combination = the distractor).

## Why it reduces round-trips (the cost being saved)

Each loop iteration = one `messages.create` call = one API round-trip. For the two-tool case:

| | turn 0 | turn 1 | turn 2 | **API calls** |
|---|---|---|---|---|
| **Parallel** | both `tool_use` blocks | final answer (`end_turn`) | — | **2** |
| **Sequential** | `get_customer` only | `lookup_order` only | final answer | **3** |

It isn't literally "1 call per tool" total — but **each additional tool done sequentially adds one
round-trip**, and parallel collapses N tool-producing turns into one. That round-trip count is the
cost the "4+ API round-trips per resolution" complaint is about.

## What "parallel" does NOT mean

It means the model **requests** the tools together — it does **not** mean your tool functions run
concurrently. In `agent.py` the `tools.DISPATCH[...]` calls still execute one-after-another inside the
`for block in resp.content` loop. That's fine: they're local, instant fixture calls, so they're free.
**The thing being optimized is API round-trips, not local execution time.** (In production you *could*
run the real tool calls concurrently with threads/async — a separate optimization from the API-level
batching.)

## Where this lives in `agent.py`

- The model emitting 1 *or many* `tool_use` blocks is handled by the **inner** `for block in
  resp.content` loop — it iterates over however many tool calls come back and collects all results.
- All `tool_result` blocks then go back in **one** user message (`messages.append({"role": "user",
  "content": results})`) — the API expects every parallel `tool_use` answered in a single following
  turn, never split across messages.

So Case 1's "both calls in `turn 0`" needs no special handling — the loop already supports any number
of `tool_use` blocks per turn. The only variable is whether the model *chose* to batch.

## Related: Q58 vs Q48 — same pillar, different scope

The "too many round-trips" question (Q58) and the "complex multi-part request" question (Q48) rest on
the **same** native capability — parallel tool use — but Q48 is a **superset**:

| | Q58 (round-trips) | Q48 (complex multi-part) |
|---|---|---|
| Symptom | 4+ round-trips; tools called in separate sequential turns | 12+ calls, low resolution — sequential **and** redundant data re-fetching |
| Fix pillars | **parallel** (batch the calls) | **decompose** concerns + **parallel** + **shared context** (fetch the customer once, reuse it) |

Q58's answer is *one pillar* of Q48's answer. The parallel-tool-use piece is identical; Q48 adds
decomposition (handle every concern) and context reuse (don't re-pull the same customer per concern).
Same default-on capability either way — neither needs special configuration to make tools run in parallel.

## ⚠️ Do not confuse this with the Batch API ("batch processing")

These are **two different concepts**; conflating them is a classic distractor trap:

| | Parallel tool use *(this doc — D1/D2)* | Batch API / "batch processing" *(D4, CI scenario)* |
|---|---|---|
| What | Multiple `tool_use` blocks in **one assistant turn** | The `/v1/messages/batches` endpoint — many **independent requests** submitted together |
| Config | **None** — default-on | **Deliberate setup** — different endpoint, `custom_id`, async polling |
| Speed | Faster (fewer round-trips) in a **live** conversation | **Slower**: up to 24h, **no latency SLA** — but **50% cheaper** |
| Use case | Speed up a single agent resolution | Latency-**tolerant** bulk work (overnight reports, backfills) |

"Call two tools in one turn" = **parallel tool use** = free/default. "Batch processing" = **Batch API**
= a configured, async, cheaper-but-slower endpoint for a totally different job. Keep them in separate
mental boxes: a CI question (Batch API) and a Customer Support question (parallel tools) can both
*look* right when only one fits the scenario.
