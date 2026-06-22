# Hub-and-spoke: why route subagent communication through the coordinator

> In a multi-agent system, should subagents talk to each other directly, or route everything through
> the coordinator? The exam rewards the **coordinator-as-central-hub** (hub-and-spoke) pattern — and
> the *reason* it rewards is specific. A D1 (orchestration) pattern; companion to
> [`GRACEFUL_DEGRADATION.md`](./GRACEFUL_DEGRADATION.md) (the coordinator is the error boundary).

## The three real advantages

Keeping the coordinator as the single hub for all subagent communication buys you:

1. **Observability** — the coordinator sees *every* interaction. One place to log, trace, and debug the
   whole system; nothing happens "off to the side" between two subagents.
2. **Consistent error handling** — failures surface at one boundary and are handled uniformly (retries,
   escalation, graceful degradation). This is *why* partial-failure decisions belong at the coordinator
   — see `GRACEFUL_DEGRADATION.md`.
3. **Context control** — the coordinator decides **what information each subagent receives**. Subagents
   don't inherit context automatically; the hub hands each one a clean, scoped brief, which prevents
   context bleed and keeps each subagent focused (D1.3).

That's the answer to "why keep the coordinator in the middle": **visibility + consistent control**, not
speed.

## Why the *tempting* reasons are wrong

Each is a true-sounding fact that does **not** capture the main advantage:

- **"Direct communication needs serialization only the coordinator can do."** Subagents *do* have
  isolated memory (true), but exchanging structured output isn't a coordinator-only power — direct
  agents could serialize too. The isolation is real; the *exclusivity* is invented.
- **"The coordinator batches requests, cutting API calls / latency."** Batching is a real technique, but
  it isn't what hub-and-spoke is *for* — routing through a hub adds a hop and can *increase* latency.
  The benefit is control, not speed.
- **"Routing enables retry that direct calls can't support."** A coordinator makes retry *consistent*,
  but direct agent-to-agent calls can implement retry too. The hub centralizes it; it doesn't uniquely
  enable it.

Pattern to notice: each wrong reason pairs a **true fact** with a **false exclusivity** ("only…",
"cannot…") or a **misattributed benefit** (a real efficiency cited as *the* advantage). See the
"compound distractor" technique in [`DISTRACTOR_HEURISTIC.md`](./DISTRACTOR_HEURISTIC.md).

## The honest tradeoff

Hub-and-spoke isn't free: the coordinator is an extra hop and a potential bottleneck / single point of
failure. You accept that **on purpose** — you're buying central observability and consistent control.
Direct (mesh) communication is leaner but loses the single vantage point. The exam's "main advantage"
question is asking which property you're *buying*, and the answer is visibility + control, not latency.

## Where it's demonstrated

`exercises/04-multi-agent-research/coordinator.py` is a hub-and-spoke coordinator — the subagents return
to the coordinator, which controls context (`PASS_CONTEXT`) and dispatch (`DYNAMIC_SELECTION`). This doc
states the *principle* the exam tests; that exercise is where you can watch it run.
