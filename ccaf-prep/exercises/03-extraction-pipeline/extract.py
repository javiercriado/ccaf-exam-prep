"""
Exercise 3 — structured extraction pipeline (D4.3) with few-shot (D4.2),
validation-retry (D4.4), context trimming (D5.1) and field-level confidence
routing (D5.5). Forced tool_choice is the D2.3 piece.

Run:  cd ccaf-prep/exercises/03-extraction-pipeline && uv run python extract.py
Env:  ANTHROPIC_API_KEY (+ optional CLAUDE_MODEL) — copy ccaf-prep/.env.example
      to ccaf-prep/.env and add your key; it is loaded robustly below (the env
      is NOT assumed to be exported into the shell).

Toggles that drive the learning (defaults shown; flip ONE per study step, reset between):
  - FEW_SHOT       = True  -> flip False to watch judgment/confidence degrade on the
                             AMBIGUOUS input. MODEL-DEPENDENT: on this toy the wobble is
                             mild (observed aggregate 0.72-0.75 vs 0.77). D4.2.
  - DEMO_RETRY     = True  -> corrupts attempt 0's date so the D4.4 retry path fires every
                             run. DETERMINISTIC: flip False and attempt 0 already passes (no
                             retry). D4.4.
  - CONF_THRESHOLD = 0.70  -> a numeric knob, not a baseline boolean. DETERMINISTIC arithmetic:
                             raise it (0.99) and every field routes to human review; drop it
                             to 0.0 and even the 0.0-confidence account_id auto-accepts. D5.5.

Teaching simplification: the few-shot examples (FEW_SHOT_TURNS) are CANNED demonstrations and
MESSY_INPUT is one hardcoded toy support message — both stand in for a real labelled example set
and a real document stream. The MECHANISMS (forced tool_use, validate-retry, confidence routing)
are real; the data is a fixture so one cheap call teaches each concept.

What each printed block proves (read alongside README.md):
  - "FORCED tool_use" block  -> D4.3 structured output is SYNTACTICALLY guaranteed.
  - "VALIDATION failed ... retrying" -> D4.4 retry-with-error-feedback.
  - "CONFIDENCE routing"     -> D5.5 per-field routing; an aggregate score hides
                                a weak field.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from anthropic import Anthropic

# ---- Portable env load (no machine paths; env is NOT assumed exported) -----------
_env = find_dotenv(filename=".env", usecwd=True)
if not _env:  # fall back to the sibling course project's .env, if present
    for _p in Path(__file__).resolve().parents:
        if (_p / "claude-with-anthropic-api" / ".env").exists():
            _env = str(_p / "claude-with-anthropic-api" / ".env"); break
load_dotenv(_env)
MODEL = os.environ.get("CLAUDE_MODEL") or "claude-haiku-4-5"   # cheap default; set CLAUDE_MODEL=claude-sonnet-4-6 in .env for harder tasks

# ---- toggle: flip False to study the D4.2 anti-pattern (instructions ALONE) -----
FEW_SHOT = True

MAX_RETRIES = 1   # one validation-retry is enough to make the D4.4 point


# ============================================================================
# D4.3 — the extraction TOOL. A JSON input_schema makes tool_use the most
# reliable structured-output mechanism: the model CANNOT return malformed JSON
# (no parse errors). But syntactic validity != semantic correctness — a value
# can land in the wrong field, or "amount" can disagree with the source. That
# residual risk is exactly what the D4.4 validator and D5.5 confidence catch.
#
# `account_id` is NULLABLE on purpose (D4.3 skill): when the source omits it the
# model should emit null instead of FABRICATING a value to satisfy a required
# field. Required fields would pressure the model to hallucinate.
# ============================================================================
EXTRACT_TOOL = {
    "name": "record_refund_request",                                # <- D4.3
    "description": "Record the structured fields of a customer refund request.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":   {"type": "string", "description": "Customer full name."},
            "amount": {"type": "number", "description": "Refund amount in USD."},
            "date":   {"type": "string",
                       "description": "Purchase date, STRICT ISO format YYYY-MM-DD."},
            # nullable: source may not contain it -> null, never invented.   <- D4.3
            "account_id": {"type": ["string", "null"],
                           "description": "Account id like ACC-1234, or null if absent."},
            # also nullable: the refund reason, when the message states one.
            "reason": {"type": ["string", "null"],
                       "description": "Short refund reason (e.g. 'item arrived damaged'), or null if absent."},
            # D5.5 — per-field confidence 0.0-1.0 so we can ROUTE, not just trust.
            "confidence": {
                "type": "object",
                "description": "Model's 0.0-1.0 confidence for EACH extracted field.",
                "properties": {
                    "name":       {"type": "number"},
                    "amount":     {"type": "number"},
                    "date":       {"type": "number"},
                    "account_id": {"type": "number"},
                    "reason":     {"type": "number"},
                },
                "required": ["name", "amount", "date", "account_id", "reason"],
            },
        },
        # account_id deliberately NOT required (it is nullable).            <- D4.3
        "required": ["name", "amount", "date", "confidence"],
    },
}

# name -> function dispatch registry (mirrors EX1's DISPATCH).
DISPATCH = {"record_refund_request": lambda **kw: kw}


# ---- D4.2 few-shot block ----------------------------------------------------
# Most effective for: consistent FORMAT + AMBIGUOUS-case judgment + EXTRACTION.
# Each example shows the messy phrasing -> the disciplined call, including the
# judgment calls we care about: spelled-out money -> number, missing id -> null,
# and a LOW confidence when the source is vague. Instructions alone (FEW_SHOT
# =False) leave these to chance — that is the distractor for D4.2.
FEW_SHOT_TURNS = [
    {"role": "user", "content": "hey it's Dana Lopez, want my money back, the item never arrived, paid ninety bucks back on the third of march 2024, acct ACC-0007"},
    {"role": "assistant", "content": [{
        "type": "tool_use", "id": "fs1", "name": "record_refund_request",
        "input": {"name": "Dana Lopez", "amount": 90, "date": "2024-03-03",
                  "account_id": "ACC-0007", "reason": "item never arrived",
                  "confidence": {"name": 0.99, "amount": 0.97, "date": 0.95,
                                 "account_id": 0.99, "reason": 0.96}},
    }]},
    {"role": "user", "content": [{
        "type": "tool_result", "tool_use_id": "fs1", "content": "recorded"}]},
    # ambiguous example: spelled-out money + NO account id -> null + low conf.
    {"role": "user", "content": "Sam here. refund the order, was like a hundred-ish, sometime last april"},
    {"role": "assistant", "content": [{
        "type": "tool_use", "id": "fs2", "name": "record_refund_request",
        "input": {"name": "Sam", "amount": 100, "date": "2024-04-01",
                  "account_id": None, "reason": None,
                  "confidence": {"name": 0.6, "amount": 0.4, "date": 0.3,
                                 "account_id": 0.0, "reason": 0.0}},
    }]},
    {"role": "user", "content": [{
        "type": "tool_result", "tool_use_id": "fs2", "content": "recorded"}]},
]

SYSTEM = (
    "You extract refund-request fields by calling record_refund_request. "
    "Normalize spelled-out money to a number and dates to STRICT YYYY-MM-DD. "
    "Capture the refund reason when the message states one. "
    "If a field is absent from the message, set it to null — never invent it. "
    "Give an honest per-field confidence: low when the source is vague."
)

# Demo toggle: a capable model usually extracts a clean ISO date on attempt 0,
# so the D4.4 retry path would never fire and you'd never SEE the feedback loop.
# With this on, we corrupt ONLY the first attempt's date into verbal form ("Mar
# 5 2024") so it FAILS the strict validator — forcing one real retry where the
# specific error is appended as feedback (is_error) and the model self-corrects.
# This is faithful to D4.4: the info IS present, just mis-formatted (retryable).
# Flip False to see attempt 0 already pass when the model nails the format.
DEMO_RETRY = True

# Tiny toy input — one short, MESSY support message. Note: amount is spelled out,
# the date is sloppy, and there is NO account id (so account_id must be null).
MESSY_INPUT = (
    "ugh hi, Maria Garcia here. need a refund — it was two-fifty (250-ish), "
    "bought it on march 5 2024. order arrived smashed."
)

# Confidence threshold for D5.5 auto-accept vs human-review routing.
CONF_THRESHOLD = 0.70


# ---- D4.4 validator ---------------------------------------------------------
def validate(extracted):
    """Return a list of human-readable validation errors (semantic / format).
    These are NOT JSON syntax errors — tool_use already eliminated those (D4.3).
    Retry can fix these because the info IS present, just mis-formatted. If the
    info were simply ABSENT from the source, retry would be useless (D4.4)."""
    errors = []
    date = extracted.get("date", "")
    # strict YYYY-MM-DD check (format error, present-but-wrong -> retryable).
    parts = date.split("-")
    if not (len(parts) == 3 and parts[0].isdigit() and len(parts[0]) == 4
            and parts[1].isdigit() and len(parts[1]) == 2
            and parts[2].isdigit() and len(parts[2]) == 2):
        errors.append(f"'date' must be strict YYYY-MM-DD, got {date!r}.")
    if not isinstance(extracted.get("amount"), (int, float)):
        errors.append("'amount' must be a number (normalize spelled-out money).")
    return errors


def force_extract(client, source_text):
    """One forced extraction call, with a D4.4 validation-retry loop.

    D2.3 tool_choice modes:
      - {"type": "auto"} : model MAY return text instead of calling a tool.
      - {"type": "any"}  : model MUST call SOME tool (good when several schemas).
      - {"type": "tool", "name": ...} : FORCE this specific tool (used here, so
        the response is guaranteed to be a structured record_refund_request).
    """
    messages = list(FEW_SHOT_TURNS) if FEW_SHOT else []
    messages.append({"role": "user", "content": f"Extract from this message:\n{source_text}"})

    for attempt in range(MAX_RETRIES + 1):
        resp = client.messages.create(
            model=MODEL, max_tokens=300, system=SYSTEM, tools=[EXTRACT_TOOL],
            tool_choice={"type": "tool", "name": "record_refund_request"},  # <- D2.3 forced
            messages=messages,
        )
        # D4.3 — because we FORCED the tool, content[0] is a tool_use block and
        # its .input is valid JSON. No try/except json.loads is needed: tool_use
        # guarantees SYNTACTIC validity. (Semantic validity is NOT guaranteed.)
        tool_block = next(b for b in resp.content if b.type == "tool_use")
        extracted = DISPATCH[tool_block.name](**tool_block.input)
        extracted.setdefault("account_id", None)   # nullable: absent key == null (D4.3)
        extracted.setdefault("reason", None)        # nullable too
        if DEMO_RETRY and attempt == 0 and isinstance(extracted.get("date"), str):
            # corrupt ONLY attempt 0's date into a verbal form to force one retry
            extracted["date"] = "Mar 5 2024"   # present-but-mis-formatted (retryable)
        print(f"  [attempt {attempt}] FORCED tool_use -> stop_reason="
              f"{resp.stop_reason}  (JSON syntactically valid by construction)")  # <- D4.3

        errors = validate(extracted)                                    # <- D4.4
        if not errors:
            return extracted, attempt

        print(f"  VALIDATION failed: {errors} -> retrying with feedback")  # <- D4.4
        # Append the assistant turn, a tool_result flagged is_error, and the
        # specific errors so the model can self-correct (retry-with-feedback).
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": [{
            "type": "tool_result", "tool_use_id": tool_block.id,
            "is_error": True,                                           # <- EX1-style is_error
            "content": "Validation errors, FIX and re-call: " + "; ".join(errors),
        }]})
        # NOTE: this retry helps ONLY because the date/amount ARE in the source,
        # just mis-formatted. If a field were ABSENT, no amount of retrying would
        # conjure it — the right move there is null + human review, not a loop.

    print("  retries exhausted; returning last (still-invalid) extraction")
    return extracted, MAX_RETRIES


def route_by_confidence(extracted):
    """D5.5 — route each field by its own confidence. The point: an AGGREGATE
    'mean confidence' can look high while ONE field is weak. We must inspect
    fields, not the average, before auto-accepting an extraction."""
    conf = extracted["confidence"]
    auto, flagged = [], []
    for field in ("name", "amount", "date", "account_id", "reason"):
        (auto if conf[field] >= CONF_THRESHOLD else flagged).append(field)
    aggregate = sum(conf.values()) / len(conf)
    print(f"  CONFIDENCE routing (threshold {CONF_THRESHOLD}):")
    print(f"    aggregate(mean) = {aggregate:.2f}  <- can HIDE a weak field (D5.5)")
    print(f"    AUTO-ACCEPT : {auto}")
    print(f"    HUMAN REVIEW: {[(f, conf[f]) for f in flagged]}")
    return auto, flagged


def trim_for_downstream(extracted):
    """D5.1 — trim verbose context before passing forward. We keep only the
    structured fields the next stage needs and DROP the raw confidence blob (and
    we would drop any raw source text). Verbose blobs accumulate tokens out of
    proportion to their relevance; the structured fields are what matter."""
    trimmed = {k: extracted.get(k) for k in ("name", "amount", "date", "account_id", "reason")}
    print(f"  TRIMMED for downstream (dropped raw 'confidence' blob): {trimmed}")  # <- D5.1
    return trimmed


def run():
    client = Anthropic()
    print(f"\n{'='*70}\nEX3 extraction pipeline   [FEW_SHOT={FEW_SHOT}  MODEL={MODEL}]")
    print(f"INPUT: {MESSY_INPUT}\n{'='*70}")

    extracted, attempts = force_extract(client, MESSY_INPUT)
    print(f"\nEXTRACTED (after {attempts} retr{'y' if attempts == 1 else 'ies'}):")
    print("  " + json.dumps({k: v for k, v in extracted.items() if k != 'confidence'}))
    print(f"  account_id is {'null (correctly NOT fabricated)' if extracted.get('account_id') is None else extracted['account_id']}")  # <- D4.3 nullable

    print()
    route_by_confidence(extracted)                                      # <- D5.5
    print()
    trim_for_downstream(extracted)                                      # <- D5.1


if __name__ == "__main__":
    run()
