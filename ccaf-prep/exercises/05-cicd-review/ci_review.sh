#!/usr/bin/env bash
# Exercise 5 — headless Claude Code code review for CI/CD (D3.6, sample Q10).
#
# This is the SAMPLE pattern a CI step runs; it doesn't need to execute locally.
# The point: a CI gate is HEADLESS (`-p`/`--print`), SYNCHRONOUS, and emits MACHINE-PARSEABLE
# JSON constrained to a schema so the pipeline can decide pass/fail.
set -euo pipefail

BASE="${1:-origin/main}"

# D3.6 — the real flags (the distractors invent CLAUDE_HEADLESS / --batch; those don't exist):
#   -p / --print            run headless, no interactive UI (Q10)
#   --output-format json    structured envelope CI can parse
#   --json-schema FILE       constrain the result to findings.schema.json
#
# CLAUDE.md in the repo provides review CONTEXT automatically. Running this as a SEPARATE
# `claude -p` invocation gives an INDEPENDENT reviewer (D4.6) — it never sees the author's
# generation conversation, so it can't rationalize the author's bugs.

git diff "${BASE}...HEAD" > /tmp/pr.diff

claude -p "You are an INDEPENDENT reviewer. Review the diff in /tmp/pr.diff against ONLY these
categories: security, correctness, resource-leak, cross-file. Report nothing outside them
(vague nitpicks erode trust). Emit findings per the provided schema." \
  --output-format json \
  --json-schema findings.schema.json \
  > review.json

# CI gates on the structured output (e.g. fail the build on any high-severity finding):
HIGH=$(jq '[.findings[] | select(.severity=="high")] | length' review.json)
echo "high-severity findings: ${HIGH}"
if [ "${HIGH}" -gt 0 ]; then
  echo "BLOCKING: high-severity issues found"; exit 1
fi

# NOTE (D4.5): this blocking pre-merge gate is SYNCHRONOUS on purpose. Do NOT move it to the
# Batch API — Batches are async (≤24h, no SLA, 50% off) and suit NIGHTLY/offline REPORTS, not
# a gate that must return before the merge button unlocks (sample Q11).
