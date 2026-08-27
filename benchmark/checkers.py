#!/usr/bin/env python3
"""Deterministic compliance checkers for the yesand benchmark.

Every checker takes the model's raw output plus a parameter mapping and returns
True when the output complies with the instruction. Checkers stay deterministic
and model-free on purpose: a judge model would make the headline number depend
on the judge's own handling of negation, which is the thing under test.
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Mapping

Checker = Callable[[str, Mapping[str, Any]], bool]

REGISTRY: dict[str, Checker] = {}


def checker(name: str) -> Callable[[Checker], Checker]:
    def register(fn: Checker) -> Checker:
        REGISTRY[name] = fn
        return fn

    return register


# --- helpers -------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*(```|~~~)", re.M)
_BULLET_RE = re.compile("^\\s*(?:[-*+•‣]|\\d+[.)])\\s+\\S", re.M)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.M)
_BOLD_RE = re.compile(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1", re.S)
_TABLE_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)
_SENTENCE_END_RE = re.compile(r"[.!?]+(?=\s|$)")
_EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "☀-➿"
    "\U0001f1e6-\U0001f1ff"
    "←-⇿"
    "️"
    "]"
)


def _strip_code(text: str) -> str:
    """Remove fenced blocks and inline spans so prose checks skip code.

    Checks about prose style score the prose. A question mark inside
    `is_ready?`, a capital inside `README`, or a hyphen bullet inside a shell
    snippet all belong to code, so they are removed before the check runs.
    """
    without_fences = re.sub(r"(```|~~~).*?\1", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", without_fences)


def count_sentences(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    # Protect common abbreviations and decimals from the sentence splitter.
    guarded = re.sub(r"\b(?:e\.g|i\.e|etc|vs|Mr|Mrs|Dr|Fig|approx)\.", " ", stripped)
    guarded = re.sub(r"(\d)\.(\d)", r"\1 \2", guarded)
    parts = [p for p in _SENTENCE_END_RE.split(guarded) if p.strip()]
    return max(len(parts), 1)


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


# --- checkers ------------------------------------------------------------


@checker("no_markdown")
def no_markdown(text: str, params: Mapping[str, Any]) -> bool:
    return not (
        _FENCE_RE.search(text)
        or _BULLET_RE.search(text)
        or _HEADING_RE.search(text)
        or _BOLD_RE.search(text)
        or _TABLE_RE.search(text)
    )


@checker("no_bullets")
def no_bullets(text: str, params: Mapping[str, Any]) -> bool:
    return _BULLET_RE.search(_strip_code(text)) is None


@checker("no_headings")
def no_headings(text: str, params: Mapping[str, Any]) -> bool:
    return _HEADING_RE.search(_strip_code(text)) is None


@checker("no_bold")
def no_bold(text: str, params: Mapping[str, Any]) -> bool:
    return _BOLD_RE.search(_strip_code(text)) is None


@checker("no_code_fence")
def no_code_fence(text: str, params: Mapping[str, Any]) -> bool:
    return _FENCE_RE.search(text) is None


@checker("no_emoji")
def no_emoji(text: str, params: Mapping[str, Any]) -> bool:
    return _EMOJI_RE.search(text) is None


@checker("max_sentences")
def max_sentences(text: str, params: Mapping[str, Any]) -> bool:
    return count_sentences(text) <= int(params["n"])


@checker("max_words")
def max_words(text: str, params: Mapping[str, Any]) -> bool:
    return count_words(text) <= int(params["n"])


@checker("max_chars")
def max_chars(text: str, params: Mapping[str, Any]) -> bool:
    return len(text.strip()) <= int(params["n"])


@checker("single_paragraph")
def single_paragraph(text: str, params: Mapping[str, Any]) -> bool:
    return "\n\n" not in text.strip()


@checker("no_questions")
def no_questions(text: str, params: Mapping[str, Any]) -> bool:
    return "?" not in _strip_code(text)


@checker("no_first_person")
def no_first_person(text: str, params: Mapping[str, Any]) -> bool:
    pattern = r"\b(I|I'm|I've|I'll|me|my|mine|we|we're|our|us)\b"
    return re.search(pattern, _strip_code(text)) is None


@checker("no_preamble")
def no_preamble(text: str, params: Mapping[str, Any]) -> bool:
    opener = text.strip()[:120].lower()
    starts = (
        "sure", "certainly", "of course", "absolutely", "great question",
        "good question", "happy to", "i'd be happy", "i am happy",
        "let me", "here's", "here is", "thanks", "thank you", "no problem",
    )
    return not opener.startswith(starts)


@checker("no_apology")
def no_apology(text: str, params: Mapping[str, Any]) -> bool:
    return re.search(r"\b(sorry|apologi[sz]e|apologies|regret)\b", text, re.I) is None


@checker("no_trailing_offer")
def no_trailing_offer(text: str, params: Mapping[str, Any]) -> bool:
    tail = text.strip()[-200:].lower()
    offers = (
        "let me know", "feel free", "hope this helps", "hope that helps",
        "if you have any", "anything else", "happy to help", "just ask",
        "would you like me to", "want me to",
    )
    return not any(phrase in tail for phrase in offers)


@checker("json_object")
def json_object(text: str, params: Mapping[str, Any]) -> bool:
    stripped = text.strip()
    if stripped.startswith("```"):
        return False
    try:
        parsed = json.loads(stripped)
    except (ValueError, TypeError):
        return False
    if not isinstance(parsed, dict):
        return False
    required = params.get("keys")
    if required:
        return all(key in parsed for key in required)
    return True


@checker("lowercase_only")
def lowercase_only(text: str, params: Mapping[str, Any]) -> bool:
    return re.search(r"[A-Z]", _strip_code(text)) is None


@checker("forbidden_words")
def forbidden_words(text: str, params: Mapping[str, Any]) -> bool:
    words = [re.escape(w) for w in params["words"]]
    pattern = r"\b(?:" + "|".join(words) + r")\b"
    return re.search(pattern, text, re.I) is None


@checker("no_bare_url")
def no_bare_url(text: str, params: Mapping[str, Any]) -> bool:
    return re.search(r"https?://", _strip_code(text)) is None


def run(name: str, text: str, params: Mapping[str, Any] | None = None) -> bool:
    try:
        fn = REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown checker {name!r}; known: {sorted(REGISTRY)}") from None
    return bool(fn(text, params or {}))
