# Code ↔ Task-Statement ↔ Sample-Question Map

> The antidote to abstractness. When a task statement reads as vague, jump to its
> **anchor** column and look at / run the code. When you see a sample question, find it
> here and recall the *pattern*, not the wording.
>
> **Each row summarizes the ENTIRE task statement** (every "Knowledge of" + "Skills in"
> bullet), compressed to one line as an index — not as your first encounter with it.
> For the full, runnable walkthrough, **start with the matching notebook in `notebooks/`.**
>
> Anchor key:
> - `notebooks/` = per-domain Jupyter notebooks (the place to *learn* each task statement).
> - `exercises/01-support-agent/` … `exercises/05-cicd-review/` = the hands-on exercise folders ("EX1"…"EX5").
> - `cli_project`, `queries`, `app_starter` = your existing `claude-with-anthropic-api` boilerplate.

---

## Domain 1 — Agentic Architecture & Orchestration (27%)

| Task | What it really means | Concrete anchor | Sample Q | Distractor pattern |
|---|---|---|---|---|
| 1.1 Agentic loops | Loop while `stop_reason=="tool_use"`, stop on `"end_turn"`; append tool results | **`notebooks/D1_agentic_loops.ipynb`** (run it); `exercises/01-support-agent/agent.py`; course loop: `cli_project/core/chat.py:24-47` | — | Don't parse text / cap iterations to stop |
| 1.2 Coordinator–subagent | Hub-and-spoke; subagents have **isolated context**; coordinator owns decomposition | **`notebooks/D1_agentic_loops.ipynb` §1.2** (real SDK); **`exercises/04-multi-agent-research/coordinator_sdk.py`** (real `Task` delegation); `EX4` `coordinator.py` (raw-API D5 companion) | **Q7** (root cause = coordinator decomposition too narrow) | #3 blame wrong component |
| 1.3 Subagent invocation | `Task` tool; `allowedTools` must include `"Task"`; pass context **in the prompt**; parallel Task calls in one response | **`notebooks/D1_agentic_loops.ipynb` §1.3** (real SDK); **`exercises/04-multi-agent-research/coordinator_sdk.py`** (`AgentDefinition` + `allowed_tools=["Task"]`) | — | "subagents inherit context" = false |
| 1.4 Enforcement & handoff | Programmatic gates vs. prompt guidance; structured escalation summaries; multi-concern decomposition | **`notebooks/D1_agentic_loops.ipynb` §1.4** (real SDK: stateful `PreToolUse` prereq gate + threshold→structured handoff + parallel multi-concern decomposition); `exercises/01-support-agent/agent.py:34-48,76-85` gate (`ENFORCE` toggle); handoff `tools.py:78-81` | **Q1** (block until get_customer verified) | #2 prompt when determinism needed |
| 1.5 Hooks | `PostToolUse` / tool-call interception for deterministic compliance | **`notebooks/D1_agentic_loops.ipynb` §1.5** (real SDK: `PreToolUse` block + `PostToolUse` epoch→ISO normalize, `matcher=None`); `exercises/01-support-agent/agent.py:34-48` gate ≈ hook; `queries/hooks/query_hook.js` (blocks w/ `exit 2`) | — | #2 prompt for guaranteed compliance |
| 1.6 Task decomposition | Fixed prompt-chaining vs. dynamic adaptive; per-file + integration pass | **`notebooks/D1_agentic_loops.ipynb` §1.6** (fixed-chain code sketch + real SDK adaptive map→plan-from-findings run); `exercises/01-support-agent/agent.py:29-30,105-106`; `EX5` per-file (planned) | **Q12** | #1 bigger model instead of split |
| 1.7 Sessions / forking | `--resume <name>`, `fork_session`; new session + summary beats stale resume | **`notebooks/D1_agentic_loops.ipynb` §1.7** (real SDK: resume + `fork_session`, verified independent branches); `queries/sdk.ts:1-12`; `EX2` notes (planned) | — | resume with stale results |

## Domain 2 — Tool Design & MCP Integration (18%)

