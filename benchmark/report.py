#!/usr/bin/env python3
"""Aggregate benchmark result rows into a markdown table.

Reads every .jsonl file under benchmark/results/ and reports the compliance
rate for each arm, with a Wilson score interval so the reader can see how much
the sample actually supports. The paired difference comes with a bootstrap
interval over pairs, since repeats of the same pair are correlated.

    python3 benchmark/report.py                 # all results
    python3 benchmark/report.py --by-alignment  # split with/against default
    python3 benchmark/report.py --by-checker    # split by constraint type
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
Z = 1.959963985  # 95%


def wilson(successes: int, total: int, z: float = Z) -> tuple[float, float, float]:
    """Return (point, low, high) as percentages."""
    if total == 0:
        return (float("nan"),) * 3
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return p * 100, max(0.0, centre - half) * 100, min(1.0, centre + half) * 100


def bootstrap_diff(per_pair: dict[str, tuple[list[bool], list[bool]]],
                   iterations: int = 5000, seed: int = 20260827) -> tuple[float, float, float]:
    """Paired bootstrap over pair ids. Returns (point, low, high) in pp."""
    ids = [pid for pid, (neg, pos) in per_pair.items() if neg and pos]
    if not ids:
        return (float("nan"),) * 3

    def diff(sample: list[str]) -> float:
        neg_ok = neg_n = pos_ok = pos_n = 0
        for pid in sample:
            neg, pos = per_pair[pid]
            neg_ok += sum(neg); neg_n += len(neg)
            pos_ok += sum(pos); pos_n += len(pos)
        if not neg_n or not pos_n:
            return float("nan")
        return (pos_ok / pos_n - neg_ok / neg_n) * 100

    point = diff(ids)
    rng = random.Random(seed)
    draws = []
    for _ in range(iterations):
        sample = [ids[rng.randrange(len(ids))] for _ in ids]
        value = diff(sample)
        if not math.isnan(value):
            draws.append(value)
    if not draws:
        return point, float("nan"), float("nan")
    draws.sort()
    lo = draws[int(0.025 * (len(draws) - 1))]
    hi = draws[int(0.975 * (len(draws) - 1))]
    return point, lo, hi


def load_rows(results_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(results_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def fmt(point: float, low: float, high: float) -> str:
    if math.isnan(point):
        return "n/a"
    return f"{point:.1f}% ({low:.1f}-{high:.1f})"


def table(rows: list[dict], group_key, group_label: str) -> list[str]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[group_key(row)].append(row)

    out = [
        f"| Model | {group_label} | n/arm | Negative phrasing | Positive phrasing | Difference (pp) |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for key in sorted(groups):
        bucket = groups[key]
        neg = [r for r in bucket if r["arm"] == "negative"]
        pos = [r for r in bucket if r["arm"] == "positive"]
        per_pair: dict[str, tuple[list[bool], list[bool]]] = defaultdict(lambda: ([], []))
        for r in bucket:
            per_pair[r["pair_id"]][0 if r["arm"] == "negative" else 1].append(bool(r["compliant"]))

        neg_stat = wilson(sum(bool(r["compliant"]) for r in neg), len(neg))
        pos_stat = wilson(sum(bool(r["compliant"]) for r in pos), len(pos))
        d_point, d_lo, d_hi = bootstrap_diff(dict(per_pair))
        diff_cell = "n/a" if math.isnan(d_point) else f"{d_point:+.1f} ({d_lo:+.1f} to {d_hi:+.1f})"
        model = key[0]
        rest = " / ".join(str(k) for k in key[1:]) or "all"
        out.append(
            f"| `{model}` | {rest} | {min(len(neg), len(pos))} | "
            f"{fmt(*neg_stat)} | {fmt(*pos_stat)} | {diff_cell} |"
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--by-alignment", action="store_true")
    ap.add_argument("--by-checker", action="store_true")
    args = ap.parse_args(argv)

    rows = load_rows(args.results_dir)
    if not rows:
        print(
            "No result rows found under "
            f"{args.results_dir}.\n"
            "Run `make bench` with an API key set to produce them; "
            "see docs/HONEST-NUMBERS.md for what is and is not measured yet."
        )
        return 0

    models = sorted({r["model"] for r in rows})
    print(f"Rows: {len(rows)} across {len(models)} model(s): {', '.join(models)}")
    print("Intervals are 95%: Wilson for each arm, paired bootstrap over pairs for the difference.\n")

    print("### Overall\n")
    print("\n".join(table(rows, lambda r: (r["model"],), "Scope")))

    if args.by_alignment:
        print("\n### By constraint alignment\n")
        print("\n".join(table(rows, lambda r: (r["model"], r["alignment"]), "Alignment")))

    if args.by_checker:
        print("\n### By constraint type\n")
        print("\n".join(table(rows, lambda r: (r["model"], r["checker"]), "Checker")))

    print("\n_Generated by `benchmark/report.py` from the raw rows in "
          "`benchmark/results/`._")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
