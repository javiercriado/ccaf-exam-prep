"""examkit — the runner behind `practice_exam_A.ipynb`.

Stdlib only, no external dependencies. Questions and the answer key are read from the
notebook itself (the hidden `<!--ANSWER ... -->` blocks), so this file duplicates no
content: edit a question and the grader follows automatically.

Usage from the notebook:

    import examkit as ex
    ex.start()                 # start (or resume) the clock
    ex.answer(Q1="B")          # one cell per question
    ex.answer(Q4="A, C")       # Select-2: "A, C" / "A,C" / "AC" all work
    ex.clock()                 # check the time whenever you want
    ex.remaining()             # which questions are still blank
    ex.grade()                 # score, breakdowns, and why you missed each one

Attempt state lives in `ccaf-prep/personal/` (git-ignored), so it survives a kernel
restart and never reaches the repo.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "practice_exam_A.ipynb"
PERSONAL = HERE.parent / "personal"
STATE = PERSONAL / "practice_exam_A_attempt.json"

MIN_PER_QUESTION = 2.0  # real exam pace: 120 min / 60 questions


# ---------------------------------------------------------------------------- parsing


def _answer_block(text: str):
    """Pull (correct, tag, why) out of a question's <!--ANSWER ...--> comment."""
    m = re.search(r"<!--\s*ANSWER(.*?)-->", text, re.S)
    if not m:
        return None
    body = m.group(1)
    correct = re.search(r"^\s*Correct:\s*(.+)$", body, re.M)
    tag = re.search(r"^\s*Tag:\s*(.+)$", body, re.M)
    why = re.search(r"^\s*Why:\s*(.*?)(?=\n\s*\w+:|\Z)", body, re.M | re.S)
    return (
        _normalize(correct.group(1)) if correct else set(),
        tag.group(1).strip() if tag else "",
        " ".join(why.group(1).split()) if why else "",
    )


def load_questions() -> dict[int, dict]:
    """Parse the notebook into {number: question}. Cached by file mtime."""
    mtime = NOTEBOOK.stat().st_mtime
    if getattr(load_questions, "_cache_mtime", None) == mtime:
        return load_questions._cache
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    questions: dict[int, dict] = {}
    scenario = "?"
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        # the scenario heading may sit in its own cell (one question per cell) or in the
        # same cell as its questions — remember the most recent heading either way
        head = re.search(r"^##\s+(Scenario\s+\d[^\n]*)", src, re.M)
        if head:
            scenario = head.group(1).strip()
        # each block starts at **Qn.** and ends where the next one starts
        for block in re.split(r"(?=^\*\*Q\d+\.\*\*)", src, flags=re.M):
            qm = re.match(r"\*\*Q(\d+)\.\*\*\s*(.*?)(?=\n\s*\n|\Z)", block, re.S)
            if not qm:
                continue
            n = int(qm.group(1))
            sel = re.search(r"\(Select\s+(\d)\.?\)", block)
            # options: tolerates both "A. text" and the list form "- **A.** text"
            options = dict(
                re.findall(
                    r"^(?:[-*]\s+)?\*{0,2}([A-E])[.)]\*{0,2}\s+(.+?)\s*$",
                    block.split("<!--")[0],
                    re.M,
                )
            )
            key = _answer_block(block)
            questions[n] = {
                "n": n,
                "scenario": scenario,
                "stem": " ".join(qm.group(2).split()),
                "options": options,
                "select": int(sel.group(1)) if sel else 1,
                "correct": key[0] if key else set(),
                "tag": key[1] if key else "",
                "why": key[2] if key else "",
            }
    load_questions._cache_mtime = mtime
    load_questions._cache = dict(sorted(questions.items()))
    return load_questions._cache


def _normalize(response: str) -> set[str]:
    """'B' | 'B,D' | 'B, D' | 'BD' | 'b d'  ->  {'B','D'}"""
    return {c.upper() for c in re.findall(r"[A-Ea-e]", str(response))}


# ------------------------------------------------------------------------------ state


def _read_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"started": None, "finished": None, "answers": {}}


def _write_state(state: dict) -> None:
    PERSONAL.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _limit_min() -> float:
    return MIN_PER_QUESTION * len(load_questions())


def _elapsed(state: dict):
    """Return (elapsed_seconds, seconds_left)."""
    if not state.get("started"):
        return 0.0, _limit_min() * 60
    end = state.get("finished") or time.time()
    elapsed = end - state["started"]
    return elapsed, _limit_min() * 60 - elapsed


