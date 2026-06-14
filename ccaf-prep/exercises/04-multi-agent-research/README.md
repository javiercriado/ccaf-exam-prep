# Exercise 4 — Coordinator–Subagent Multi-Agent Research

**Lights up:** Scenario 2 (Multi-Agent Research). **Sample questions:** 7, 8.
**Domains:** D1 (hub-and-spoke, context passing), D2 (per-subagent tool scoping), D5 (error propagation, scratchpad, provenance).

## What's here
- **`coordinator_sdk.py` — the PRIMARY artifact: REAL Agent SDK delegation.** A coordinator
  whose only tool is `Task` (`allowed_tools=["Task"]`) genuinely spawns `weather` + `landmark`
  subagents, each an `AgentDefinition` owning a scoped in-process `@tool`; the SDK isolates each
  subagent's context. This is the actual mechanism the exam tests (D1.2/1.3/D2.3), not a sim.
- `coordinator.py` — the **D5 reliability companion**: a raw-API hand-rolled hub-and-spoke over a
  TINY toy topic (Tokyo facts) that stages D5.3 structured error propagation, D5.4 manifest /
  crash-recovery, and D5.6 provenance + conflict annotation, plus the anti-pattern **toggles**.
  Each "subagent" is a separate `client.messages.create` with its **own** `messages` list =
  isolated context — cheap and deterministic, so the D5 concepts run without spawning real agents.
- `manifest.json` — written each `coordinator.py` run (D5.4 scratchpad / crash-recovery state).

The real `Task`/`allowedTools`/`AgentDefinition` surface lives in `coordinator_sdk.py`; the raw-API
`coordinator.py` reproduces the *D5 reliability concepts* without needing the SDK to spawn agents.

## Run
```bash
# from this folder — uv finds ../pyproject.toml and uses the ccaf-prep env (native arm64).
uv run python coordinator_sdk.py   # REAL SDK delegation (D1.2/1.3/D2.3). Spawns the claude CLI on
                                   # your Claude Code auth -> real usage, ~$0.04 on Haiku.
uv run python coordinator.py       # D5 reliability companion + anti-pattern toggles (raw API).
```
Key + model load from `../../claude-with-anthropic-api/.env` automatically (`CLAUDE_MODEL` if set,
else `claude-haiku-4-5`; `coordinator_sdk.py` uses the SDK short name `"haiku"`).

## What maps to what (read while the output scrolls)

The D1.2/1.3/D2.3 *delegation mechanism* (Task spawns, scoped subagent tools, isolated context) is
shown for real by `coordinator_sdk.py` — watch its `[coordinator -> Task spawns subagent]` and
`[scoped data tool fired]` lines. The table below maps the **`coordinator.py`** output, which adds
the D5 reliability layer and the toggles on a raw-API hub-and-spoke:

| You see in the output | Task Statement |
|---|---|
| each `subagent()` is a fresh `messages` list; `[coordinator <- X]` routes through the hub | **D1.2** hub-and-spoke + isolated context |
| `ISOLATION PROOF` — a fresh subagent says it can't see the websearch finding | **D1.2** isolated context (no inheritance) |
| `[coordinator] selected N subagent(s)` — 3 for the broad query, 1 for the simple one | **D1.2** dynamic selection by query complexity |
| each subagent gets a distinct subtopic / source-type (web vs docs vs landmark) | **D1.2** partition scope, minimize duplication |
| `[synthesis WITH passed context]` — prior findings passed as STRUCTURED, attributed JSON | **D1.3** context passing in the prompt |
| `scoped tools: [['web_search'], ['load_document'], ...]` per subagent; synthesis gets only `verify_fact` | **D2.3** per-subagent tool scoping |
| `STRUCTURED ERROR (failure_type=access_failure)` with partial + alternative; `empty_result` distinct | **D5.3** error propagation (Q8) |
| `wrote manifest -> manifest.json` capturing completed/errors/findings | **D5.4** scratchpad / crash-recovery manifest |
| `[PROVENANCE] claim -> source` + `! CONFLICT ... ANNOTATED, not resolved` | **D5.6** provenance + conflict annotation |

## The anti-pattern experiments (the real learning)

1. **"Subagents inherit context" — FALSE (D1.3).** Set `PASS_CONTEXT = False`, rerun.
   The synthesis subagent no longer receives the prior findings in its prompt, so it goes
   *blind* (`[synthesis WITHOUT passed context]`) — it has no hidden memory of what the
   search subagents found. Context is isolated; the **prompt is the only channel**.

2. **Always routing the full pipeline (D1.2).** Set `DYNAMIC_SELECTION = False`, rerun.
   Now the simple "one famous temple" query runs all 3 subagents instead of 1 — wasted
   calls. The coordinator should **select** subagents by query complexity, not always
   fan out fully.

3. **Blame the wrong component (D1.2, sample Q7).** When coverage of a broad topic is
   incomplete, the usual root cause is the **coordinator decomposing too narrowly**, not a
   broken subagent. Here `select_subagents()` is the decomposition logic — narrow it (drop
   `documents` from the population branch) and you lose the conflicting figure entirely:
   that gap is a *coordinator* bug, not a websearch failure.

4. **Suppressing an error / killing the workflow (D5.3, sample Q8).** The `outage` query
   returns a **structured** error (`failure_type`, `attempted_query`, `partial_results`,
   `suggested_alternative`) that propagates UP — the coordinator keeps going and can retry
   or fall back. The anti-patterns are (a) returning empty-as-success (silent suppression)
   and (b) terminating the whole workflow on one failure. Note `access_failure` (retry?)
   vs `empty_result` (valid, no match) are **distinct** — a generic "search unavailable"
   would hide that.

5. **Re-exploring from scratch (D5.4).** `manifest.json` records `completed`, `errors`, and
   `findings`. A crash mid-run could **resume** from the manifest instead of re-invoking
   every subagent. Deleting the manifest and re-running = the re-explore anti-pattern.

6. **Arbitrarily picking one value on conflict (D5.6).** The web source says 37.0M, the
   document says 41.0M. The code **annotates** the conflict with both sources and dates
   rather than silently choosing one — and the differing dates flag that it may not even be
   a true contradiction (temporal, not contradictory).

## After this exercise
Do **15–20 bank questions on D1.2/1.3 + D5.3/5.4/5.6**. If you miss a pattern, flip the
matching toggle in `coordinator.py` and rerun before moving on. Pair with
`notebooks/D1_agentic_loops.ipynb` §1.2–1.3 — those cells now run the **same real SDK**
delegation as `coordinator_sdk.py` (Task / AgentDefinition / scoped tools), so the notebook and
this exercise reinforce the identical mechanism; `coordinator.py` then layers on the D5 reliability
concepts.
