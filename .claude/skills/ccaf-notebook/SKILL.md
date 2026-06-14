---
name: ccaf-notebook
description: Generate a CCAF (Claude Certified Architect – Foundations) exam-prep study notebook for one domain (D1–D5), with one section per task statement, following the validated D1/1.1 template (verbatim guide quote → plain-English table → runnable cell → anti-patterns → pointer to the user's own code → self-check). Use when the user asks to build, generate, or continue the exam-guide notebooks — e.g. "make the D2 notebook", "generate domain 3", "do the next task statements".
---

# CCAF exam-prep notebook generator

Produce a Jupyter notebook that teaches one exam **domain**, turning each abstract task
statement into something **observable and runnable** — the same shape as the proven
template `ccaf-prep/notebooks/D1_agentic_loops.ipynb`. The user is studying for the Claude
Certified Architect – Foundations exam and learns by running code and mapping it back to the
guide. Abstractness is the enemy; every claim must become a line you can run or a file you
can open.

## Input

The domain to build, e.g. `D2`, `domain 3`, `D5`. If not given, ask which domain (D1 is
already done as the template). Build **one notebook per domain** (decided with the user):
all of that domain's task statements as ordered sections in a single file, so one running
example can grow across the domain (e.g. a toy agent gains a 2nd tool, then a gate, then a
decomposition). Read top-to-bottom in guide order (N.1 → N.2 → …).

## Step 1 — Read the sources (do this first, every time)

Always work from the real files, never from memory:

1. **`ccaf-prep/reference/exam_guide.txt`** — the authoritative guide. Structure markers:
   `Domain N:`, `Task Statement N.M:`, `Knowledge of:`, `Skills in:`. Pull each task
   statement's text **verbatim** (every Knowledge-of + Skills-in bullet). `grep -n` the
   markers to find line ranges, then read them.
2. **`ccaf-prep/MAPPING.md`** — per task statement: the concrete anchor (which exercise
   folder / course file), the sample question number, and the distractor pattern. These feed
   the "pointer to your own code" and "anti-pattern" sections.
3. **The anchor code itself** — the exercise folders `ccaf-prep/exercises/0X-*/` and the course code
   under `claude-with-anthropic-api/` (e.g. `cli_project/core/chat.py`,
   `cli_project/core/tools.py`, `mcp_server.py`). Open what MAPPING.md points to and cite
   **exact `file:line` ranges** — verify the lines exist right now (code drifts; never cite
   from memory).
4. **The template** `ccaf-prep/notebooks/D1_agentic_loops.ipynb` — mirror its structure and
   tone exactly. When unsure how deep to go, match the 1.1 section.

## Step 2 — Build the notebook: one SECTION per task statement

Each task statement N.M becomes a run of cells following this **6-part anatomy** (this is
what made 1.1 work — do not drop parts):

1. **Verbatim guide quote** (markdown, blockquote). The full task statement: title +
   every Knowledge-of and Skills-in bullet, copied exactly from `exam_guide.txt`. The user
   should never have to reopen the PDF.
2. **Plain-English unpacking** (markdown table). One row per bullet: left column the guide
   phrase, right column what it means concretely ("`end_turn` = I'm done"). Demystify jargon.
3. **A runnable cell** (code) that makes the concept **observable** — print a `stop_reason`, the
   tool Claude actually chose, the recovery Claude actually took, a validation retry, etc. If the
   concept is a Claude behavior, this cell **must make a real model call** and let Claude produce
   the observable (see the "Claude API call MUST be real" standard below) — never print the output
   of a Python `if`/`switch` that hardcodes what Claude *would* do. Prefer evolving the domain's
   running example over inventing a new one. It must actually run and print something that *is* the
   task statement happening.
4. **Anti-patterns as commented code** (code cell, commented out). Turn the MAPPING.md
   "distractor pattern" into 2–3 wrong approaches written as code, each with a one-line
   comment on why it's fragile. These are the exam's wrong answers — the user should learn to
   recognize them. End with a `print(...)` stating the one correct approach.
5. **Pointer to the user's own code** (markdown). The exact `file:line` in their course /
   exercise code that does this for real ("you already wrote this"). Verify the lines. Tell
   them to open it and map each line to a bullet.
6. **Self-check** (markdown, `<details><summary>answers</summary>`). 3–4 questions with
   covered answers, targeting the distractors and the one true rule.

Open the domain notebook with a domain-title markdown cell (`# Domain N · <name> (XX%)`) and
a "How to use this notebook" note. Close with a short "coming next / related domains" cell.

## Step 2b — Two closing cells per domain notebook (sample questions + exercise block)

After the last task statement, every domain notebook ends with TWO markdown cells (see
[[ccaf-review-assets]] for the full convention and `D1`/`D2` for the live shape):

1. **`## Sample exam questions — Domain N`** — the official guide questions whose *tested
   skill* lives in this domain, **verbatim** (prompt + A–D options), answer + explanation
   hidden under `<details><summary>Answer + explanation</summary>` (same mechanism as the
   self-checks). Each question gets a `<sub>Maps to: D_ §N.M …</sub>` line. Source the text
   from `reference/exam_guide.txt` (the "Sample Questions" section, ~lines 937–1244); pick
   the question→domain assignment from `MAPPING.md`'s "Sample Q" column:
   - D1 → Q7, Q1, Q12 · D2 → Q2, Q9 · D3 → Q4, Q5, Q6, Q10 · D4 → Q11, Q12, Q3 · D5 → Q8, Q3.
   - **Cross-domain questions are FULLY DUPLICATED in both domains** (user's call, not
     "assign to one primary"): **Q12** spans D1 §1.6 + D4 §4.6; **Q3** spans D4 §4.1 +
     D5 §5.2. In each copy, end the Maps-to line with "— spans two domains".
2. **`## Exercises that use this domain`** — a table of which `exercises/0X-*/` folders
   reinforce this domain, their *full* domain set, and which domains must be studied first
   (exercises are cross-domain; none is single-domain). Map: Ex1 D1+D2+D5 · Ex2 D3+D2 ·
   Ex3 D4+D5 · Ex4 D1+D2+D5 · Ex5 D3+D4. Note the exercise *wave* it belongs to (study order
   `D1→D2→D5→D3→D4`; waves: after D5 → Ex1→Ex4, after D3 → Ex2, after D4 → Ex3∥Ex5).

**Do NOT touch `notebooks/mock_exam_and_review.ipynb` or `notebooks/README.md`** when
building a domain — they are already complete (all 12 questions by scenario, full coverage
checklist, study-order guide) and the mock holds the user's checkbox progress. Regenerating
them destructively would wipe that progress.

## Notebook-wide conventions (reuse exactly — these were debugged already)

- **Setup cell** must load the key from the user's single `.env` (do NOT assume the env var
  is present in the kernel — the VS Code kernel does not source the shell). Use this exact
  pattern at the top of the first code cell:

  ```python
  from anthropic import Anthropic
  from dotenv import load_dotenv, find_dotenv
  from pathlib import Path
  import os, json

  # Portable .env discovery — nearest .env walking up from the working dir (repo
  # root or ccaf-prep/), then the sibling course .env. No machine-specific paths.
  _candidates = [Path.cwd().parents[1] / "claude-with-anthropic-api" / ".env"]
  _found = find_dotenv(filename=".env", usecwd=True)
  _envfile = Path(_found) if _found else next((p for p in _candidates if p.exists()), None)
  if _envfile: load_dotenv(_envfile); print(f"Loaded .env from: {_envfile}")
  else: print("WARNING: no .env found — copy .env.example to .env at the repo root")
  assert os.environ.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY not set — see .env.example"

  client = Anthropic()
  MODEL = os.environ.get("CLAUDE_MODEL") or "claude-haiku-4-5"   # cheap default (see convention below)
  print("Using model:", MODEL)
  ```