| Task | What it really means | Concrete anchor | Sample Q | Distractor pattern |
|---|---|---|---|---|
| 2.1 Tool descriptions | Descriptions are the **primary** selection mechanism; overlap → misrouting | **`notebooks/D2_tool_design_mcp.ipynb` §2.1** (live: vague vs differentiated routing); `EX1/tools.py:88-122` (`GOOD_DESCRIPTIONS` toggle: 2 similar tools) | **Q2** (expand descriptions first) | #1 routing layer / consolidate prematurely |
| 2.2 Structured errors | `isError`; `errorCategory` (transient/validation/permission), `isRetryable` | **`notebooks/D2_tool_design_mcp.ipynb` §2.2** (error shape → recovery router); `EX1/tools.py:32-35` `_err` + returns; `cli_project/core/tools.py:38-50` `_build_tool_result_part` (`is_error`) | — | generic "operation failed" |
| 2.3 Tool distribution | Too many tools (18 vs 4-5) degrades selection; scope per role; `tool_choice` auto/any/forced | **`notebooks/D2_tool_design_mcp.ipynb` §2.3** (3 tool_choice modes live + scope map); `EX4` `coordinator_sdk.py:50-60,73` per-subagent scoped `@tool` (real); `EX3` `extract.py:166-183` forced tool | **Q9** (scoped `verify_fact` for the 85% case) | #1 give synthesis all tools |
| 2.4 MCP servers in Claude Code | `.mcp.json` (project) vs `~/.claude.json` (user); `${ENV}` expansion; resources = catalogs | **`notebooks/D2_tool_design_mcp.ipynb` §2.4** (parses real `.mcp.json` + resources); `EX2/.mcp.json:1-21`; `cli_project/mcp_server.py:44-60` `docs://` resource | — | commit secrets / custom over community |
| 2.5 Built-in tools | Grep=content, Glob=paths, Read/Write/Edit; Edit fails on non-unique → Read+Write | **`notebooks/D2_tool_design_mcp.ipynb` §2.5** (Grep vs Glob vs Edit→Read+Write, real files); `EX2/CLAUDE.md`; this Claude Code session | — | reading all files upfront |

## Domain 3 — Claude Code Configuration & Workflows (20%)

| Task | What it really means | Concrete anchor | Sample Q | Distractor pattern |
|---|---|---|---|---|
| 3.1 CLAUDE.md hierarchy | user / project / directory; user-level NOT shared via VCS; `@import`; `.claude/rules/` | `EX2/CLAUDE.md`; `queries/CLAUDE.md` | — | user-level for team config |
| 3.2 Slash commands & skills | `.claude/commands/` (project, VCS) vs `~/.claude/commands/`; SKILL.md frontmatter `context: fork`, `allowed-tools` | `EX2/.claude/commands/`, `EX2/.claude/skills/` | **Q4** (`.claude/commands/`) | #4 `.claude/config.json` array |
| 3.3 Path-specific rules | `.claude/rules/` YAML `paths:` globs; load only on matching files | `EX2/.claude/rules/*.md` | **Q6** (globs for tests spread everywhere) | subdir CLAUDE.md for spread files |
| 3.4 Plan vs direct | Plan = large/architectural/multi-approach; direct = single well-scoped change; Explore subagent | `EX2` plan-mode experiments | **Q5** (monolith→microservices = plan mode) | direct-then-switch-if-complex |
| 3.5 Iterative refinement | Concrete I/O examples; test-driven iteration; interview pattern; batch interacting fixes | `EX5` test-first; `app_starter/tests` | — | prose over examples |
| 3.6 CI/CD integration | `-p`/`--print`; `--output-format json` + `--json-schema`; CLAUDE.md context; independent review instance | `EX5` (`claude -p ... --json-schema`) | **Q10** (`-p` flag) | #4 `CLAUDE_HEADLESS`, `--batch` |

## Domain 4 — Prompt Engineering & Structured Output (20%)