def _hms(seconds: float) -> str:
    """Seconds -> 'MM:SS', or 'H:MM:SS' past the hour."""
    seconds = int(abs(seconds))
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# -------------------------------------------------------------------------------- API


def start(restart: bool = False) -> None:
    """Start the clock. Pass restart=True to discard the previous attempt."""
    state = _read_state()
    if restart or not state.get("started"):
        state = {"started": time.time(), "finished": None, "answers": {}}
        _write_state(state)
        n = len(load_questions())
        print(f"⏱  Clock started — {n} questions · limit {_limit_min():.0f} min "
              f"({MIN_PER_QUESTION:.0f} min/question, the real exam's pace)")
        print("   Every question has its own answer cell below it: type the letter")
        print("   between the quotes and run it.  \"B\"  ·  \"B, D\"  ·  \"BD\"  all work.")
    else:
        elapsed, _ = _elapsed(state)
        print(f"⏱  Resuming attempt in progress — {len(state['answers'])} answered · "
              f"{_hms(elapsed)} elapsed")
        print("   (use `start(restart=True)` to wipe it and begin from scratch)")


def clock() -> None:
    """Show the clock and your pace without touching any answers."""
    state = _read_state()
    if not state.get("started"):
        print("The clock hasn't started. Run `start()`.")
        return
    questions = load_questions()
    elapsed, left = _elapsed(state)
    done = len(state["answers"])
    filled = int(20 * done / len(questions))
    print(f"⏱  elapsed {_hms(elapsed)}   |   "
          f"{'left ' + _hms(left) if left >= 0 else 'OVER by ' + _hms(left)}")
    print(f"   [{'█' * filled}{'·' * (20 - filled)}] {done}/{len(questions)} answered")
    if done:
        pace = elapsed / 60 / done
        verdict = "on track" if pace <= MIN_PER_QUESTION else "too slow — speed up"
        print(f"   pace {pace:.1f} min/question (target ≤ {MIN_PER_QUESTION:.1f}) — {verdict}")
        print(f"   projected over all {len(questions)}: {pace * len(questions):.0f} min "
              f"of {_limit_min():.0f}")


def answer(**responses: str) -> None:
    """Record answers: answer(Q1="B") or answer(Q4="A, C").

    Accepts one or more letters, with or without commas and spaces. Never tells you
    whether you were right — that is what `grade()` is for.
    """
    state = _read_state()
    if not state.get("started"):
        print("⚠️  The clock hasn't started; run `start()` first.\n")
        state["started"] = time.time()
    state["finished"] = None  # still working: un-freeze a clock a stray grade() stopped
    questions = load_questions()
    warnings = []
    for key, value in responses.items():
        m = re.fullmatch(r"[Qq]?(\d+)", key)
        if not m:
            warnings.append(f"· `{key}` doesn't look like a question (use Q1, Q2, …)")
            continue
        n = int(m.group(1))
        if n not in questions:
            warnings.append(f"· Q{n} is not in this form")
            continue
        letters = _normalize(value)
        q = questions[n]
        valid = set(q["options"]) or set("ABCD")
        if not letters:
            warnings.append(f"· Q{n}: no letter found in {value!r}")
            continue
        if letters - valid:
            warnings.append(f"· Q{n}: {', '.join(sorted(letters - valid))} is not an option "
                            f"(valid: {', '.join(sorted(valid))})")
        if len(letters) != q["select"]:
            warnings.append(f"· Q{n}: you marked {len(letters)} but it's Select {q['select']} "
                            f"— no partial credit, take another look")
        state["answers"][str(n)] = "".join(sorted(letters))
    _write_state(state)

    done = len(state["answers"])
    elapsed, _ = _elapsed(state)
    print(f"✔ saved {len(responses)} · total {done}/{len(questions)} · {_hms(elapsed)} elapsed")
    if done:
        pace = elapsed / 60 / done
        print(f"  pace {pace:.1f} min/question (target ≤ {MIN_PER_QUESTION:.1f}) — "
              f"{'OK' if pace <= MIN_PER_QUESTION else 'SLOW, speed up'}")
    for w in warnings:
        print("  ⚠️ " + w)


def remaining() -> None:
    """List the unanswered questions, grouped by scenario."""
    state = _read_state()
    questions = load_questions()
    blank = [n for n in questions if str(n) not in state["answers"]]
    if not blank:
        print("✅ Nothing left. Run `grade()`.")
        return
    print(f"{len(blank)} of {len(questions)} still blank:")
    for scen in dict.fromkeys(questions[n]["scenario"] for n in blank):
        nums = [f"Q{n}" for n in blank if questions[n]["scenario"] == scen]
        print(f"  {scen}: {', '.join(nums)}")


