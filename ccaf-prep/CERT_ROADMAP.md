# Certification Roadmap — which Claude exams to take, and how to prep each

> Companion to [`STUDY_PLAN.md`](./STUDY_PLAN.md) (the CCAR-F schedule) and
> [`MAPPING.md`](./MAPPING.md) (the task-statement index). This file is the **cross-exam
> strategy**: as of **July 2026** the Anthropic Partner program split into **four separate
> credentials**, all delivered via **Pearson VUE** (register through the Anthropic Partner
> Academy). The old Skilljar practice exam is retired — we simulate our own (see
> `notebooks/practice_exam_A.ipynb`).

## The four credentials at a glance

All four: pass = **720 / 1000** scaled · **120 min** · **12-month** validity · **no prerequisites**
· retake waits **14 / 30 / 90 days** (max 4 attempts / rolling 12 mo) · free on-time renewal ·
mix of **multiple-choice and multiple-response** items (each item says how many to select).

| Credential | Code | Price | Items | Domains | Who it's for |
|---|---|---|---|---|---|
| Associate – Foundations | CCAO-F | $99 | 60 | 7 | Business power-users: Projects, Artifacts, prompting, governance. **No code/API.** |
| Developer – Foundations | CCDV-F | $125 | 53 | 8 | Engineers shipping apps: API mechanics, SW-eng, agent frameworks, security. |
| **Architect – Foundations** | **CCAR-F** | **$125** | **60** | **5** | **Solution architects — the one this kit targets.** |
| Architect – Professional | CCAR-P | $175 | 63 | 7 | Senior architects; *analyze/evaluate/justify*; adds RAG, evals, compliance, lifecycle. |

**No credential requires another as a prerequisite** — the "Foundations → Professional" order is a
recommendation, not a gate.

## Recommended ladder (and why)

1. **CCAR-F — Architect – Foundations** *(in progress).* Finish + pass first. This kit is built for it.
2. **CCAR-P — Architect – Professional** ⭐ *primary next step.* Same role track, one tier up, the
   highest résumé value of the set, and it **reuses D1–D5** of the Foundations work. No prerequisite,
   so nothing is wasted. This is the one that signals seniority.
3. **CCDV-F — Developer – Foundations** *(optional, for breadth).* ~60–70% overlaps what's already
   built; demonstrates hands-on build credibility. Cheapest incremental cert after the Architect track.
4. **CCAO-F — Associate – Foundations** *(skip unless completionist).* Lowest technical value for an
   architect; it targets non-technical business users. Only worth it to advise non-technical
   stakeholders or to hold the full set.

**Is CCAR-F alone enough?** As a standalone credential validating architect skills — yes. But if the
goal is to keep leveling up, **CCAR-P is the differentiator.**

## How to prepare for each — it's the *same system*, extended

The method does **not** change: **one notebook per domain** (verbatim guide quote → plain-English
unpack → runnable cell that makes the concept observable → anti-pattern as code → pointer to your own
code → self-check), **plus cross-domain exercises**, **plus a `MAPPING.md`** index and a
scenario-format **practice exam**. New exam = new `MAPPING`, new per-domain notebooks, new exercises
for whatever is genuinely new. Concretely:

### CCAR-P — Architect – Professional (the real target after this)
Reuse D1–D5 notebooks/exercises almost as-is (the Professional D1–D5 map onto them). **Add** notebooks/
exercises for what's new and pitched at analyze/justify level:
- **RAG pipeline design** — chunking, indexing, retrieval strategies matched to data shape/query.
- **Evaluation, testing & optimization** — metrics (accuracy/latency/cost/safety), eval datasets, A/B
  testing, diagnosing hallucination/model-mismatch, observability at scale.
- **Governance, safety & risk** — guardrails, failure modes, human-in-the-loop, compliance
  (GDPR/HIPAA/FedRAMP), bias/fairness/transparency.
- **Stakeholder communication & lifecycle** — discovery, trade-off communication, SLAs, handoff/docs.
- **Integration depth** — protocol selection (MCP vs API/CLI vs agent-to-agent), auth/authz gaps,
  accuracy-latency trade-offs, capability-bloat evaluation.

### CCDV-F — Developer – Foundations (breadth)
Keep the agents/tools/MCP/Claude-Code/prompt/context material. **Add**:
- **Claude API mechanics** — messages, streaming, vision, thinking, caching, batch vs realtime.
- **Software-engineering foundations** — REST/JSON, async, version control, SDLC, refactoring.
- **Model selection & optimization** — Opus/Sonnet/Haiku trade-offs, token budgeting, cost modeling.
- **Security & safety** — prompt-injection mitigation, jailbreak/untrusted-input handling, PII,
  secrets/key management, guardrail layering.
- **Agent frameworks** — awareness of Strands, LangGraph, PydanticAI (patterns, not deep APIs).
- Note the weight skew: **Domain 2 "Applications & Integration" = 33%**; Claude Code only ~3%.

### CCAO-F — Associate – Foundations (only if pursued)
Different framing — build a couple of notebooks around **product features** (Projects, Artifacts,
Memory, connectors like Drive/Gmail), **output evaluation/validation**, **model selection for
cost/speed**, and **responsible-use judgment** (data sensitivity, appropriate use cases, escalation).
Little code; heavy on judgment and governance.

## Prep principle that carries across all four
Every one of these exams is **scenario-based and tests judgment, not recall** — "your system fails
this way; which fix is correct?" The single most transferable rule: **"code must, prompt should"** — a
guaranteed requirement goes in deterministic code (hook / gate / schema), not a prompt. Drill the
*decision*, not the definition. That's exactly what the per-notebook anti-patterns and the
`practice_exam_A.ipynb` simulacrum train.
