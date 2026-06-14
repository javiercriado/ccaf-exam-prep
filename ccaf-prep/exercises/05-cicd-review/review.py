"""
Exercise 5 — a code-review pipeline for CI/CD (D1.6, D3.5, D3.6, D4.1, D4.5, D4.6).

Run:  cd ccaf-prep/exercises/05-cicd-review && uv run python review.py
Env:  ANTHROPIC_API_KEY (CLAUDE_MODEL optional) — copy ccaf-prep/.env.example to ccaf-prep/.env.

The whole exercise is one toggle:

  DECOMPOSE = True   -> each file is reviewed in its OWN clean call (per-file local pass),
                        THEN a SEPARATE cross-file integration pass runs. The cross-file
                        bug (a contract mismatch spanning two files) is only caught by the
                        integration pass.  (D1.6 decomposition, D4.6 multi-pass)

  DECOMPOSE = False  -> all files are jammed into ONE big prompt ("just use a bigger
                        context window"). Watch the cross-file bug get diluted/missed.
                        That is the sample-Q12 anti-pattern.  (D1.6/D4.6 distractor #1)

Other points made observable below:
  - D4.1  EXPLICIT categorical criteria (security/correctness/resource-leak) are passed,
          NOT "be conservative / find problems" (which causes false positives that erode trust).
  - D4.6  INDEPENDENT reviewer: every review runs in a FRESH message list. The reviewer
          never sees an author's "generation" conversation or reasoning — self-review is weak.
  - D3.6  STRUCTURED OUTPUT via tool_use + JSON input_schema so a CI step can parse the
          findings (severity / file / line / category / message).  See ci_review.sh for the
          headless `claude -p ... --json-schema` equivalent.
"""
import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv, find_dotenv

# portable env load (no machine paths); copy ccaf-prep/.env.example -> ccaf-prep/.env
_env = find_dotenv(filename=".env", usecwd=True)
if not _env:  # fall back to the sibling course project's .env, if present
    for _p in Path(__file__).resolve().parents:
        if (_p / "claude-with-anthropic-api" / ".env").exists():
            _env = str(_p / "claude-with-anthropic-api" / ".env"); break
load_dotenv(_env)
MODEL = os.environ.get("CLAUDE_MODEL") or "claude-haiku-4-5"   # cheap default; set CLAUDE_MODEL=claude-sonnet-4-6 in .env for harder tasks

# ---- the one toggle that drives the learning (flip to False for the Q12 anti-pattern)
DECOMPOSE = True                                                       # <- D1.6 / D4.6 / Q12

# ---------------------------------------------------------------------------------
# Toy "codebase": 2 tiny files. Each has one LOCAL bug; together they have one
# CROSS-FILE bug (a contract mismatch) that no single file reveals on its own.
# ---------------------------------------------------------------------------------
PAYMENTS_PY = '''\
# payments.py
def charge(account, amount):
    # LOCAL BUG (resource-leak): file handle is never closed.
    log = open("/tmp/charge.log", "a")
    log.write(f"charging {amount}\\n")
    account["balance"] = account["balance"] - amount
    # CROSS-FILE: returns a bare bool, but ledger.py expects a dict with "ok"/"txn_id".
    return True
'''

LEDGER_PY = '''\
# ledger.py
from payments import charge

def settle(account, amount):
    # LOCAL BUG (correctness): off-by-one — should be amount, not amount - 1.
    result = charge(account, amount - 1)
    # CROSS-FILE: dereferences result["ok"], but charge() returns a bare bool.
    if result["ok"]:
        return result["txn_id"]
    return None
'''

FILES = {"payments.py": PAYMENTS_PY, "ledger.py": LEDGER_PY}

# D4.1 — EXPLICIT, categorical review criteria. NOT "be conservative" / "find problems".
# Vague instructions -> false positives that erode developer trust in the whole reviewer.
CRITERIA = {
    "security": "Untrusted input reaching dangerous sinks; injection; secrets in code.",
    "correctness": "Logic that produces a wrong result (off-by-one, wrong operator, bad branch).",
    "resource-leak": "Files/sockets/handles opened and never closed; unreleased resources.",
}
CRITERIA_TEXT = "\n".join(f"  - {k}: {v}" for k, v in CRITERIA.items())
ALLOWED_CATEGORIES = list(CRITERIA) + ["cross-file"]