# ------------------------------------------------------------------------------ grade


def grade(reveal: bool = True, save: bool = True) -> dict:
    """Score the attempt: totals, breakdowns by scenario/domain/type, and the rationale
    for every miss. Pass reveal=False for the score alone (e.g. before a re-attempt)."""
    state = _read_state()
    questions = load_questions()
    if not state.get("finished"):
        state["finished"] = time.time()
        _write_state(state)
    elapsed, left = _elapsed(state)

    rows = []
    for n, q in questions.items():
        given = _normalize(state["answers"].get(str(n), ""))
        # no partial credit: the sets have to match exactly
        rows.append({**q, "given": given, "ok": bool(given) and given == q["correct"]})

    hits = sum(r["ok"] for r in rows)
    total = len(rows)
    blank = sum(1 for r in rows if not r["given"])
    pct = 100 * hits / total if total else 0

    out = []
    P = out.append
    P("=" * 72)
    P(f"  PRACTICE EXAM A — RESULT:  {hits}/{total}  ({pct:.0f}%)")
    P("=" * 72)
    P(f"  time:  {_hms(elapsed)} of {_limit_min():.0f} min allowed"
      f"{'  ⚠️ over the limit' if left < 0 else ''}")
    if total:
        P(f"  pace:  {elapsed / 60 / total:.1f} min/question")
    if blank:
        P(f"  ⚠️ {blank} left blank (counted wrong; on the real exam always mark something — "
          f"there is no guessing penalty)")
    P(f"  rough equivalent over 60 questions: ~{round(pct / 100 * 60)}/60"
      f"   ·   your STUDY_PLAN target: ≥ 52/60")
    P("  (the real exam's 1000/720 scale is neither linear nor public — treat this as a")
    P("   thermometer, not a score prediction)")

    def breakdown(title, key):
        P("")
        P(f"  {title}")
        groups: dict[str, list] = {}
        for r in rows:
            groups.setdefault(key(r), []).append(r)
        for g in sorted(groups):
            gs = groups[g]
            a = sum(x["ok"] for x in gs)
            pc = 100 * a / len(gs)
            mark = "✓" if pc >= 80 else ("⚠️" if pc >= 60 else "✗")
            filled = int(12 * a / len(gs))
            P(f"    {mark} {g:<46} [{'█' * filled}{'·' * (12 - filled)}] "
              f"{a:>2}/{len(gs)}  {pc:>3.0f}%")

    breakdown("BY SCENARIO", lambda r: r["scenario"].replace("Scenario ", "S"))
    breakdown("BY DOMAIN", lambda r: (re.search(r"D\d", r["tag"]) or [None])[0] or "untagged")
    breakdown("BY QUESTION TYPE", lambda r: f"Select {r['select']}")

    misses = [r for r in rows if not r["ok"]]
    if reveal and misses:
        P("")
        P("=" * 72)
        P(f"  WHAT YOU MISSED ({len(misses)})")
        P("=" * 72)
        for r in misses:
            given = ", ".join(sorted(r["given"])) or "— blank —"
            P("")
            P(f"  Q{r['n']} · {r['scenario']}")
            P(f"     you: {given}      correct: {', '.join(sorted(r['correct']))}")
            P(f"     {r['tag']}")
            for line in _wrap(r["why"], 66):
                P(f"     {line}")
    elif reveal:
        P("")
        P("  🎉 Clean sweep.")

    P("")
    P("  Next: for every miss, find its Task Statement in ../MAPPING.md and name the")
    P("  distractor pattern that caught you (see ../DISTRACTOR_HEURISTIC.md).")

    report = "\n".join(out)
    print(report)

    if save:
        PERSONAL.mkdir(parents=True, exist_ok=True)
        dest = PERSONAL / f"practice_exam_A_result_{time.strftime('%Y-%m-%d_%H%M')}.md"
        dest.write_text(
            f"# Practice Exam A — attempt {time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"```\n{report}\n```\n\n## Answers given\n\n"
            + "\n".join(
                f"- Q{r['n']}: {''.join(sorted(r['given'])) or '—'} "
                f"{'✓' if r['ok'] else '✗ (correct: ' + ''.join(sorted(r['correct'])) + ')'}"
                for r in rows
            ),
            encoding="utf-8",
        )
        print(f"\n  📄 Saved to personal/{dest.name} (git-ignored)")

    return {"hits": hits, "total": total, "pct": pct, "rows": rows}


def _wrap(text: str, width: int) -> list[str]:
    line, out = "", []
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out
