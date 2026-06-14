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
| 3 | `D5_context_reliability.ipynb`| D5 · Context Management & Reliability (15%)     | ✅ built |
| 4 | `D3_*.ipynb`                  | D3 · Claude Code Configuration & Workflows (20%)| ⏳ to build |
| 5 | `D4_*.ipynb`                  | D4 · Prompt Engineering & Structured Output (20%)| ⏳ to build |

Run every code cell. Each notebook ends with its **sample exam questions** (answers hidden)
and an **"Exercises that use this domain"** block.

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
