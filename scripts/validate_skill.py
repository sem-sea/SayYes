#!/usr/bin/env python3
"""Validate SKILL.md files against the Agent Skills specification.

Spec reference: https://agentskills.io/specification

Checks the constraints the spec states, plus two repository policies that the
spec leaves open (angle brackets in frontmatter, body size). Policy checks are
labelled so a reader can tell them apart from spec checks.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

SPEC_URL = "https://agentskills.io/specification"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

# Repository policies (stricter than the spec, chosen deliberately).
MAX_BODY_LINES = 500      # spec calls this a recommendation; we enforce it
MAX_BODY_WORDS = 5000     # proxy for the spec's "< 5000 tokens recommended"


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("file starts with YAML frontmatter delimited by ---")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("frontmatter has a closing --- delimiter")
    return text[4:end], text[end + 4 :].lstrip("\n")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    try:
        raw_fm, body = split_frontmatter(text)
    except ValueError as exc:
        return [f"frontmatter: expected that {exc}"]

    try:
        fm = yaml.safe_load(raw_fm)
    except yaml.YAMLError as exc:
        return [f"frontmatter: expected valid YAML ({exc})"]

    if not isinstance(fm, dict):
        return ["frontmatter: expected a YAML mapping"]

    # --- spec: required fields -------------------------------------------
    name = fm.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name: expected a non-empty string (spec: required)")
    else:
        if len(name) > 64:
            errors.append(f"name: expected 1-64 characters, found {len(name)}")
        if not NAME_RE.match(name):
            errors.append(
                "name: expected lowercase a-z, 0-9 and single interior hyphens, "
                f"found {name!r}"
            )
        parent = path.parent.name
        if name != parent:
            errors.append(
                f"name: expected it to match the parent directory {parent!r}, found {name!r}"
            )

    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description: expected a non-empty string (spec: required)")
    elif len(description) > 1024:
        errors.append(f"description: expected 1-1024 characters, found {len(description)}")

    # --- spec: optional fields -------------------------------------------
    compatibility = fm.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            errors.append("compatibility: expected a string")
        elif len(compatibility) > 500:
            errors.append(
                f"compatibility: expected 1-500 characters, found {len(compatibility)}"
            )

    metadata = fm.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            errors.append("metadata: expected a mapping of string keys to string values")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(
                        f"metadata.{key}: expected a string value, found {type(value).__name__}"
                    )

    allowed_tools = fm.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append("allowed-tools: expected a space-separated string")

    unknown = sorted(set(fm) - SPEC_FIELDS)
    if unknown:
        errors.append(
            f"frontmatter: expected only spec fields {sorted(SPEC_FIELDS)}, found extra {unknown}"
        )

    # --- policy checks ----------------------------------------------------
    if "<" in raw_fm or ">" in raw_fm:
        stripped = re.sub(r"^\s*description:\s*>-?\s*$", "", raw_fm, flags=re.M)
        if "<" in stripped or ">" in stripped:
            errors.append(
                "frontmatter [policy]: expected plain text; angle brackets are kept out so "
                "frontmatter stays inert wherever a client interpolates it into a prompt"
            )

    lines = body.splitlines()
    if len(lines) > MAX_BODY_LINES:
        errors.append(
            f"body [policy]: expected {MAX_BODY_LINES} lines or fewer, found {len(lines)}"
        )
    words = len(body.split())
    if words > MAX_BODY_WORDS:
        errors.append(f"body [policy]: expected {MAX_BODY_WORDS} words or fewer, found {words}")

    return errors


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]] or sorted(Path("skills").glob("*/SKILL.md"))
    if not paths:
        print("no SKILL.md files found under skills/", file=sys.stderr)
        return 1

    failed = False
    for path in paths:
        errors = validate(path)
        body_words = len(path.read_text(encoding="utf-8").split())
        if errors:
            failed = True
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok   {path}  ({body_words} words total)")
    if failed:
        print(f"\nSpec: {SPEC_URL}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
