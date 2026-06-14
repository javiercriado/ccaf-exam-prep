# CCAF Study Scope — Analysis & Decisions

> The reasoning that defines *what* to study, *how deep*, and *what to skip*.
> Read this first; it clears up the "I get lost in the abstractness" problem.

---

## The core problem & the fix

The task statements are written in the passive voice of a spec, but the exam tests
**judgment in concrete scenarios**. Anchoring each abstract bullet to a line of running
code you wrote collapses that gap. This is not an invented method — the guide's own
"Preparation Recommendations" (p.17) say to *build an agent, configure Claude Code,
design MCP tools, build an extraction pipeline*. We're operationalizing Anthropic's
own advice.

## The refinement: build *decisions*, not *products*

Build the smallest running thing that makes a concept concrete — then deliberately
build the **wrong** version too. The exam is ~80% distractor discrimination: every
question has 3 plausible-but-wrong answers. If you build the refund-blocking **hook**
(correct) *and* the refund-blocking **prompt instruction** (the distractor) and watch
the prompt version fail ~1 in 20 runs, you will never miss a "hook vs. prompt"
question again. **Building the anti-pattern is higher-leverage than polishing the
happy path.**

## Build vs. memorize — don't build everything

| Build it (concept clicks by running) | Just memorize (it's a fact, not a skill) |
|---|---|
| Agentic loop / `stop_reason` (D1.1) | Batches API: 50% cheaper, ≤24h, no SLA, no multi-turn tools (D4.5) |
| Hooks for enforcement vs. prompts (D1.5) | Scaled scoring 720/1000, 60q / 120min |
| Tool descriptions & overlap (D2.1) | Nonexistent features: `CLAUDE_HEADLESS`, `--batch` (distractor bait) |
| Structured errors `isError`/`errorCategory` (D2.2) | "lost in the middle" effect (D5.1) |
| JSON-schema extraction + validation-retry (D4.3/4.4) | CLAUDE.md hierarchy paths (D3.1) — build *once*, then recall |

## You do NOT build the 6 scenarios separately

Scenarios are *framings*, not buildable artifacts. They map ~1:1 onto the 4 official
exercises + the CI/CD one. Build the 5 exercises; each "lights up" a scenario, and that's
when you re-read that scenario's sample questions.

| Build this exercise | Lights up scenario(s) | Heaviest domains |
|---|---|---|
| 1 — Multi-tool agent + escalation | **S1** Customer Support, partly **S4** | D1, D2, D5 |
| 2 — Claude Code team config | **S2** Code Gen, **S4** Dev Productivity | D3, D2 |
| 3 — Extraction pipeline | **S6** Structured Extraction | D4, D5 |
| 4 — Multi-agent research | **S3** Multi-Agent Research | D1, D2, D5 |
| 5 — CI/CD (the addition) | **S5** Claude Code for CI | D3, D4 |

All 6 scenarios covered.

## Boilerplate you already have (big head start)

- **`claude-with-anthropic-api/cli_project/`** — the crown jewel. `core/chat.py`'s loop
  *is* the D1.1 agentic loop (print `stop_reason` each turn → watch `tool_use → end_turn`).
  `core/tools.py:execute_tool_requests` already handles the MCP `is_error` flag (D2.2).
  `mcp_server.py` already exposes a **resource catalog** (`docs://documents`) — that's D2.4.
- **`claude-with-anthropic-api/queries/`** — covers the hard-to-find stuff: real
  `@anthropic-ai/claude-agent-sdk`, and `hooks/query_hook.js` is *exactly* the enforcement
  pattern (reviews a tool input, **blocks with `exit 2`**) — structurally identical to
  "block refund > $500." Its `CLAUDE.md` covers D3.1.
- **`claude-with-anthropic-api/app_starter/`** — FastMCP + pytest base for the extraction
  pipeline and the test-driven-iteration habit (D3.5).

## Extra context (things easy to miss)

1. **Your RAG/embeddings courses are OUT of scope.** The appendix excludes embeddings,
   vector DBs, chunking, hybrid search, streaming, vision, caching internals. Your notebooks
   `002_embeddings`, `003_vectordb`, `004_bm25`, `005_hybrid`, `001_chunking` → **do not
   re-study any of it.** Pure time saved.
2. **The exam's vocabulary is the Agent SDK, not the raw Python loop.** Your Python
   `cli_project` teaches the *concept* of the loop; the exam phrases it as the `Task` tool,
   `allowedTools` must include `"Task"`, `fork_session`, `AgentDefinition`. **Exercise 4**
   (TS multi-agent) is what bridges concept → exam wording. Don't skip it.
3. **The 5 distractor patterns are the actual skill tested.** Every one of the 12 sample
   questions is an instance: Q1=hook-not-prompt, Q2=descriptions-not-routing,
   Q3=criteria-not-sentiment, Q5=plan-mode, Q10=nonexistent-flag, Q11=batch-not-blocking,
   Q12=split-passes-not-bigger-model. The hands-on exists to make those reflexes physical.
4. The guide is **v0.1 (Feb 2025)** — the only authoritative source. Everything else
   (618-question banks, third-party sites) is secondary recognition practice.

## The 5 distractor patterns (the meta-skill)

1. **Over-engineered solution** — ML classifier / new infra when a prompt or description fix suffices.
2. **Prompt when determinism is required** — use a hook / programmatic gate, not an instruction.
3. **Blaming the wrong component** — especially in multi-agent (the coordinator's decomposition, not the subagents).
4. **Nonexistent features** — `CLAUDE_HEADLESS`, `--batch`, `.claude/config.json` commands array.
5. **Correlation vs. causation** — sentiment / self-reported confidence as a proxy for complexity.

## Decisions for this prep

- **Working mode:** pair-build. I scaffold the correct version **and** the deliberate
  anti-pattern; you read, run, and study.
- **Depth:** minimal + anti-pattern. Smallest runnable artifact per concept, optimized for
  exam judgment, not production polish.
- **Language:** English (materials + notes), to match the exam.
