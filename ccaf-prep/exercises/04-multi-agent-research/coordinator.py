"""
Exercise 4 — coordinator–subagent multi-agent RESEARCH (hub-and-spoke), D5 RELIABILITY companion.

Run:  cd ccaf-prep/exercises/04-multi-agent-research && uv run python coordinator.py
Env:  ANTHROPIC_API_KEY (+ optional CLAUDE_MODEL) — copy ccaf-prep/.env.example to ccaf-prep/.env.

The REAL delegation mechanism (D1.2/1.3 — Task tool, allowedTools, AgentDefinition, SDK-isolated
context) lives in `coordinator_sdk.py` (run that for the genuine spawn). THIS file is the raw-API
companion: a hand-rolled hub-and-spoke (each "subagent" is a separate `client.messages.create`
with its OWN `messages` list => isolated context) whose job is to stage the RELIABILITY layer the
exam tests here — D5.3 structured error propagation, D5.4 manifest/crash-recovery, D5.6 provenance
+ conflict annotation — plus the anti-pattern toggles, deterministically and cheaply without
spawning real subagents.

Toggles that drive the learning (defaults shown; flip ONE per study step, reset between):
  - DYNAMIC_SELECTION = True  -> coordinator inspects the query and selects WHICH subagents to run.
                                 Flip False = always-run-full-pipeline anti-pattern (D1.2).
                                 MECHANISM is DETERMINISTIC: the simple query runs 3 subagents
                                 instead of 1, the SAME way every run.
  - PASS_CONTEXT     = True   -> prior findings are passed IN the synthesis prompt as STRUCTURED,
                                 attributed data. Flip False = synthesis subagent is blind (D1.3).
                                 MECHANISM is DETERMINISTIC (no findings reach the prompt); whether
                                 the blind output looks visibly worse is model-dependent — here it
                                 plainly does (the subagent asks for the info it was never given).

Teaching simplification (mirror EX1's identity note — the MECHANISM is real, the DATA is fake):
  - verify_fact() does NOT fact-check anything: it returns a self-asserted {"verified": True,
    "note": "checksum ok (toy)"}. It exists to show a SCOPED cross-role tool (D2.3), not real
    verification — never treat a tool's own "verified: true" as proof.
  - web_search / load_document / landmark_lookup return HARDCODED records from _FACTS, not live
    sources. One figure is DELIBERATELY conflicting (web 37.0M vs doc 41.0M, different dates) so the
    D5.6 provenance + conflict-annotation path has something to annotate. The hub-and-spoke,
    isolation, error propagation and manifest logic are real; the "facts" are a fixture.

Watch for these observable lines: ISOLATION PROOF, the [coordinator] selection line, the
synthesis output WITH vs WITHOUT context, the STRUCTURED ERROR, and the PROVENANCE report
(claim->source, with a conflict ANNOTATED not silently resolved).
"""
import json
from pathlib import Path
import os

from dotenv import load_dotenv, find_dotenv
from anthropic import Anthropic

# ---- portable key + model load (no machine paths) -----------------------------------------
_env = find_dotenv(filename=".env", usecwd=True)
if not _env:  # fall back to the sibling course project's .env, if present
    for _p in Path(__file__).resolve().parents:
        if (_p / "claude-with-anthropic-api" / ".env").exists():
            _env = str(_p / "claude-with-anthropic-api" / ".env"); break
load_dotenv(_env)
MODEL = os.environ.get("CLAUDE_MODEL") or "claude-haiku-4-5"  # cheap default; set CLAUDE_MODEL=claude-sonnet-4-6 in .env for harder tasks

# ---- the two learning toggles -------------------------------------------------------------
DYNAMIC_SELECTION = True   # flip False -> always run full pipeline (D1.2 anti-pattern)
PASS_CONTEXT = True        # flip False -> synthesis subagent is blind (D1.3 anti-pattern)

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"          # D5.4 scratchpad / crash-recovery manifest

client = Anthropic()