- **Tool calling**: always dispatch by name via a `TOOL_FUNCS = {name: func}` registry and
  `func = TOOL_FUNCS.get(block.name)` — never hardcode a single function. Include the
  `is_error` field in `tool_result`. (Good habit; matches Domain 2.)
- **Stop condition**: loop while `stop_reason == "tool_use"`, stop on `"end_turn"`. Never
  parse text or use the iteration cap as the real stop — call those out as anti-patterns.
- **Default to Haiku for every call — it is the cheapest model and the user is deliberately
    saving money.** Notebook cells AND exercises: `MODEL = os.environ.get("CLAUDE_MODEL") or
  "claude-haiku-4-5"` (raw Messages API) or `model="haiku"` (Agent SDK). These demos teach the
  *mechanism*, not high-IQ replies, so Haiku is plenty and ~10× cheaper — never reach for Sonnet/
  Opus "to make it work." Keep API calls cheap in every other dimension too (small `max_tokens`,
  tiny toy tools/data, one call per concept, low `max_turns`). Always keep the `CLAUDE_MODEL` env
  override so the whole notebook/exercise can be bumped to `claude-sonnet-4-6` from one place
  *only if* a specific demo turns out genuinely flaky on Haiku — Haiku stays the committed default.
- Keep API calls **cheap**: small `max_tokens`, tiny toy tools/data, one call per concept.
- **Teach the mechanism for real; fixtures behind tools are fine.** The thing the section
  *teaches* (a Task spawn, an `allowed_tools` gate, a Pre/PostToolUse hook, the agent loop) must
  be the REAL SDK mechanism — never simulate or bypass it. The *backend behind a tool* (e.g. a
  canned `get_weather`, a fake billing store) SHOULD be a deterministic in-code fixture — do NOT
  wire live external APIs into teaching code (flaky, costs, needs keys). Mocking what's mockable
  for clarity is encouraged; faking the mechanism under test is not.
