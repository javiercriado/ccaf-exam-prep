# Gap Analysis — CCDV-F (Developer – Foundations) vs. this CCAR-F kit

> **Status: DRAFT, not yet validated.** Produced 2026-08-02, the night the CCAR-F material was
> freshest, by reading the official CCDV-F blueprint against this kit's notebooks. The coverage
> fractions are **judgment calls**, not measurements — a follow-up session must verify them
> section by section (see [Validation](#validation--what-the-next-session-must-check) at the end).
>
> Method and rationale: [`CERT_ROADMAP.md`](./CERT_ROADMAP.md) § "How to start the *next* exam".
> Guide text lives in `reference/exam_guide_CCDV-F.txt` (git-ignored, not redistributed).
> Task statements are **summarized**, never quoted verbatim — same rule as [`MAPPING.md`](./MAPPING.md).

## Headline: the "~60–70% already covered" figure was too optimistic

`CERT_ROADMAP.md` estimated CCDV-F at ~60–70% overlap **before anyone had read its blueprint**.
Measured against the actual weighted skill list:

| | |
|---|---|
| Covered by the CCAR-F kit | **~44%** |
| Plus generic SW-engineering / technical fundamentals (13.5% of the exam) that a working developer already knows, kit or no kit | **~56%** |

So the honest number is **roughly half, not two-thirds** — and the missing half is concentrated
where CCDV-F puts most of its weight.

**Why the overlap is thinner than it feels.** The two exams weight almost inversely:

| Area | CCAR-F | CCDV-F |
|---|---|---|
| Claude Code | 20% | **3.1%** |
| Applications & Integration (API mechanics, SW-eng, app design) | not a domain | **33.1%** |
| Model Selection & Optimization (LLM fundamentals, cost, caching) | not a domain | **16.8%** |

Half of CCDV-F lives in two domains this kit never had to build. Meanwhile the domain this kit
invested most in — Claude Code configuration — is worth 3.1% there.

## Gap by domain — where the work actually is

| Uncovered | Domain | Verdict |
|---:|---|---|
| **25.1 pts** | D2 Applications & Integration (33.1%) | The whole project. Build here first. |
| **14.4 pts** | D5 Model Selection & Optimization (16.8%) | Second priority; nothing in the kit teaches it. |
| 5.9 pts | D7 Security & Safety (8.1%) | Small but almost entirely new. |
| 4.4 pts | D1 Agents & Workflows (14.7%) | Mostly covered; thin edges only. |
| 3.1 pts | D8 Tools and MCPs (10.6%) | Mostly covered; MCP *authoring* is new. |
| 1.6 pts | D6 Prompt & Context Engineering (11.0%) | Essentially free. |
| 1.4 pts | D4 Eval, Testing & Debugging (2.6%) | Nearly free. |
| 0.2 pts | D3 Claude Code (3.1%) | Free. Already built and hand-validated. |

## Skill-by-skill

Legend: **✅ covered** — an existing section teaches it, just cross-reference it ·
**🟡 partial** — mechanism covered, but CCDV-F adds a facet · **🔴 new** — nothing in the kit.

### D2 · Applications and Integration — 33.1%

| Skill | Wt | | Where it stands |
|---|---:|:--:|---|
| Claude Application Design | 8.6% | 🟡 | Schema design (D4.3) and session hygiene (D1.7, D5.1) are solid. **New:** how Claude reads instructions differently across Claude Code / Desktop / claude.ai / API / SDKs; content boundaries; plugin management. |
| Software Engineering Foundations | 7.4% | 🔴 | REST/JSON/async/version control/SDLC/code review/refactoring. New *to the kit* — likely not new to you. Confirm before spending a day here. |
| Claude API Mechanics | 6.8% | 🟡 | Batch is well covered (D4.5); tool use throughout. **New:** streaming, vision, extended thinking, **prompt caching**, and invoking Claude through third-party vendors (Bedrock / Vertex — zero mentions in the kit). |
| Configuration Management | 4.1% | 🟡 | CLAUDE.md hierarchy and settings.json are in D3. **New:** model version pinning, prompt versioning, plugin dependencies. |
| Understanding Requirements | 3.4% | 🔴 | Deriving functional/infra requirements from business requirements. |
| Systems Life Cycle | 2.8% | 🔴 | SDLC frameworks for developing/operating/maintaining systems. |

### D5 · Model Selection and Optimization — 16.8%

| Skill | Wt | | Where it stands |
|---|---:|:--:|---|
| Technical Fundamentals | 6.1% | 🔴 | SDKs wrapping REST, websockets. New to the kit; probably known to you. |
| LLM Fundamentals | 5.2% | 🟡 | Few-shot is covered (D4.2). **New:** tokens/context windows/sampling/non-determinism as *mechanics*, plus fast mode, extended thinking, adaptive thinking, effort levels. |
| Cost and Token Management | 2.8% | 🔴 | Token tracking, cost modeling, **prompt caching and cache check-pointing**. The kit's only cost content is the "keep calls cheap" convention — a habit, not a taught mechanism. |
| Model Selection and Tradeoffs | 2.7% | 🔴 | Opus/Sonnet/Haiku selection, quality-latency-cost trade-offs, breaking changes across releases. The kit *uses* Haiku everywhere but never teaches *why you'd pick it*. |

### D7 · Security and Safety — 8.1%

| Skill | Wt | | Where it stands |
|---|---:|:--:|---|
| AI Application Security | 3.2% | 🔴 | Prompt injection, jailbreak defense, untrusted input, data-leakage prevention, PII, authn/authz. |
| Guardrails and Safe Deployment | 2.3% | 🟡 | [`LEAST_PRIVILEGE.md`](./LEAST_PRIVILEGE.md) covers part. **New:** content policy, guardrail layering, secure-by-design. |
| Identity, Secrets, Key Management | 1.6% | 🔴 | Secrets/credentials/keys across environments, access approval and monitoring. |
| Claude Hooks | 1.0% | ✅ | D1.5 (`PreToolUse` deny, `PostToolUse` normalize). Reuse as-is. |

### D1 · Agents and Workflows — 14.7% · mostly covered

| Skill | Wt | | Where it stands |
|---|---:|:--:|---|
| Agent Construction with Claude | 5.3% | 🟡 | Agent SDK, custom loops, hooks all covered (D1.1, D1.5). **New:** managed agent deployment — self-hosted vs. Anthropic-hosted. |
| Agent Patterns and Frameworks | 4.9% | 🟡 | Patterns covered. **New:** awareness of Strands, LangGraph, PydanticAI (patterns, not APIs). |
| Agent Architecture | 4.5% | 🟡 | Coordinator/subagent and decomposition covered (D1.2, D1.6). **New:** the explicit *workflow vs. agent* decision criteria — when **not** to build an agent. |

### D8 · Tools and MCPs — 10.6% · mostly covered

| Skill | Wt | | Where it stands |
|---|---:|:--:|---|
| Tool Implementation | 4.4% | ✅ | CCAR-F D2 covers descriptions, structured errors, tool sets. Thin edge: client-side vs. server-side tools, approval patterns. |
| Agentic Customization | 4.1% | ✅ | Built-in vs. custom tools vs. Skills vs. MCPs — D2/D3 plus [`DISTRACTOR_HEURISTIC.md`](./DISTRACTOR_HEURISTIC.md). |
| MCP Server Development | 2.1% | 🟡 | **Authoring and deploying MCP servers was explicitly OUT of scope for CCAR-F**, so the kit configures servers but never builds one. Resources/prompts primitives and stdio transport are new. |

### D6 · Prompt & Context Engineering — 11.0% · nearly free

Context Engineering (3.8%) ✅ CCAR-F D5 · Output Handling (2.6%) ✅ D4.3/D4.4, including the
"confident output is poorly calibrated" lesson · Prompt Engineering (4.6%) 🟡 D4.1/D4.2 cover it;
**new:** system-vs-user placement and input sanitization.

### D3 (3.1%) and D4 (2.6%) · free and nearly free

Claude Code Operation ✅ — CCAR-F D3, hand-validated. Debugging & Error Handling 🟡 — structured
errors and graceful degradation are covered in D5; **new:** trace analysis and isolating whether a
failure came from the integration layer or the model output.

## What to build — and what not to

**Build, in this order** (roughly 5 new notebooks, not 8):

1. **`CCDV_D2_api_and_app_design`** — the 25-point gap. Streaming, vision, extended thinking,
   prompt caching, Bedrock/Vertex, cross-interface instruction handling, plugins, config
   pinning/versioning. Highest weight, highest novelty.
2. **`CCDV_D5_model_and_cost`** — model selection trade-offs, thinking/effort modes, token
   budgeting, cost modeling, prompt caching mechanics. Runnable and cheap to demonstrate.
3. **`CCDV_D7_security`** — prompt injection, untrusted input, PII, secrets, guardrail layering.
4. **`CCDV_D8_mcp_authoring`** — build one small MCP server (stdio; tools + resources + prompts).
5. **Deltas only, folded into the existing notebooks** — workflow-vs-agent criteria (D1),
   framework awareness (D1), input sanitization + system/user placement (D6), trace analysis (D4).

**Do not rebuild:** Claude Code configuration, agentic loops, hooks, tool design, structured
output/validation, context management. That is the ~44% already paid for — cross-reference it from
a new `MAPPING_CCDV-F.md` instead of re-teaching it.

**Reuse unchanged:** the notebook authoring standard, `notebooks/examkit.py` (exam-agnostic — a
`practice_exam_CCDV.ipynb` needs only new questions), `DISTRACTOR_HEURISTIC.md`.

## Validation — what the next session must check

This draft was written from the blueprint plus keyword sweeps of the notebooks. **Verify before
building anything.** Cheap keyword greps found zero mentions of Bedrock/Vertex, websockets,
prompt injection, and the agent frameworks — but a keyword *hit* is not coverage either:
`Opus|Sonnet|Haiku` matches in all five notebooks purely because of the `claude-haiku-4-5` default,
and `cost` matches the "keep calls cheap" convention. Neither teaches model selection.

1. **Open the notebooks, don't grep them.** For every 🟡 row, read the cited section and confirm it
   really teaches the CCDV-F facet, then reclassify to ✅ or 🔴. Correct the coverage figure.
2. **Confirm the developer-background assumption.** 13.5% of the exam is generic SW-eng and
   technical fundamentals. If Javier is comfortable there, skip it; if not, the gap is ~56%, not ~44%.
3. **Decide the repo layout before writing notebook one.** A second credential wants per-cert
   folders over a shared core. Deciding after the fact means paying for the restructure twice.
4. **Sanity-check the weights** against `reference/exam_guide_CCDV-F.txt` — this table was
   transcribed by hand.
5. **Then, and only then**, generate notebooks with the `ccaf-notebook` skill (its prompt is
   CCAR-F-specific; it will need a parameter or a sibling skill for another exam).

## CCAR-P — deferred, guide already extracted

`reference/exam_guide_CCAR-P.txt` is in place for when CCDV-F is done. Its seven domains
(Integration 19%, Solution Design 17%, Evaluation/Testing/Optimization 16%, Governance & Risk 14%,
Stakeholder & Lifecycle 14%, Models/Prompting/Context 13%, Developer Productivity 7%) reuse D1–D5
conceptually but pitch everything at *analyze / evaluate / justify*. It is a larger project than
CCDV-F, not a smaller one. Same gap-analysis treatment when its turn comes.