# ===========================================================================================
# TINY toy "source backend". Each source-type tool returns STRUCTURED records carrying their
# OWN provenance (source label + date). One number deliberately CONFLICTS across sources so
# we can show provenance + conflict annotation (D5.6) instead of arbitrarily picking one.
# ===========================================================================================
_FACTS = {
    # web search: a population figure dated 2023
    "web": {"claim": "Tokyo metro population is about 37.0 million",
            "value": "37.0M", "source": "web:worldstats.example", "date": "2023-01"},
    # document analysis: a CONFLICTING population figure, different date/methodology
    "docs": {"claim": "Tokyo metro population is about 41.0 million",
             "value": "41.0M", "source": "doc:UN-WUP-2018.pdf p.12", "date": "2018-05"},
    # landmark facts (distinct subtopic -> partitioned scope, minimizes duplication)
    "landmark": {"claim": "Senso-ji is Tokyo's oldest temple (founded 645 AD)",
                 "value": "645 AD", "source": "web:tokyo-guide.example", "date": "2024-02"},
}


def _err(failure_type, attempted_query, partial=None, alternative=None):
    """D5.3 — STRUCTURED error context the coordinator can actually reason about.
    failure_type distinguishes 'access_failure' (retry?) from 'empty_result' (valid, no match)."""
    return {"isError": True, "failure_type": failure_type, "attempted_query": attempted_query,
            "partial_results": partial, "suggested_alternative": alternative}


# ---- the scoped "tools" each subagent is allowed to call (D2.3) ----------------------------
def web_search(query=None):
    if query and "outage" in query.lower():
        # access failure (timeout-like) -> NOT the same as a valid empty result
        return _err("access_failure", query, partial={"cached": _FACTS["web"]},
                    alternative="retry once, or fall back to document analysis (load_document)")
    if query and "unicorn" in query.lower():
        # a successful query that simply has no matches -> empty_result, do NOT retry forever
        return _err("empty_result", query, partial=None,
                    alternative="broaden the query or accept that no source covers this")
    return {"isError": False, **_FACTS["web"]}


def load_document(doc=None):
    # constrained alternative to a generic fetch_url (D2.3): validates it's a known doc
    if doc and not str(doc).endswith(".pdf"):
        return _err("access_failure", doc, partial=None,
                    alternative="load_document only accepts validated .pdf sources")
    return {"isError": False, **_FACTS["docs"]}


def landmark_lookup(query=None):
    return {"isError": False, **_FACTS["landmark"]}


def verify_fact(claim=None):
    # scoped cross-role tool given ONLY to synthesis for the high-frequency verify need (D2.3),
    # instead of handing synthesis the full web_search/load_document toolset.
    # TEACHING SIMPLIFICATION: this does NOT actually verify — it self-asserts verified=True. The
    # point is the SCOPING (D2.3), not the check. Real verification would re-query an independent source.
    return {"isError": False, "claim": claim, "verified": True, "note": "checksum ok (toy)"}


DISPATCH = {"web_search": web_search, "load_document": load_document,
            "landmark_lookup": landmark_lookup, "verify_fact": verify_fact}

# Per-subagent SCOPED tool lists (D2.3): each role gets ONLY what it needs, NOT every tool.
SUBAGENT_TOOLS = {
    "websearch": ["web_search"],
    "documents": ["load_document"],
    "landmark":  ["landmark_lookup"],
    "synthesis": ["verify_fact"],          # scoped cross-role tool, NOT web_search/load_document
}


# ===========================================================================================
# A subagent = a FRESH client.messages.create with its OWN messages list => ISOLATED CONTEXT.
# It does NOT inherit the coordinator's history. If it needs a fact, the coordinator must put
# it in THIS prompt. Subagents never talk to each other; everything routes through the hub.
# ===========================================================================================
def subagent(role_system, task):
    msgs = [{"role": "user", "content": task}]        # <- isolated context begins here  # D1.2
    r = client.messages.create(model=MODEL, max_tokens=120, system=role_system, messages=msgs)
    return "".join(b.text for b in r.content if b.type == "text").strip()


# ---- search/analysis subagents: deterministic tool fetch + a 1-line natural-language gloss.
# We call the scoped tool ourselves (the coordinator routes), then ask the subagent to phrase
# the finding. Tool I/O is structured; the LLM only adds a human sentence. Keeps it cheap.
def research_subagent(name, role_system, tool_name, tool_args):
    """Returns a STRUCTURED finding {finding, value, source, date} OR a structured error (D5.3)."""
    raw = DISPATCH[tool_name](**tool_args)            # coordinator routes the scoped tool  # D2.3
    if raw.get("isError"):
        return raw                                    # propagate structured error UP, don't suppress
    gloss = subagent(role_system, f"In ONE short sentence, restate this finding:\n{raw['claim']}")
    return {"isError": False, "finding": gloss, "value": raw["value"],
            "source": raw["source"], "date": raw["date"]}


