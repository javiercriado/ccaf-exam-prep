# CCAF Exam Prep — Claude Certified Architect (Foundations)

> 🇪🇸 ¿Prefieres español? Lee el **[README en español](README.es.md)**.

A hands-on study kit for the **Claude Certified Architect – Foundations (CCAF)** exam,
mapped **1:1 to the official exam guide** — every domain, every task statement, and all
**6 official scenarios**. The notebooks teach each concept by making it *runnable*: they
make **real Claude API calls** (some via the **Claude Agent SDK**, a few via the raw
Messages API purely for learning) so you watch the behavior the exam tests actually happen,
instead of reading about it.

> [!IMPORTANT]
> **Unofficial & independent.** This repository is **not affiliated with, endorsed by, or
> produced by Anthropic.** It is a personal study project. I built it while preparing for the
> exam — **I have not taken the exam yet** (preparing as of 2026). Nothing here is a brain
> dump: everything traces back to the **official exam guide** and the **official Anthropic
> Academy courses**. The official guide itself is **not redistributed** here — download it
> from Anthropic (see [The exam guide](#the-exam-guide)).

## Why this repo

There are practice sites and repos that **invent** questions and drift away from what the
exam actually covers. This one is the opposite: it is deliberately **faithful to the official
material**. Each notebook section quotes the guide's task statement *verbatim*, then turns it
into code you can run; each sample question is the official one, mapped back to the task
statement it tests. If it isn't in the guide or the courses, it isn't here.

## Status & validation

I **personally designed, reviewed, studied, and ran every cell** of the domain notebooks that
exist — this is hand-built study material, not AI output dumped into a repo. The
[`ccaf-notebook` skill](.claude/skills/ccaf-notebook/SKILL.md) helps generate notebooks to a
fidelity standard, but **a skill's output is not validated on its own** — the human pass is
what makes a section trustworthy. Anything not yet marked ✅ is still being checked; verify it
against the official guide before you rely on it.

**Legend:** ✅ hand-validated (designed · reviewed · studied · run) · 🔧 in progress ·
🧪 built/generated, not yet hand-reviewed · ⏳ not built yet

| Domain notebook | Status | | Hands-on exercise | Status |
|---|:--:|---|---|:--:|
| D1 · Agentic Architecture & Orchestration | ✅ | | 01 · support-agent | ✅ |
| D2 · Tool Design & MCP Integration | ✅ | | 02 · claude-code-team | 🧪 |
| D5 · Context Management & Reliability | ✅ | | 03 · extraction-pipeline | 🧪 |
| D3 · Claude Code Configuration & Workflows | 🔧 | | 04 · multi-agent-research | 🧪 |
| D4 · Prompt Engineering & Structured Output | ⏳ | | 05 · cicd-review | 🧪 |

(Exercise 01 has had my hand-review/tuning pass; 02–05 currently run and are portable but
haven't been hand-reviewed yet.)

## Start here — prerequisites (do these first)

This kit assumes you've already done the **four official Anthropic Academy courses**. Do them
first, **take notes by hand**, and **complete their exercises** — that's where the muscle
memory comes from. Their code lives in [`claude-with-anthropic-api/`](claude-with-anthropic-api/).

| Official course | Mostly maps to |
|---|---|
| Building with the Claude API | **D4** Prompt Engineering & Structured Output |
| Claude Code in Action | **D3** Claude Code Configuration & Workflows |
| Introduction to Model Context Protocol (MCP) | **D2** Tool Design & MCP Integration |
| Introduction to Agent Skills | **D3** Claude Code Configuration & Workflows |

Courses are on **[Anthropic Academy](https://anthropic.skilljar.com/)** (and mirrored at
[github.com/anthropics/courses](https://github.com/anthropics/courses)). Everything — the
courses and the exam — is **in English**, so this kit is in English too (with this Spanish
README as a convenience).

## The exam at a glance

- **60 questions**, **120 minutes**, multiple-choice (1 correct + 3 distractors).
- **4 of 6 scenarios** are chosen at random for your sitting.
- Pass = **720 / 1000** scaled. **No penalty for guessing → never leave a blank.**
- Domain weights: **D1 27% · D3 20% · D4 20% · D2 18% · D5 15%**.

## What's inside

```
ccaf-prep/
  notebooks/      one notebook per domain + the mock exam
    D1_agentic_loops.ipynb          ✅  D1 · Agentic Architecture & Orchestration (27%)
    D2_tool_design_mcp.ipynb        ✅  D2 · Tool Design & MCP Integration (18%)
    D5_context_reliability.ipynb    ✅  D5 · Context Management & Reliability (15%)
    D3_claude_code_config.ipynb     🔧  D3 · Claude Code Configuration & Workflows (20%)
    D4_*.ipynb                      ⏳  D4 · Prompt Engineering & Structured Output (20%)
    mock_exam_and_review.ipynb      coverage checklist + the 12 sample Qs by scenario
    README.md                       the study-order guide
  exercises/      five cross-domain, runnable hands-on builds
    01-support-agent/      02-claude-code-team/      03-extraction-pipeline/
    04-multi-agent-research/         05-cicd-review/
  MAPPING.md      abstract task statement → concrete file:line → sample question (the index)
  STUDY_PLAN.md   the full schedule and rationale
  reference/      where YOU drop your downloaded exam_guide.txt (git-ignored — see its README)
claude-with-anthropic-api/   the official Anthropic course code + exercises
.claude/skills/ccaf-notebook/   the skill used to generate the notebooks (see below)
```

Each domain notebook follows the same anatomy per task statement: **verbatim guide quote →
plain-English table → a runnable cell that makes it observable → the anti-patterns as code
(the exam's wrong answers) → a pointer to the matching line in your own course/exercise code
→ a self-check**. Each ends with that domain's **official sample questions** (answers hidden).

## How to study (recommended order)

The order is **dependency-driven** so each exercise unlocks as soon as its domains are
covered — not pure exam weight:

1. **Notebooks:** `D1 → D2 → D5 → D3 → D4`. Run every cell; do the hidden sample questions
   actively (cover the answer, justify why each distractor is wrong, then reveal).
2. **Exercises, in waves** (they're cross-domain — none is single-domain):

   | After studying… | Do exercises | Domains used |
   |---|---|---|
   | D1 + D2 + D5 | **Ex1** then **Ex4** | D1 + D2 + D5 |
   | + D3 | **Ex2** | D3 + D2 |
   | + D4 | **Ex3** ∥ **Ex5** | D4 + D5 / D3 + D4 |

3. **Consolidate** in [`mock_exam_and_review.ipynb`](ccaf-prep/notebooks/mock_exam_and_review.ipynb):
   tick coverage as you finish each domain, then do the scenario-grouped mock at the end.
4. **Finally**, sit the official **Practice Exam** (Skilljar) under timed conditions.

### Which layer: raw Messages API vs Agent SDK (and why)

The exam tests **architecture concepts, not one SDK's syntax** — so the notebooks use
*whichever layer the concept actually lives at*, not a global preference:

- **Raw Messages API** (`client.messages.create`) when the concept **is a Messages-API primitive
  the SDK hides** and you need to *see* it: agentic loop / `stop_reason` (D1.1),
  `tool_use`/`tool_result`, tool descriptions & `tool_choice` (D2.1/2.3), structured errors /
  `isError` (D2.2), structured output via tool_use + JSON schema (D4.3/4.4), Batch (D4.5),
  single-turn decisions (D5.1/5.2/5.5/5.6).
  *(Raw-API tool use has two halves: Claude returns a `tool_use` block — that's "calling" the
  tool — and **your** code executes it and returns a `tool_result`. The API never runs your
  function; that loop is the protocol.)*
- **Agent SDK** (`query()` + `Task` / `AgentDefinition`) when the concept **is a runtime feature**
  — doing it raw would be faking it: coordinator + subagents + `Task` (D1.2/1.3),
  `PreToolUse`/`PostToolUse` hooks and deterministic gates (D1.4/1.5), sessions / `fork_session`
  (D1.7), multi-agent error propagation & delegation (D5.3/5.4).
- **Claude Code (config/CLI)** when it's **configuration, not code**: `CLAUDE.md`,
  `.claude/commands/`, `.claude/rules/`, plan mode, headless `-p` (D2.4, all of D3).

Rule of thumb: **Agent SDK / Claude Code is the predominant architecture *vocabulary*** (most of
D1, D3, and the multi-agent parts of D5); the **raw API exposes the primitive underneath** when
the concept *is* that primitive. Each notebook's setup cell states which layer it uses and why;
full detail in [`ccaf-prep/notebooks/README.md`](ccaf-prep/notebooks/README.md).

Keep [`ccaf-prep/MAPPING.md`](ccaf-prep/MAPPING.md) open as your index. The full rationale is
in [`ccaf-prep/STUDY_PLAN.md`](ccaf-prep/STUDY_PLAN.md).

## Setup

Requires **Python 3.12+** and **[uv](https://docs.astral.sh/uv/)**.

```bash
# 1. install dependencies (creates ccaf-prep/.venv)
cd ccaf-prep && uv sync

# 2. add your API key — copy the template at the repo root and edit it
cp ../.env.example ../.env
#    then put your key in ../.env:  ANTHROPIC_API_KEY=sk-ant-...
```

The `.env` is auto-discovered from anywhere in the repo (no path config needed). Calls
**default to `claude-haiku-4-5`** — the cheapest model — because these demos teach the
*mechanism*, not model IQ. Override everywhere with `CLAUDE_MODEL=...` in `.env`.

**Run a notebook:** open it in VS Code / Jupyter and select the `ccaf-prep` kernel, or run
all cells headless. **Run an exercise:**

```bash
cd ccaf-prep/exercises/01-support-agent && uv run python agent.py
```

Each exercise folder has its own `README.md` with the build steps, the task-statement tags,
and the **anti-pattern toggles** to try (flip a flag, watch the wrong approach fail).

### Keep your notebook outputs local, not committed

Notebook outputs are stripped from commits automatically (clean diffs, no leaked API
responses) while staying in your working copy. Enable it once per clone:

```bash
cd ccaf-prep && uv run nbstripout --install --attributes ../.gitattributes
```

### Track your own progress

The mock exam holds a coverage checklist. To record your progress **without committing it**,
make a personal copy (it's git-ignored):

```bash
cd ccaf-prep/notebooks && cp mock_exam_and_review.ipynb mock_exam_and_review.personal.ipynb
```

Keep handwritten-notes scans or any private notes in a git-ignored `personal/` folder.

## The exam guide

The official guide is **not included** (it's Anthropic's material). Download the
**Claude Certified Architect – Foundations Certification Exam Guide** from Anthropic. If you
want the notebook-generator skill to regenerate domains, save the guide's text as
`ccaf-prep/reference/exam_guide.txt` (git-ignored) — the **12 sample questions** reproduced in
the notebooks are the ones Anthropic publishes as samples in that guide.

## How the notebooks were built

The notebooks were generated and maintained with a Claude Code skill,
[`.claude/skills/ccaf-notebook/`](.claude/skills/ccaf-notebook/SKILL.md), which enforces the
fidelity rules above (verbatim quotes, real API calls, anchored `file:line` pointers). It's
included as a reference if you want to extend or regenerate domains.

## About me

**Javier Criado Gómez** — AI Engineer.
LinkedIn: https://www.linkedin.com/in/javierjcriadogomez/ · questions, suggestions, and corrections
welcome (open an issue or a PR). I'm sharing this to help others certify while I study for it
myself — once I've sat the exam I'll update this note.

## Contributing

Found something that drifts from the official material, or a notebook cell that doesn't run?
Open an issue or PR. The bar is **fidelity to the official guide and courses** — corrections
that pull it closer to the source are the most valuable.

## Disclaimer

Independent, community study material. **Not affiliated with or endorsed by Anthropic.**
"Claude" and "Anthropic" are trademarks of Anthropic. The official exam guide and courses are
Anthropic's; they are referenced and linked here, not redistributed. Provided as-is, for
educational use.
