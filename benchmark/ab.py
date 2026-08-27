#!/usr/bin/env python3
"""A/B two phrasings of your own instruction on your own task.

The pairs in pairs.jsonl measure phrasing on a fixed test set. This measures it
on yours, which is the number that should decide whether you adopt yesand.

    # 1. Write the two phrasings you want to compare.
    echo "Do not use bullet points."      > a.txt
    echo "Write the answer as prose."     > b.txt
    echo "Explain how DNS resolution works." > task.txt

    # 2. Run them head to head.
    export ANTHROPIC_API_KEY=...
    python3 benchmark/ab.py --a a.txt --b b.txt --task task.txt \
        --checker no_bullets --repeat 10 \
        --provider anthropic --model claude-sonnet-5

Pick --checker from the list printed by --list-checkers, or pass --checker none
to skip scoring and read the outputs yourself.

Two cautions worth more than this script's output:

  * Provider-billed totals outrank any estimate printed here. When cost is the
    question, run the same task with and without your rewrite and compare your
    provider's usage page.
  * A difference whose interval spans zero is a difference you have yet to
    measure. Raise --repeat until the interval tightens, or treat it as no
    effect.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checkers  # noqa: E402
from report import wilson  # noqa: E402
from run import PROVIDERS, ProviderError, call_with_retry  # noqa: E402


def read_text(value: str) -> str:
    path = Path(value)
    return path.read_text(encoding="utf-8").strip() if path.exists() else value.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--list-checkers", action="store_true", help="print checker names and exit")
    ap.add_argument("--a", help="file or literal: phrasing A (typically the original)")
    ap.add_argument("--b", help="file or literal: phrasing B (typically the rewrite)")
    ap.add_argument("--task", help="file or literal: the user message sent under both")
    ap.add_argument("--checker", default="none", help="checker name, or none to skip scoring")
    ap.add_argument("--params", default="{}", help="JSON params for the checker, e.g. '{\"n\": 3}'")
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default="anthropic")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--repeat", type=int, default=10, help="completions per arm (default 10)")
    ap.add_argument("--temperature", type=float, default=1.0,
                    help="default 1.0: your real traffic is rarely at 0")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--max-tokens-field", default=None,
                    choices=["max_tokens", "max_completion_tokens"],
                    help="override the OpenAI-compatible token-cap field name")
    ap.add_argument("--save", type=Path, default=None, help="write raw rows to this JSONL path")
    args = ap.parse_args(argv)

    if args.list_checkers:
        for name in sorted(checkers.REGISTRY):
            print(name)
        return 0

    missing = [f"--{n}" for n in ("a", "b", "task") if getattr(args, n) is None]
    if missing:
        ap.error(f"provide {', '.join(missing)} (or use --list-checkers)")

    arm_a, arm_b, task = read_text(args.a), read_text(args.b), read_text(args.task)
    params = json.loads(args.params)
    scoring = args.checker != "none"
    if scoring and args.checker not in checkers.REGISTRY:
        ap.error(f"unknown checker {args.checker!r}; see --list-checkers")

    call = PROVIDERS[args.provider]
    results: dict[str, list[bool]] = {"A": [], "B": []}
    rows: list[dict] = []
    total_out_tokens = {"A": 0, "B": 0}

    print(f"A: {arm_a[:70]}")
    print(f"B: {arm_b[:70]}")
    print(f"task: {task[:70]}")
    print(f"{args.repeat} completions per arm on {args.model} at temperature {args.temperature}\n")

    for rep in range(args.repeat):
        # Alternate which arm leads so ordering cannot favour either one.
        order = [("A", arm_a), ("B", arm_b)]
        if rep % 2:
            order.reverse()
        for label, instruction in order:
            try:
                text, usage = call_with_retry(
                    call, 4,
                    model=args.model, system=instruction, user=task,
                    max_tokens=args.max_tokens, temperature=args.temperature,
                    base_url=args.base_url, timeout=args.timeout,
                    max_tokens_field=args.max_tokens_field,
                )
            except ProviderError as exc:
                print(f"  ! {label} r{rep}: {exc}", file=sys.stderr)
                continue

            compliant = checkers.run(args.checker, text, params) if scoring else None
            if compliant is not None:
                results[label].append(compliant)
            total_out_tokens[label] += usage.get("output_tokens") or 0
            rows.append({
                "arm": label, "repeat_index": rep, "instruction": instruction,
                "task": task, "model": args.model, "temperature": args.temperature,
                "checker": args.checker if scoring else None,
                "output": text, "compliant": compliant, "usage": usage,
            })
            mark = "" if compliant is None else ("  ok" if compliant else "  VIOLATION")
            print(f"[r{rep}] {label}{mark}")

    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        with args.save.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"\nraw rows written to {args.save}")

    print()
    if scoring and results["A"] and results["B"]:
        a_point, a_lo, a_hi = wilson(sum(results["A"]), len(results["A"]))
        b_point, b_lo, b_hi = wilson(sum(results["B"]), len(results["B"]))
        print(f"A compliance: {a_point:.1f}% ({a_lo:.1f}-{a_hi:.1f})  n={len(results['A'])}")
        print(f"B compliance: {b_point:.1f}% ({b_lo:.1f}-{b_hi:.1f})  n={len(results['B'])}")
        print(f"difference:   {b_point - a_point:+.1f} pp (B minus A)")
        if a_lo <= b_point <= a_hi or b_lo <= a_point <= b_hi:
            print("\nThe intervals overlap, so this run leaves the two phrasings "
                  "indistinguishable.\nRaise --repeat, or read it as no effect on this task.")
    elif scoring:
        print("Too few scored completions to report a rate.")

    if any(total_out_tokens.values()):
        print(f"\noutput tokens — A: {total_out_tokens['A']}, B: {total_out_tokens['B']}")
        print("Compare your provider's usage page for the number that bills you.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