# ===========================================================================================
# COORDINATOR — owns decomposition, dynamic selection, routing, aggregation, error handling.
# ===========================================================================================
def select_subagents(query):
    """D1.2 dynamic selection: inspect the query, pick WHICH subagents to invoke.
    Simple query -> fewer subagents. DYNAMIC_SELECTION=False -> always the full pipeline."""
    full = ["websearch", "documents", "landmark"]
    if not DYNAMIC_SELECTION:
        return full                                   # anti-pattern: always run everything
    q = query.lower()
    chosen = []
    if "population" in q or "how many" in q:
        chosen += ["websearch", "documents"]          # numeric claim -> corroborate 2 source types
    if "landmark" in q or "temple" in q or "famous" in q:
        chosen += ["landmark"]
    return chosen or ["websearch"]                    # default: a single source type for simple asks


def write_manifest(query, selected, phase_status, findings, errors, status="in_progress"):
    """D5.4 — scratchpad/state manifest: persist progress so a crash can RESUME without
    re-exploring. Written INCREMENTALLY (after each subagent, and each marked 'in_progress'
    BEFORE it runs) so a mid-exploration crash leaves the last good checkpoint on disk, then
    ONCE MORE at the end (status='complete'). The coordinator loads this on restart and injects
    it into prompts — and skips any subagent already marked 'complete'."""
    manifest = {
        "query": query,
        "selected_subagents": selected,
        "status": status,                  # 'in_progress' until the whole run finishes -> 'complete'
        "phase_status": phase_status,       # per-subagent: pending | in_progress | complete | error
        "completed": [k for k, v in findings.items() if not v.get("isError")],
        "errors": {k: v for k, v in errors.items()},
        "findings": findings,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    return manifest


# Map each selectable subagent to its role-system + scoped tool call.
PLAN = {
    "websearch": ("You report ONLY web-sourced facts. Be terse.", "web_search", {"query": "Tokyo population"}),
    "documents": ("You report ONLY document-analysis facts. Be terse.", "load_document", {"doc": "UN-WUP-2018.pdf"}),
    "landmark":  ("You report ONLY landmark facts. Be terse.", "landmark_lookup", {"query": "Tokyo landmark"}),
}


def coordinate(query):
    print(f"\n{'='*78}\nQUERY: {query}\n  [DYNAMIC_SELECTION={DYNAMIC_SELECTION}  "
          f"PASS_CONTEXT={PASS_CONTEXT}]\n{'='*78}")

    # --- D1.2 decomposition + dynamic selection -------------------------------------------
    selected = select_subagents(query)
    print(f"[coordinator] selected {len(selected)} subagent(s): {selected}   "
          f"(scoped tools: {[SUBAGENT_TOOLS[s] for s in selected]})")     # <- D2.3 visible

    findings, errors = {}, {}
    # D5.4 — every phase starts 'pending'; we checkpoint the manifest AFTER each one (and mark a
    # phase 'in_progress' BEFORE it runs) so a crash mid-exploration leaves the last good state.
    phase_status = {name: "pending" for name in selected}
    write_manifest(query, selected, phase_status, findings, errors)   # initial checkpoint (all pending)
    for name in selected:                              # the hub routes to each spoke  # D1.2
        phase_status[name] = "in_progress"
        write_manifest(query, selected, phase_status, findings, errors)  # crash here -> 'in_progress' on disk
        role_sys, tool, args = PLAN[name]
        result = research_subagent(name, role_sys, tool, args)
        if result.get("isError"):
            # D5.3 — surface the STRUCTURED error; do NOT kill the workflow, keep going.
            errors[name] = result
            phase_status[name] = "error"
            print(f"[coordinator <- {name}]  STRUCTURED ERROR "
                  f"(failure_type={result['failure_type']}): attempted={result['attempted_query']!r}"
                  f"  alt={result['suggested_alternative']!r}")
        else:
            findings[name] = result
            phase_status[name] = "complete"
            print(f"[coordinator <- {name}]  {result['finding']}  "
                  f"[src={result['source']} | {result['date']}]")
        write_manifest(query, selected, phase_status, findings, errors)  # checkpoint AFTER each phase

    # --- D5.4 final manifest: status='complete' (both incremental AND terminal) -------------
    write_manifest(query, selected, phase_status, findings, errors, status="complete")
    print(f"[coordinator] wrote manifest -> {MANIFEST.name} "
          f"(completed={list(findings)}, errors={list(errors)})")

    if not findings:
        print("[coordinator] no usable findings; nothing to synthesize.")
        return

    # --- D1.3 context passing: STRUCTURED + ATTRIBUTED prior findings into the synth prompt -
    prior = [{"subtopic": k, "finding": v["finding"], "value": v["value"],
              "source": v["source"], "date": v["date"]} for k, v in findings.items()]
    synth_sys = ("You synthesize a 1-2 sentence briefing. PRESERVE each claim's [source] tag. "
                 "If two sources give CONFLICTING values, ANNOTATE the conflict with both "
                 "sources and dates — do NOT silently pick one.")          # <- D5.6 instruction
    if PASS_CONTEXT:
        ctx = json.dumps(prior, indent=2)
        synth = subagent(synth_sys, f"Findings to synthesize:\n{ctx}\n\nWrite the briefing.")
        print(f"\n[synthesis WITH passed context]:\n  -> {synth}")          # <- D1.3 ON
    else:
        # anti-pattern: isolated context, no findings passed -> synthesis is blind.
        synth = subagent(synth_sys, "Write the Tokyo briefing.")
        print(f"\n[synthesis WITHOUT passed context (blind, D1.3 anti-pattern)]:\n  -> {synth}")

    # --- D5.6 provenance: machine-readable claim->source map; conflicts ANNOTATED ----------
    print("\n[PROVENANCE] claim -> source (preserved through synthesis):")
    by_value = {}
    for p in prior:
        print(f"    - {p['finding']}  ==>  {p['source']}  ({p['date']})")
        by_value.setdefault(p["subtopic"], p)
    # detect the deliberate population conflict between websearch + documents
    if "websearch" in findings and "documents" in findings:
        w, d = findings["websearch"], findings["documents"]
        if w["value"] != d["value"]:
            print(f"    ! CONFLICT on population: {w['value']} [{w['source']} {w['date']}] "
                  f"vs {d['value']} [{d['source']} {d['date']}]  -> ANNOTATED, not resolved "
                  f"(coordinator decides; dates differ so it may not be a true contradiction).")


if __name__ == "__main__":
    # 1) Broad numeric+landmark query -> dynamic selection picks 3 subagents; surfaces the
    #    population CONFLICT (provenance) and a clean synthesis with sources.
    coordinate("What is Tokyo's population and a famous landmark?")

    # 2) Simple landmark-only query -> dynamic selection picks just ONE subagent (vs the
    #    full pipeline). Flip DYNAMIC_SELECTION=False to watch it over-run.
    coordinate("Tell me one famous Tokyo temple.")

    # 3) ISOLATION PROOF (D1.2): a FRESH subagent cannot see what the websearch subagent found.
    print(f"\n{'='*78}\nISOLATION PROOF (D1.2): subagents have isolated context\n{'='*78}")
    probe = subagent("Answer in one short sentence. If you don't know, say so plainly.",
                     "What population figure did the websearch subagent just report to the coordinator?")
    print(f"  fresh subagent (no prior findings in its prompt) -> {probe}")

    # 4) STRUCTURED ERROR (D5.3, sample Q8): force an access_failure and show it propagates
    #    UP as structured context (failure_type + partial + alternative), workflow survives.
    print(f"\n{'='*78}\nSTRUCTURED ERROR propagation (D5.3 / Q8)\n{'='*78}")
    for q in ["Tokyo population during the outage", "Tokyo unicorn population"]:
        e = web_search(query=q)
        print(f"  web_search({q!r}) -> failure_type={e['failure_type']}  "
              f"partial={e['partial_results'] is not None}  alt={e['suggested_alternative']!r}")
    print("  (access_failure => coordinator may RETRY/fallback; empty_result => valid, no match.)")