| Task | What it really means | Concrete anchor | Sample Q | Distractor pattern |
|---|---|---|---|---|
| 4.1 Explicit criteria | Specific categorical criteria > "be conservative"; false positives erode trust | `EX5` review criteria; `EX1` escalation criteria | **Q3** (explicit escalation criteria) | #5 sentiment/confidence proxy |
| 4.2 Few-shot | Most effective for consistent format + ambiguous-case judgment + extraction | `EX3` few-shot; `EX1` escalation examples | — | detailed instructions alone |
| 4.3 Structured output via tool_use | tool_use + JSON schema = no syntax errors (not semantic); `tool_choice` auto/any/forced; nullable fields | `EX3/extract.py` schema + tool_choice | — | strict schema fixes semantics (false) |
| 4.4 Validation / retry | Append validation errors on retry; retry useless if info absent; semantic vs syntax errors | `EX3` validation-retry loop | — | retry when info simply absent |
| 4.5 Batch processing | Batches API: 50% off, ≤24h, no SLA, no multi-turn tools; `custom_id`; not for blocking | `EX5` notes (sync for pre-merge) | **Q11** (batch reports only) | switch blocking checks to batch |
| 4.6 Multi-pass review | Self-review weak (retains reasoning); independent instance; per-file + integration passes | `EX5` independent reviewer; `EX1` | **Q12** | #1 bigger context window |

## Domain 5 — Context Management & Reliability (15%)

| Task | What it really means | Concrete anchor | Sample Q | Distractor pattern |
|---|---|---|---|---|
| 5.1 Preserve context | "Case facts" block outside summary; trim verbose tool outputs; lost-in-the-middle | **`notebooks/D5_context_reliability.ipynb` §5.1** (case-facts vs progressive-summary, real calls); `EX3` `extract.py:234-241` trim; `EX1` `tools.py:78-81` handoff | — | progressive summarization of numbers |
| 5.2 Escalation / ambiguity | Triggers: customer asks, policy gap, no progress; honor explicit requests; multi-match → ask for ID | **`notebooks/D5_context_reliability.ipynb` §5.2** (escalate-vs-resolve, real decisions); `EX1` `agent.py:32-38,52-54`, `tools.py:38-55` multi-match | **Q3** | #5 sentiment ≠ complexity |
| 5.3 Error propagation | Structured error context (failure type, attempted query, partials, alternatives); access-fail vs empty-result | **`notebooks/D5_context_reliability.ipynb` §5.3** (structured vs generic, real SDK recovery); `EX4` `coordinator.py:64-68,72-81,191-200` | **Q8** (structured error context) | suppress error / kill workflow |
| 5.4 Large codebase context | Scratchpad files; subagent delegation; state manifests for crash recovery; `/compact` | **`notebooks/D5_context_reliability.ipynb` §5.4** (real Task delegation + manifest); `EX4` `coordinator.py:156-167` manifest | — | re-explore from scratch |
| 5.5 Human review / confidence | Aggregate accuracy hides per-type gaps; stratified sampling; field-level calibrated confidence | **`notebooks/D5_context_reliability.ipynb` §5.5** (per-field confidence routing, real calls); `EX3` `extract.py:66-81,143,218-230` | — | trust 97% aggregate |
| 5.6 Provenance | Claim-source mappings preserved through synthesis; conflicts annotated; dates prevent false contradictions | **`notebooks/D5_context_reliability.ipynb` §5.6** (conflict synthesis, real calls); `EX4` `coordinator.py:51-61,214-216,226-238` | — | arbitrarily pick one value |

---

## The 12 sample questions → one-line takeaway

1. **A** — programmatic prerequisite (gate), not prompt. *Hook beats prompt for compliance.*
2. **B** — expand tool descriptions first. *Cheapest root-cause fix.*
3. **A** — explicit escalation criteria + few-shot. *Not sentiment, not self-confidence, not ML.*
4. **A** — `.claude/commands/` (project, VCS-shared).
5. **A** — plan mode (architectural, dozens of files).
6. **A** — `.claude/rules/` globs (tests spread everywhere; subdir CLAUDE.md can't).
7. **B** — coordinator's decomposition too narrow. *Blame the right component.*
8. **A** — structured error context to coordinator.
9. **A** — scoped `verify_fact` tool for the 85% case (least privilege).
10. **A** — `-p` flag. *(`CLAUDE_HEADLESS`/`--batch` don't exist.)*
11. **A** — batch for overnight reports only; sync for blocking pre-merge.
12. **A** — split into per-file + integration passes (not a bigger model).
