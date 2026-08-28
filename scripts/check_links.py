#!/usr/bin/env python3
"""Check that relative markdown links in this repository resolve to real files.

Absolute http(s) links stay out of scope here, since resolving them would make
CI depend on third-party uptime. Run scripts/check_links.py --list-external to
print them for a periodic manual sweep.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".smoke"}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def markdown_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list-external", action="store_true", help="print external URLs and exit")
    args = ap.parse_args(argv)

    external: set[str] = set()
    failures: list[str] = []
    checked = 0

    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                external.add(target)
                continue
            if target.startswith("#"):
                continue
            checked += 1
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            resolved = (path.parent / relative).resolve()
            if not resolved.exists():
                failures.append(
                    f"{path.relative_to(ROOT)}: [{target}] resolves to a missing path"
                )

    if args.list_external:
        for url in sorted(external):
            print(url)
        return 0

    if failures:
        print(f"FAIL: {len(failures)} broken relative link(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"ok: {checked} relative link(s) resolve across {len(markdown_files())} markdown files; "
        f"{len(external)} external URL(s) left for manual review"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
