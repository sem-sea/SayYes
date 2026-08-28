#!/usr/bin/env python3
"""Emit a blinded review sheet for the benchmark pairs.

The threat this addresses: both arms of a pair are supposed to mean the same
thing, and the author of the pairs believes positive phrasing wins. If a
positive arm is also clearer, more specific, or simply easier to satisfy, the
benchmark measures that instead of phrasing, and produces a convincing result
about nothing.

A reviewer catches this only while blind to which arm is which. This script
shuffles the pair order, assigns each pair's two instructions to X and Y at
random, and prints them with no mention of positive, negative, or yesand. The
assignment is reproducible from the seed, so --unblind recovers it after the
review is recorded.

    python3 scripts/make_pair_review.py --seed 41 > review-sheet.md
    # hand review-sheet.md to a reviewer who has not read the repository
    python3 scripts/make_pair_review.py --seed 41 --unblind
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "benchmark" / "pairs.jsonl"

HEADER = """# Instruction pair review

Below are {n} numbered items. Each holds a task and two candidate instructions,
X and Y, that were written to mean the same thing.

For each item, answer two questions.

**Q1. Do X and Y ask for the same thing?**  `same` / `different` / `unsure`

**Q2. Is one of them easier to satisfy, more specific, or clearer than the
other, setting aside how each is worded?**  `X` / `Y` / `neither`

Q2 is the one that matters. Two instructions can mean the same thing while one
of them is still a lower bar to clear, and an item where a reviewer keeps
picking the same letter for Q2 is measuring that difference rather than the one
intended.

Answer from the text alone. Skip anything you would have to guess at, and mark
it `unsure` rather than choosing.

Record answers as `item, Q1, Q2`, for example `7, same, neither`.

---
"""

ITEM = """### Item {i}

**Task given to the model**

> {task}

**Instruction X**

> {x}

**Instruction Y**

> {y}

Q1 (same / different / unsure): ______   Q2 (X / Y / neither): ______

"""


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def assign(pairs: list[dict], seed: int) -> list[tuple[int, dict, str, str]]:
    """Return (item_number, pair, x_arm, y_arm) with order and labels shuffled.

    The X/Y assignment is balanced rather than drawn per pair: half the items
    carry the positive arm as X, half as Y. An independent coin lands lopsided
    often enough that a reviewer answering Q2 could pick up a base rate, and a
    lopsided split also makes the tally harder to read afterwards.
    """
    rng = random.Random(seed)
    order = list(pairs)
    rng.shuffle(order)

    n = len(order)
    slots = ["positive"] * (n // 2) + ["negative"] * (n - n // 2)
    rng.shuffle(slots)

    rows = []
    for i, (pair, x_arm) in enumerate(zip(order, slots), 1):
        y_arm = "negative" if x_arm == "positive" else "positive"
        rows.append((i, pair, x_arm, y_arm))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=41)
    ap.add_argument("--pairs", type=Path, default=PAIRS)
    ap.add_argument("--unblind", action="store_true",
                    help="print the item-to-pair mapping instead of the sheet")
    args = ap.parse_args(argv)

    pairs = load(args.pairs)
    rows = assign(pairs, args.seed)

    if args.unblind:
        print(f"seed {args.seed}, {len(rows)} items\n")
        print(f"{'item':>4}  {'pair':<8} {'X is':<9} {'Y is':<9} alignment")
        for i, pair, x_arm, y_arm in rows:
            print(f"{i:>4}  {pair['id']:<8} {x_arm:<9} {y_arm:<9} {pair['alignment']}")
        flipped = sum(1 for _, _, x, _ in rows if x == "positive")
        print(f"\nX carries the positive arm in {flipped} of {len(rows)} items.")
        return 0

    print(HEADER.format(n=len(rows)))
    for i, pair, x_arm, y_arm in rows:
        print(ITEM.format(i=i, task=pair["task"], x=pair[x_arm], y=pair[y_arm]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Writing into head/less closes the pipe early; that is a clean exit.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
