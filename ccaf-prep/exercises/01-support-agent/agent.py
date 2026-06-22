"""
Exercise 1 — the agentic loop (D1.1) with a deterministic enforcement gate (D1.4/1.5).

Run:  cd ccaf-prep/exercises/01-support-agent && uv run python agent.py
Env:  ANTHROPIC_API_KEY (+ optional CLAUDE_MODEL) — copy ccaf-prep/.env.example to ccaf-prep/.env.

Two toggles drive the learning:
  - tools.GOOD_DESCRIPTIONS  -> flip False to watch tool MISROUTING (D2.1, sample Q2).
  - ENFORCE (below)          -> flip False to watch the PROMPT-ONLY anti-pattern fail
                                to guarantee verify-before-refund (D1.4, sample Q1).

Watch the printed `stop_reason` each turn: the loop continues on "tool_use" and
terminates on "end_turn". That single line IS Task Statement 1.1.
"""
import json, os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv, find_dotenv
import tools

# Self-load the key from the single .env so a bare run just works (no `export` step).
# Portable discovery (no machine paths): nearest .env walking up, else the sibling course .env.
_env = find_dotenv(filename=".env", usecwd=True)
if not _env:
    for _p in Path(__file__).resolve().parents:
        if (_p / "claude-with-anthropic-api" / ".env").exists():
            _env = str(_p / "claude-with-anthropic-api" / ".env"); break
load_dotenv(_env)

MODEL = os.environ.get("CLAUDE_MODEL") or "claude-haiku-4-5"   # cheap default; set CLAUDE_MODEL=claude-sonnet-4-6 in .env for harder tasks
MAX_TURNS = 12                # SAFETY backstop only — NOT the primary stop (anti-pattern 1.1)

# ---- toggle: flip to False to study the D1.4 / Q1 anti-pattern (prompt-only enforcement)
ENFORCE = True

SYSTEM = (
    "You are a customer-support resolution agent. Resolve returns, billing, and account "
    "issues. Always verify the customer with get_customer before any order or refund "
    "operation. Refunds over $500 must be escalated to a human, not processed. When you "
    "escalate, include a full handoff summary. Decompose multi-issue requests and address "
    "each part."
)


def gate(name, tool_input, verified_ids):
    """D1.4/D1.5 — deterministic enforcement. Returns an error string to block, or None
    to allow. This is what the Agent SDK formalizes as a PreToolUse hook; in the raw API
    you enforce it right here in the loop. Prompt instructions (SYSTEM) have a non-zero
    failure rate — this does not."""
    if not ENFORCE:
        return None
    if name == "process_refund":
        if not verified_ids:
            return ("BLOCKED: customer identity not verified. Call get_customer "
                    "successfully before processing any refund.")
        if (tool_input.get("amount") or 0) > 500:
            return ("BLOCKED: refunds over $500 cannot be processed automatically. "
                    "Use escalate_to_human with a full handoff summary.")
    return None


def run(user_message):
    client = Anthropic()
    schemas = tools.tool_schemas()
    messages = [{"role": "user", "content": user_message}]
    verified_ids = set()   # populated when get_customer returns a real record

    print(f"\n{'='*70}\nUSER: {user_message}\n  [ENFORCE={ENFORCE}  "
          f"GOOD_DESCRIPTIONS={tools.GOOD_DESCRIPTIONS}]\n{'='*70}")

    for turn in range(MAX_TURNS):
        resp = client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM,
                                      tools=schemas, messages=messages)
        print(f"\n-- turn {turn}  stop_reason={resp.stop_reason} --")  # <- D1.1

        if resp.stop_reason == "end_turn":                              # <- D1.1 terminate
            text = "".join(b.text for b in resp.content if b.type == "text")
            print(f"AGENT: {text}")
            return

        if resp.stop_reason == "tool_use":                             # <- D1.1 continue
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                blocked = gate(block.name, block.input, verified_ids)
                if blocked:
                    print(f"   GATE blocked {block.name}: {blocked}")
                    out, is_err = {"isError": True, "errorCategory": "permission",
                                   "isRetryable": False, "description": blocked}, True
                else:
                    out = tools.DISPATCH[block.name](**block.input)
                    is_err = bool(out.get("isError"))
                    if block.name == "get_customer" and not is_err:
                        verified_ids.add(out["id"])                    # <- enables the gate
                    print(f"   {block.name}({block.input}) -> {out}")
                # D2.2 — return the structured result; is_error lets the agent recover
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(out), "is_error": is_err})
            messages.append({"role": "user", "content": results})      # <- append & loop
            continue

        print(f"   (unhandled stop_reason {resp.stop_reason})")
        return
    print("   hit MAX_TURNS safety cap")


if __name__ == "__main__":
    # NOTE — teaching simplification (not the trust model of a real system):
    # these strings ARE real Messages API user turns, but the customer *self-asserting* their
    # name/ID ("I'm John Smith, customer C001") stands in for real identity verification. A
    # production agent gets identity from an authenticated session, never from chat text; here
    # get_customer doubles as look-up + "verify" so the D1.4 prereq-gate fits in one file.
    # The gate and the lesson are real — only the "a typed name counts as verified" part is the shortcut.

    # Single-issue: should verify (get_customer) then lookup/refund.
    run("Hi, I'm Maria Garcia. Order 12345 arrived damaged, please refund it.")

    # Over-threshold: gate should block the refund and force escalation (Q1).
    run("This is John Smith, customer C001. Refund my $900 order 67890, it never arrived.")

    # Multi-concern (D1.4 decomposition) + ambiguous identity (D5.2 multi-match on 'John Smith').
    run("I'm John Smith. Two things: where is order 67890, and I want a refund on it.")