# D3.6 — structured output the CI step can parse. tool_use guarantees JSON SHAPE
# (no syntax errors); it does NOT guarantee the findings are semantically right.
REPORT_TOOL = {
    "name": "report_findings",
    "description": "Emit code-review findings as structured data for the CI pipeline to parse.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "category": {"type": "string", "enum": ALLOWED_CATEGORIES},
                        "message": {"type": "string"},
                    },
                    "required": ["severity", "file", "line", "category", "message"],
                },
            }
        },
        "required": ["findings"],
    },
}

CRITERIA_BLOCK = (
    "Review ONLY against these explicit categories (report nothing outside them; do not "
    "flag style/naming — vague nitpicks erode trust):\n" + CRITERIA_TEXT +
    "\nFor a multi-file contract mismatch use category 'cross-file'."
)


def _review(client, instruction, code_blocks, allow_cross_file):
    """Run ONE independent review in a FRESH message list (D4.6: no author reasoning context),
    forcing the structured-output tool (D3.6). Returns the list of findings."""
    cats = ALLOWED_CATEGORIES if allow_cross_file else list(CRITERIA)
    schema = json.loads(json.dumps(REPORT_TOOL))           # copy so we can scope the enum
    schema["input_schema"]["properties"]["findings"]["items"]["properties"]["category"]["enum"] = cats
    system = "You are an INDEPENDENT code reviewer. You did not write this code and have no "\
             "access to the author's reasoning. " + CRITERIA_BLOCK
    messages = [{"role": "user", "content": instruction + "\n\n" + "\n".join(code_blocks)}]
    resp = client.messages.create(
        model=MODEL, max_tokens=300, system=system, tools=[schema],
        tool_choice={"type": "tool", "name": "report_findings"},     # D4.3 forced tool
        messages=messages,
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "report_findings":
            return block.input.get("findings", [])
    return []


def review_decomposed(client):
    """D1.6 + D4.6: per-file LOCAL passes, then a SEPARATE cross-file INTEGRATION pass."""
    all_findings = []

    print("\n-- PER-FILE LOCAL PASSES (each file in its OWN call; no attention dilution) --")
    for fname, code in FILES.items():
        findings = _review(
            client,
            f"Review THIS ONE FILE ({fname}) for LOCAL issues only.",
            [f"=== {fname} ===\n{code}"],
            allow_cross_file=False,                                   # local pass can't see contracts
        )
        print(f"   [{fname}] local findings: {len(findings)}")
        for f in findings:
            print(f"      - {f['severity']:>6} {f['category']:<13} L{f['line']}: {f['message']}")
        all_findings += findings

    print("\n-- CROSS-FILE INTEGRATION PASS (data flow across files) --")
    integ = _review(
        client,
        "These files are reviewed together. Find ONLY cross-file CONTRACT mismatches: a value "
        "returned by one file but consumed with a different shape/type by another. "
        "Report each as category 'cross-file'.",
        [f"=== {n} ===\n{c}" for n, c in FILES.items()],
        allow_cross_file=True,
    )
    print(f"   integration findings: {len(integ)}")
    for f in integ:
        print(f"      - {f['severity']:>6} {f['category']:<13} {f['file']} L{f['line']}: {f['message']}")
    all_findings += integ
    return all_findings


def review_monolith(client):
    """ANTI-PATTERN (Q12, D1.6/D4.6 distractor #1): all files in ONE big prompt.
    'Just use a bigger context window' instead of decomposing -> attention dilution,
    the cross-file contract bug typically gets missed."""
    print("\n-- SINGLE BIG PROMPT (all files at once; the 'bigger context window' anti-pattern) --")
    findings = _review(
        client,
        "Review this entire codebase for any issues across all files.",
        [f"=== {n} ===\n{c}" for n, c in FILES.items()],
        allow_cross_file=True,
    )
    print(f"   findings: {len(findings)}")
    for f in findings:
        print(f"      - {f['severity']:>6} {f['category']:<13} {f['file']} L{f['line']}: {f['message']}")
    return findings


def main():
    client = Anthropic()
    print(f"{'='*72}\nCODE REVIEW PIPELINE  [DECOMPOSE={DECOMPOSE}  MODEL={MODEL}]\n{'='*72}")

    findings = review_decomposed(client) if DECOMPOSE else review_monolith(client)

    caught_cross_file = any(f.get("category") == "cross-file" for f in findings)
    print(f"\n{'='*72}")
    print(f"cross-file contract bug caught? {caught_cross_file}   "
          f"({'decomposition found it' if caught_cross_file else 'MISSED — diluted in one big prompt'})")

    # D3.6 — the final machine-parseable artifact a CI step would consume / post as comments.
    report = {"tool": "claude-review", "decompose": DECOMPOSE, "findings": findings}
    print("\n-- STRUCTURED OUTPUT (what CI parses) --")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
