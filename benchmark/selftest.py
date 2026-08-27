#!/usr/bin/env python3
"""Offline self-test for the benchmark harness.

Runs with no API key and no network, so CI can prove two things on every
commit: each checker separates compliant from violating text, and every pair in
pairs.jsonl is well formed and points at a checker that exists.

    python3 benchmark/selftest.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checkers  # noqa: E402

PAIRS_PATH = Path(__file__).parent / "pairs.jsonl"

# checker -> (params, [text that complies], [text that violates])
CASES: dict[str, tuple[dict, list[str], list[str]]] = {
    "no_markdown": (
        {},
        ["An index is a sorted structure the planner consults before a scan.",
         "Two paragraphs, plain.\n\nStill plain, still prose."],
        ["# Heading\n\nbody", "- one\n- two", "Use **bold** here", "```py\nx=1\n```",
         "| a | b |\n| - | - |"],
    ),
    "no_bullets": (
        {},
        ["First the author reads. Second the reviewer reads.",
         "A dash - used mid-sentence stays fine."],
        ["- one\n- two", "1. first\n2. second", "* star", "  • bullet item"],
    ),
    "no_headings": (
        {},
        ["Generating a key comes first. Installing it comes second.",
         "A # inside a sentence like issue #12 stays fine."],
        ["# Setup", "### Step three\ntext", "  ## Indented heading"],
    ),
    "no_bold": (
        {},
        ["Consistency, availability, partition tolerance.", "2 * 3 * 4 is arithmetic."],
        ["Pick **two** of three", "__strong__ text"],
    ),
    "no_code_fence": (
        {},
        ["du -ah . | sort -rh | head -10", "Inline `backticks` are fine."],
        ["```\ndu -ah\n```", "~~~sh\nls\n~~~"],
    ),
    "no_emoji": (
        {},
        ["Fixed a crash on startup.", "Welcome aboard."],
        ["Fixed a crash \U0001f680", "Welcome ☀️"],
    ),
    "max_sentences": (
        {"n": 2},
        ["One sentence. Two sentences.", "Just one sentence here.",
         "Costs approx. 3.5 units per request."],
        ["One. Two. Three.", "A. B. C. D."],
    ),
    "max_words": (
        {"n": 5},
        ["one two three four five", "three words only"],
        ["one two three four five six"],
    ),
    "max_chars": (
        {"n": 20},
        ["short enough", "  padded  "],
        ["this string is definitely longer than twenty characters"],
    ),
    "single_paragraph": (
        {},
        ["One flowing paragraph\nwith a soft wrap."],
        ["First para.\n\nSecond para."],
    ),
    "no_questions": (
        {},
        ["PostgreSQL suits this app.", "The code `is_ready?` stays inside a fence."],
        ["Which one do you prefer?"],
    ),
    "no_first_person": (
        {},
        ["The build failed because the file was absent.", "Imports resolve from the venv."],
        ["I think the file is missing.", "Let us check our config.", "That is my guess."],
    ),
    "no_preamble": (
        {},
        ["443.", "git reset --soft HEAD~1 keeps the changes staged."],
        ["Sure! HTTPS uses 443.", "Here's the command you want.",
         "Great question — the answer is 443."],
    ),
    "no_apology": (
        {},
        ["The fifth Fibonacci number is 5."],
        ["Sorry, the correct value is 5.", "I apologise for the error."],
    ),
    "no_trailing_offer": (
        {},
        ["A webhook is an outbound HTTP call the server makes on an event."],
        ["A webhook is a callback. Let me know if you have questions.",
         "That is the difference. Hope this helps!"],
    ),
    "json_object": (
        {"keys": ["name", "role"]},
        ['{"name": "Priya Raman", "role": "staff engineer"}'],
        ['```json\n{"name": "a", "role": "b"}\n```',
         'Here you go: {"name": "a", "role": "b"}',
         '{"name": "a"}',
         '["name", "role"]'],
    ),
    "lowercase_only": (
        {},
        ["fix typo in readme"],
        ["Fix typo in README"],
    ),
    "forbidden_words": (
        {"words": ["delve", "leverage", "robust", "seamless"]},
        ["The cache now serves reads directly, which cuts tail latency."],
        ["We leverage a robust cache.", "Let us delve into it.", "A Seamless upgrade."],
    ),
    "no_bare_url": (
        {},
        ["Work through the exercises on Regex Crossword."],
        ["See https://regexcrossword.com for practice."],
    ),
}


def test_checkers() -> list[str]:
    failures: list[str] = []
    untested = sorted(set(checkers.REGISTRY) - set(CASES))
    if untested:
        failures.append(f"checkers with no fixtures: {untested}")

    for name, (params, good, bad) in CASES.items():
        if name not in checkers.REGISTRY:
            failures.append(f"{name}: fixture references a checker that does not exist")
            continue
        for text in good:
            if not checkers.run(name, text, params):
                failures.append(f"{name}: expected compliant, scored violating: {text!r}")
        for text in bad:
            if checkers.run(name, text, params):
                failures.append(f"{name}: expected violating, scored compliant: {text!r}")
    return failures


def test_pairs() -> list[str]:
    failures: list[str] = []
    if not PAIRS_PATH.exists():
        return [f"{PAIRS_PATH} is absent; run python3 benchmark/build_pairs.py"]

    seen: set[str] = set()
    required = {"id", "checker", "params", "alignment", "task", "negative", "positive"}
    count = 0
    with PAIRS_PATH.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            count += 1
            try:
                pair = json.loads(line)
            except ValueError as exc:
                failures.append(f"pairs.jsonl:{lineno}: expected valid JSON ({exc})")
                continue
            missing = required - set(pair)
            if missing:
                failures.append(f"pairs.jsonl:{lineno}: missing fields {sorted(missing)}")
                continue
            if pair["id"] in seen:
                failures.append(f"pairs.jsonl:{lineno}: duplicate id {pair['id']}")
            seen.add(pair["id"])
            if pair["checker"] not in checkers.REGISTRY:
                failures.append(f"{pair['id']}: unknown checker {pair['checker']!r}")
            if pair["alignment"] not in {"with-default", "against-default"}:
                failures.append(f"{pair['id']}: unknown alignment {pair['alignment']!r}")
            if pair["negative"].strip() == pair["positive"].strip():
                failures.append(f"{pair['id']}: both arms carry identical text")
            for arm in ("negative", "positive"):
                if len(pair[arm].split()) < 3:
                    failures.append(f"{pair['id']}: {arm} instruction looks too short to be real")

    if count < 30:
        failures.append(f"pairs.jsonl holds {count} pairs; the harness targets 30 or more")
    return failures


def main() -> int:
    failures = test_checkers() + test_pairs()
    fixtures = sum(len(g) + len(b) for _, g, b in CASES.values())
    if failures:
        print(f"FAIL — {len(failures)} problem(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        f"ok — {len(checkers.REGISTRY)} checkers pass {fixtures} fixtures; "
        f"pairs.jsonl is well formed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
