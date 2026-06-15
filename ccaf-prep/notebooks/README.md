# CCAF notebooks — study order

The short version. For the full schedule and rationale, see [`../STUDY_PLAN.md`](../STUDY_PLAN.md);
for the abstract→concrete index, [`../MAPPING.md`](../MAPPING.md).

## 1. Study the domain notebooks in this order

Order is dependency-driven (so each exercise unlocks as soon as its domains are covered),
not pure exam weight.

| # | Notebook | Domain (weight) | Status |
|---|----------|-----------------|--------|
| 1 | `D1_agentic_loops.ipynb`      | D1 · Agentic Architecture & Orchestration (27%) | ✅ built |
| 2 | `D2_tool_design_mcp.ipynb`    | D2 · Tool Design & MCP Integration (18%)        | ✅ built |
| 3 | `D5_context_reliability.ipynb`| D5 · Context Management & Reliability (15%)     | 🔧 in progress |
| 4 | `D3_*.ipynb`                  | D3 · Claude Code Configuration & Workflows (20%)| ⏳ to build |
| 5 | `D4_*.ipynb`                  | D4 · Prompt Engineering & Structured Output (20%)| ⏳ to build |

Run every code cell. Each notebook ends with its **sample exam questions** (answers hidden)
and an **"Exercises that use this domain"** block.

### Which layer — raw Messages API vs Agent SDK (and why)

The exam tests **architecture concepts, not one SDK's syntax**. So these notebooks use
*whichever layer the concept actually lives at* — that's the rule, not a global preference:

- **Raw Messages API** (`client.messages.create`) when the concept **is a Messages-API
  primitive the SDK hides** and you need to *see* it:
  agentic loop / `stop_reason` (D1.1), `tool_use`/`tool_result`, tool descriptions &
  `tool_choice` (D2.1/2.3), structured errors / `isError` (D2.2), structured output via
  tool_use + JSON schema (D4.3/4.4), Batch (D4.5), single-turn decisions (D5.1/5.2/5.5/5.6).
  *(Raw-API tool use has two halves: Claude returns a `tool_use` block — that's "calling" the
  tool — and **your** code executes it and returns a `tool_result`. The API never runs your
  function; that loop is the protocol.)*
- **Agent SDK** (`query()` + `Task` / `AgentDefinition`) when the concept **is a runtime
  feature** — doing it raw would be faking it:
  coordinator + subagents + `Task` (D1.2/1.3), `PreToolUse`/`PostToolUse` hooks and
  deterministic gates (D1.4/1.5), sessions / `fork_session` (D1.7), multi-agent error
  propagation & delegation (D5.3/5.4).
- **Claude Code (config/CLI)** when it's **configuration, not code**:
  `CLAUDE.md`, `.claude/commands/`, `.claude/rules/`, plan mode, headless `-p` (D2.4, all of D3).

Rule of thumb: the **Agent SDK / Claude Code is the predominant *vocabulary*** of the
architecture (most of D1, D3, and the multi-agent parts of D5); the **raw API exposes the
primitive underneath** when the concept *is* that primitive. Each notebook's setup cell
states which layer it uses and why.

## 2. Do the hands-on exercises as they unlock

Exercises are **cross-domain** — none maps to a single domain — so do them in waves once
their domains are studied (not one-per-notebook):

| After studying… | Do exercises | Domains each needs |
|-----------------|--------------|--------------------|
| D1 + D2 + D5    | **Ex1** then **Ex4** | D1+D2+D5 |
| + D3            | **Ex2**              | D3+D2    |
| + D4            | **Ex3** ∥ **Ex5**    | D4+D5 / D3+D4 |

(Ex1 before Ex4: Ex4 cements the Agent SDK vocabulary — `Task`, `allowedTools`, `fork_session`.)
Exercise folders are `../exercises/01-support-agent/` … `../exercises/05-cicd-review/`.

## 3. After finishing each domain notebook

Open [`mock_exam_and_review.ipynb`](./mock_exam_and_review.ipynb) and tick off, for the domain
you just finished:
- its **In-Scope topics** and **Technologies & Concepts** (Part A),
- the **prep recommendations** it satisfies (Part C).

## 4. At the very end

Once all 5 notebooks and all 5 exercises are done, work through
`mock_exam_and_review.ipynb` end-to-end: the **scenario-grouped mock** (Part D), confirm
Part A coverage is fully ticked, then sit the official **Practice Exam** (Skilljar) under
timed conditions.