- **The Claude API call MUST be real whenever the lesson is a Claude behavior/decision.** This is
  the #1 trap and it has bitten us (D2 §2.2 originally faked it). If the task statement is about
  *what Claude does* given some input — picks a tool, recovers from a structured error, obeys a
  `tool_choice`, retries on validation feedback, decomposes a task — the demo MUST call
  `client.messages.create(...)` (raw Messages API) or `query(...)`/the Agent SDK and let **Claude**
  produce the observable. A Python `if`/`switch`/dict that hardcodes "what Claude *would* decide"
  is BANNED: it teaches your routing logic, not Claude's, and is exactly the abstraction the user
  is studying *against*. Canonical fix to mirror: §2.2's `run_until_done` loop hands a mocked
  backend's structured error back via a real `tool_result` and lets Claude choose to retry
  (transient) vs explain (business) — fixture backend, **real** decision. **Deciding test:** does the
  *section* contain a real model call that exercises the taught mechanism? If yes, an extra
  pure-Python *scaffold* cell is fine and often good — e.g. D1 §1.4 shows a deterministic gate as
  isolated Python (the lesson there is that enforcement is *model-independent*), then wires that
  same gate into a **real** `PreToolUse` hook + `query()` loop in the next cell. That is legitimate
  (scaffold *then* real loop). The ban is specifically a Python `if`/`switch` that *stands in for*
  Claude's decision when **no** real call exercises it anywhere in the section (old §2.2). The ONLY cells allowed to
  have no Claude call are ones where there is genuinely no Claude call to make: pure-config tasks
  shown as real files (`.mcp.json`, `CLAUDE.md`) and Claude Code *harness* built-ins (Grep/Glob/
  Edit) that aren't API calls at all — and those must read/operate on the user's REAL artifacts,
  never a paraphrase.
- **Never use `permission_mode="bypassPermissions"` in Agent SDK cells/exercises** — it switches
  off the very allow-list the lesson is about. Use `permission_mode="default"` and put the real
  tool names in `allowed_tools`. Verified SDK facts to teach accurately: `allowed_tools` is a
  **global** execution gate (an `mcp__*` tool absent from it is *denied*; there is no per-agent
  permission — `can_use_tool` needs streaming mode and carries no caller id); the real per-subagent
  scope is `AgentDefinition(tools=[…])` (a subagent literally can't call a tool not in its list);
  and "`allowedTools` must include `Task`" is the documented contract, though `Task` is a built-in
  that may still spawn if omitted — list it as the rule says, but don't claim it hard-blocks.
- Markdown headers per task statement (`## N.M · <title>`) so VS Code's Outline panel
  navigates the file.

## Step 3 — Verify before declaring done (mandatory)

Notebooks that don't run are worse than useless for studying. `ccaf-prep/` is a self-contained
uv project (`pyproject.toml`: anthropic + python-dotenv + ipykernel). Execute every code cell
with `uv run` and confirm clean output + the expected observable line:

```bash
cd ccaf-prep
uv run python -c "
import json
nb = json.load(open('notebooks/D<N>_<slug>.ipynb'))
code = '\n\n'.join((c['source'] if isinstance(c['source'], str) else ''.join(c['source'])) for c in nb['cells'] if c['cell_type']=='code')
exec(compile(code, 'notebook', 'exec'))
"
```

Then run the **real-call gate**: for every task statement whose lesson is a Claude
behavior/decision (per the standard above), confirm its runnable cell actually calls the model —
`grep -c "client.messages.create\|query(" ` the notebook's code, and eyeball that each such section
has at least one. A section with zero Claude calls is only acceptable if it is a pure-config or
harness-built-in task (the documented exceptions). If you find a `plan_recovery`-style Python
`if`/`switch` standing in for Claude's decision, it FAILS the gate — rewrite it as a real call
(mirror §2.2's `run_until_done`) before declaring done.

If anything errors, fix the notebook and re-run until green. The `ccaf-prep/.venv` is native
arm64 (built by `uv sync`) and has everything needed. Do NOT use any stale `.venv` that points
at `/usr/local/opt` — that's a dead Intel path (see the broken-venv memory). The runnable
EXERCISE scripts (`exercises/01-support-agent/` … `exercises/05-cicd-review/`) run the same way: from the exercise
folder, `uv run python <script>.py` (uv finds `../pyproject.toml`).

## Step 4 — Wire it up and report

- Save as `ccaf-prep/notebooks/D<N>_<short_slug>.ipynb`.
- Update `ccaf-prep/MAPPING.md`: point each task statement's anchor at the new notebook
  (as 1.1 points at `D1_agentic_loops.ipynb`).
- Tell the user: which task statements were covered, the running example used, any
  `file:line` pointers cited, and the verification result (what the cells printed). Then ask
  if the depth is right before building the next domain.

## Quality bar

Verbatim guide text (no paraphrase in the quote cell). Every code cell runs and prints the
concept. Distractors come from MAPPING.md, written as code. Every "your own code" pointer is
a real, verified `file:line`. If you can't make a task statement observable in code (some are
config/CLI concepts — e.g. `.mcp.json`, CLAUDE.md hierarchy, `claude -p`), show it as a real
file/command the user creates or runs, plus the anchor — never leave it abstract.
