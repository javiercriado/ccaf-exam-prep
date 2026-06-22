# Sample runs — annotated reference transcripts

Representative output of the two EX4 scripts, annotated with the task statements each step proves —
so you can review the behavior without re-running. One section per **Study runbook step** in the
[`README`](./README.md#study-runbook-do-this-in-order).

> ⚠️ **Output is non-deterministic, but the MECHANISMS here are deterministic.** Subagent *wording*
> varies between runs; the *structure* does not — the selection count, the conflict annotation, and
> whether context reaches the synthesis prompt are fixed by the toggles, not the dice. The toy
> `_FACTS` backend is deterministic; only the natural-language glosses (and the SDK briefing) vary.
> The `coordinator_sdk.py` cost (~$0.04) is a real charge on your Claude Code auth.
>
> Model: default `claude-haiku-4-5` (`coordinator_sdk.py` uses the SDK short name `"haiku"`).

**How runs are filed.** Each section = one runbook step. Runs go in the `Run N` table. To add a run:
paste me the output, say the step number, I append it under that section.

---

## Experiment SDK — real Task delegation · Runbook step 1 (`coordinator_sdk.py`)

> **Run 1× (real SDK, ~$0.04). Expected result:** the coordinator spawns the `weather` and
> `landmark` subagents via the `Task` tool; each fires only its **own scoped MCP tool**; a single
> two-sentence briefing combines their findings.

```
[coordinator -> Task spawns subagent]: 'weather'
[coordinator -> Task spawns subagent]: 'landmark'
   [scoped data tool fired]: mcp__research__get_landmark
   [scoped data tool fired]: mcp__research__get_weather

[FINAL BRIEFING]
**Tokyo Briefing:**

Tokyo is currently experiencing cloudy conditions with a temperature of 18°C. The city's most
iconic landmark is Tokyo Tower, a 333-meter structure completed in 1958 that dominates the skyline.

(real run on haiku: turns=3, cost=$0.0436)

Task spawned subagents? True -> ['weather', 'landmark']
Scoped subagent tools fired? True -> ['mcp__research__get_landmark', 'mcp__research__get_weather']
```

- 🎯 **A subagent spawn surfaces as a `task_started` SystemMessage** (not a `ToolUseBlock` named
  "Task") — that is the real delegation signal (D1.2/1.3).
- 🎯 **Each subagent fires only its scoped tool** (`weather` → `get_weather`, `landmark` →
  `get_landmark`); the SDK enforces the `AgentDefinition.tools` scope (D2.3).
- The CLI may emit the two `scoped data tool fired` lines in either order — both subagents run.

| Run | spawned | scoped tools fired | turns | cost | Verdict |
|---|---|---|---|---|---|
| 1 | `weather`, `landmark` | `get_weather`, `get_landmark` | 3 | $0.0436 | expected |

---

## Experiment 0 — Clean pass · Runbook step 2 (`coordinator.py`, `DYNAMIC_SELECTION=True`, `PASS_CONTEXT=True`)

> **Run 1× (mechanism stable). Expected result:** 3 subagents for the broad query and 1 for the
> simple one; the population **conflict annotated** (not resolved); a fresh subagent proving context
> isolation; structured errors distinguishing `access_failure` from `empty_result`.

```
==============================================================================
QUERY: What is Tokyo's population and a famous landmark?
  [DYNAMIC_SELECTION=True  PASS_CONTEXT=True]
==============================================================================
[coordinator] selected 3 subagent(s): ['websearch', 'documents', 'landmark']   (scoped tools: [['web_search'], ['load_document'], ['landmark_lookup']])
[coordinator <- websearch]  Tokyo's metropolitan area has approximately 37 million residents.  [src=web:worldstats.example | 2023-01]
[coordinator <- documents]  The Tokyo metropolitan area has approximately 41.0 million residents.  [src=doc:UN-WUP-2018.pdf p.12 | 2018-05]
[coordinator <- landmark]  Sensō-ji, founded in 645 AD, is Tokyo's oldest temple.  [src=web:tokyo-guide.example | 2024-02]
[coordinator] wrote manifest -> manifest.json (completed=['websearch', 'documents', 'landmark'], errors=[])

[synthesis WITH passed context]:
  -> ... approximately 37 million residents [web:worldstats.example, 2023-01] versus 41 million
     residents [doc:UN-WUP-2018.pdf p.12, 2018-05] ... Sensō-ji, founded in 645 AD ...

[PROVENANCE] claim -> source (preserved through synthesis):
    - Tokyo's metropolitan area has approximately 37 million residents.  ==>  web:worldstats.example  (2023-01)
    - The Tokyo metropolitan area has approximately 41.0 million residents.  ==>  doc:UN-WUP-2018.pdf p.12  (2018-05)
    - Sensō-ji, founded in 645 AD, is Tokyo's oldest temple.  ==>  web:tokyo-guide.example  (2024-02)
    ! CONFLICT on population: 37.0M [web:worldstats.example 2023-01] vs 41.0M [doc:UN-WUP-2018.pdf p.12 2018-05]  -> ANNOTATED, not resolved (coordinator decides; dates differ so it may not be a true contradiction).

==============================================================================
QUERY: Tell me one famous Tokyo temple.
  [DYNAMIC_SELECTION=True  PASS_CONTEXT=True]
==============================================================================
[coordinator] selected 1 subagent(s): ['landmark']   (scoped tools: [['landmark_lookup']])
...

==============================================================================
ISOLATION PROOF (D1.2): subagents have isolated context
==============================================================================
  fresh subagent (no prior findings in its prompt) -> I don't have access to any previous conversations ... this is the start of our conversation ...

==============================================================================
STRUCTURED ERROR propagation (D5.3 / Q8)
==============================================================================
  web_search('Tokyo population during the outage') -> failure_type=access_failure  partial=True  alt='retry once, or fall back to document analysis (load_document)'
  web_search('Tokyo unicorn population') -> failure_type=empty_result  partial=False  alt='broaden the query or accept that no source covers this'
```

- 🎯 **Broad query → 3 subagents, simple query → 1** (D1.2 dynamic selection by complexity).
- 🎯 **Conflict ANNOTATED, not resolved** with both sources + dates (D5.6); the differing dates flag
  it may be temporal, not a true contradiction.
- 🎯 **Fresh subagent cannot see prior findings** (D1.2 isolated context).
- 🎯 **`access_failure` ≠ `empty_result`** — structured errors carry partial results + an alternative
  and propagate up without killing the run (D5.3).

| Run | broad-query subagents | simple-query subagents | conflict annotated | Verdict |
|---|---|---|---|---|
| 1 | 3 | 1 | yes (37M vs 41M) | expected |

---

## Experiment A — context passing · Runbook step 3 (`PASS_CONTEXT=False`)

> **Run 1× (deterministic mechanism). Expected result:** prior findings no longer reach the synthesis
> prompt, so it runs `[synthesis WITHOUT passed context]`. The model-dependent OUTCOME: with nothing
> to work from, the blind subagent asks for the information it was never handed.

**Observed (`claude-haiku-4-5`):** the synthesis went blind on both queries and requested the missing
context — a clear, if model-dependent, demonstration that context is not inherited.

```
[synthesis WITHOUT passed context (blind, D1.3 anti-pattern)]:
  -> # Tokyo Briefing

I'm ready to write a Tokyo briefing, but I need additional information to provide you with
accurate, source-cited content: ...
```

> **Mechanism vs. outcome.** The *mechanism* is deterministic — `PASS_CONTEXT=False` means the prior
> findings are simply absent from the prompt. The *outcome* (the subagent asking for info, or
> hallucinating, or producing a vague briefing) is model-dependent; here it asked. Either way the
> point stands: **the prompt is the only channel** — subagents share no hidden memory.

| Run | synthesis block | outcome | Verdict |
|---|---|---|---|
| 1 | WITHOUT passed context | asked for the missing info | expected (blind) |

---

## Experiment B — dynamic selection · Runbook step 4 (`DYNAMIC_SELECTION=False`)

> **Run 1× (deterministic). Expected result:** the simple "one famous Tokyo temple" query now runs
> the **full 3-subagent pipeline** instead of selecting just `landmark` — wasted calls.

**Observed (`claude-haiku-4-5`):** both queries selected all 3 subagents.

```
QUERY: What is Tokyo's population and a famous landmark?
[coordinator] selected 3 subagent(s): ['websearch', 'documents', 'landmark']   ...
QUERY: Tell me one famous Tokyo temple.
[coordinator] selected 3 subagent(s): ['websearch', 'documents', 'landmark']   ...   <- over-run (would be 1 with selection on)
```

> **The anti-pattern made visible.** With selection on, the temple query needs only `landmark`; with
> it off, the coordinator fans out fully regardless. Decomposition/selection by query complexity is
> the fix — not "always run everything to be safe" (D1.2).

| Run | broad-query subagents | simple-query subagents | Verdict |
|---|---|---|---|
| 1 | 3 | 3 (over-run) | expected (no selection) |
