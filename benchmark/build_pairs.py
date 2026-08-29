#!/usr/bin/env python3
"""Generate benchmark/pairs.jsonl. Run: python3 benchmark/build_pairs.py"""
from __future__ import annotations

import json
from pathlib import Path

# fields: id, checker, params, alignment, task, negative, positive
PAIRS: list[dict] = [
    dict(
        id="md-01", checker="no_markdown", params={}, alignment="against-default",
        task="Explain what a database index is and when adding one helps.",
        negative="Do not use markdown in your response.",
        positive="Your response should be composed of smoothly flowing prose paragraphs.",
    ),
    dict(
        id="md-02", checker="no_markdown", params={}, alignment="against-default",
        task="Summarise three trade-offs of keeping all services in a single monorepo.",
        negative="Do not use any markdown formatting.",
        positive="Write the answer as plain prose paragraphs.",
    ),
    dict(
        id="md-03", checker="no_markdown", params={}, alignment="against-default",
        task="Compare optimistic and pessimistic locking for a booking system.",
        negative="Never format your answer with markdown.",
        positive="Format your answer as unbroken prose.",
    ),
    dict(
        id="bul-01", checker="no_bullets", params={}, alignment="against-default",
        task="Describe the three stages of a thorough code review.",
        negative="Do not use bullet points or numbered lists.",
        positive="Write the answer as continuous sentences inside paragraphs.",
    ),
    dict(
        id="bul-02", checker="no_bullets", params={}, alignment="against-default",
        task="What are the main causes of memory leaks in long-running Node.js services?",
        negative="Avoid bulleted and numbered lists.",
        positive="Present each cause as its own sentence within a paragraph.",
    ),
    dict(
        id="bul-03", checker="no_bullets", params={}, alignment="against-default",
        task="Walk through how to migrate a table to a new column type with zero downtime.",
        negative="Do not present the steps as a list.",
        positive="Present the steps as consecutive sentences, each opening with an ordinal word.",
    ),
    dict(
        id="hed-01", checker="no_headings", params={}, alignment="against-default",
        task="Write a short guide to generating and installing an SSH key pair.",
        negative="Do not use markdown headings.",
        positive="Write consecutive paragraphs, using a topic sentence to open each step.",
    ),
    dict(
        id="hed-02", checker="no_headings", params={}, alignment="against-default",
        task="Explain how to profile a slow HTTP endpoint end to end.",
        negative="Never add section headers to your answer.",
        positive="Let each paragraph carry its own topic sentence in place of a section header.",
    ),
    dict(
        id="bld-01", checker="no_bold", params={}, alignment="against-default",
        task="Explain the CAP theorem to a backend engineer new to distributed systems.",
        negative="Do not bold any text.",
        positive="Use plain unstyled text throughout.",
    ),
    dict(
        id="bld-02", checker="no_bold", params={}, alignment="against-default",
        task="Describe what changes when a service moves from HTTP/1.1 to HTTP/2.",
        negative="Do not emphasise words with asterisks or underscores.",
        positive="Keep every word in plain unstyled text.",
    ),
    dict(
        id="fen-01", checker="no_code_fence", params={}, alignment="against-default",
        task="Give the shell command that lists the ten largest files in the current tree.",
        negative="Do not wrap the command in a code fence.",
        positive="Give the command as a single plain-text line.",
    ),
    dict(
        id="fen-02", checker="no_code_fence", params={}, alignment="against-default",
        task="Give the git command that discards all unstaged changes in one file.",
        negative="Do not use triple backticks.",
        positive="Write the command inline as ordinary text.",
    ),
    dict(
        id="emo-01", checker="no_emoji", params={}, alignment="with-default",
        task="Write a two-line release note announcing a fix for a crash on startup.",
        negative="Do not use emoji.",
        positive="Use words alone.",
    ),
    dict(
        id="emo-02", checker="no_emoji", params={}, alignment="against-default",
        task="Write a warm three-line welcome banner for a CLI tool's first run.",
        negative="Do not include any emoji or decorative symbols.",
        positive="Convey the warmth through word choice alone.",
    ),
    dict(
        id="sen-01", checker="max_sentences", params={"n": 2}, alignment="against-default",
        task="What does a load balancer do, and why does a growing service need one?",
        negative="Do not write more than two sentences.",
        positive="Write two sentences or fewer.",
    ),
    dict(
        id="sen-02", checker="max_sentences", params={"n": 3}, alignment="against-default",
        task="Explain how generational garbage collection decides what to collect.",
        negative="Do not exceed three sentences.",
        positive="Write three sentences or fewer.",
    ),
    dict(
        id="sen-03", checker="max_sentences", params={"n": 1}, alignment="against-default",
        task="Define idempotence as it applies to HTTP methods.",
        negative="Do not use more than one sentence.",
        positive="Answer in exactly one sentence.",
    ),
    dict(
        id="sen-04", checker="max_sentences", params={"n": 2}, alignment="against-default",
        task="Explain why a team might choose event sourcing over a mutable audit table.",
        negative="Never go beyond two sentences.",
        positive="Keep the answer to two sentences or fewer.",
    ),
    dict(
        id="wrd-01", checker="max_words", params={"n": 40}, alignment="against-default",
        task="Summarise what unit tests are for and what they cannot tell you.",
        negative="Do not use more than 40 words.",
        positive="Use 40 words or fewer.",
    ),
    dict(
        id="wrd-02", checker="max_words", params={"n": 60}, alignment="with-default",
        task="Explain in plain terms what Docker does for a development team.",
        negative="Do not write more than 60 words.",
        positive="Write 60 words or fewer.",
    ),
    dict(
        id="wrd-03", checker="max_words", params={"n": 25}, alignment="against-default",
        task="Describe the difference between authentication and authorisation.",
        negative="Do not exceed 25 words.",
        positive="Use 25 words or fewer.",
    ),
    dict(
        id="chr-01", checker="max_chars", params={"n": 280}, alignment="against-default",
        task="Write an announcement for v2 of our public API, which adds cursor pagination.",
        negative="Do not write more than 280 characters.",
        positive="Write 280 characters or fewer.",
    ),
    dict(
        id="chr-02", checker="max_chars", params={"n": 160}, alignment="against-default",
        task="Write the alert text for a pager notification about elevated 5xx rates.",
        negative="Do not exceed 160 characters.",
        positive="Use 160 characters or fewer.",
    ),
    dict(
        id="par-01", checker="single_paragraph", params={}, alignment="against-default",
        task="Describe how a browser resolves a domain name to an IP address.",
        negative="Do not break your answer into multiple paragraphs.",
        positive="Write the answer as one continuous paragraph.",
    ),
    dict(
        id="par-02", checker="single_paragraph", params={}, alignment="against-default",
        task="Explain what happens between a git commit and a deployed container image.",
        negative="Do not use paragraph breaks.",
        positive="Deliver the whole explanation in a single paragraph.",
    ),
    dict(
        id="qst-01", checker="no_questions", params={}, alignment="with-default",
        task="A solo developer is picking between PostgreSQL and MySQL for a small app. Advise them.",
        negative="Do not ask the user any questions.",
        positive="Answer using statements only, committing to one recommendation.",
    ),
    dict(
        id="qst-02", checker="no_questions", params={}, alignment="against-default",
        task="A user says their tests are flaky but gives no further detail. Help them.",
        negative="Do not ask any clarifying questions.",
        positive="State the most likely causes and the check for each one.",
    ),
    dict(
        id="fps-01", checker="no_first_person", params={}, alignment="against-default",
        task="A build failed with 'ENOENT: no such file or directory, open .env'. Explain the cause.",
        negative="Do not refer to yourself.",
        positive="Write in the third person, describing the code and the error alone.",
    ),
    dict(
        id="fps-02", checker="no_first_person", params={}, alignment="against-default",
        task="Explain why a Python script raises 'ModuleNotFoundError' inside a virtualenv.",
        negative="Never use first-person pronouns.",
        positive="Keep every sentence in the third person.",
    ),
    dict(
        id="pre-01", checker="no_preamble", params={}, alignment="against-default",
        task="What port does HTTPS use by default?",
        negative="Do not begin with pleasantries or restate the question.",
        positive="Open with the answer itself.",
    ),
    dict(
        id="pre-02", checker="no_preamble", params={}, alignment="against-default",
        task="How do I undo the most recent git commit while keeping the changes staged?",
        negative="Do not start with phrases like 'Sure' or 'Here is'.",
        positive="Start the first sentence with the command or the fact being asked for.",
    ),
    dict(
        id="pre-03", checker="no_preamble", params={}, alignment="against-default",
        task="Which HTTP status code fits a request that is well-formed but semantically invalid?",
        negative="Do not preface your answer.",
        positive="Lead with the status code.",
    ),
    dict(
        id="apo-01", checker="no_apology", params={}, alignment="against-default",
        task="Your previous answer said the fifth Fibonacci number is 8. Give the correct value.",
        negative="Do not apologise.",
        positive="Move straight to the corrected value.",
    ),
    dict(
        id="apo-02", checker="no_apology", params={}, alignment="with-default",
        task="Explain what a semaphore does in concurrent programming.",
        negative="Do not apologise anywhere in the answer.",
        positive="Keep the tone matter-of-fact throughout.",
    ),
    dict(
        id="off-01", checker="no_trailing_offer", params={}, alignment="against-default",
        task="Explain what a webhook is and how it differs from polling.",
        negative="Do not end with an offer of further help.",
        positive="End on the final substantive sentence.",
    ),
    dict(
        id="off-02", checker="no_trailing_offer", params={}, alignment="against-default",
        task="Explain when a team should reach for a message queue.",
        negative="Never close with 'let me know if you have questions' or similar.",
        positive="Let the last sentence of the explanation be the last sentence of the reply.",
    ),
    dict(
        id="jsn-01", checker="json_object", params={"keys": ["name", "role"]}, alignment="against-default",
        task="Extract the person's name and role from: 'Priya Raman is the staff engineer on payments.'",
        negative="Do not include any text outside the JSON object.",
        positive="Reply with a single JSON object holding the keys name and role as the entire response.",
    ),
    dict(
        id="jsn-02", checker="json_object", params={"keys": ["city", "country"]}, alignment="against-default",
        task="Extract the city and country from: 'The datacentre sits just outside Eemshaven, Netherlands.'",
        negative="Do not wrap the JSON in a code fence or add commentary.",
        positive="Reply with a single bare JSON object holding the keys city and country.",
    ),
    dict(
        id="low-01", checker="lowercase_only", params={}, alignment="against-default",
        task="Write a one-line commit message for a fix to a typo in the README.",
        negative="Do not use capital letters.",
        positive="Write entirely in lowercase.",
    ),
    dict(
        id="wds-01", checker="forbidden_words",
        params={"words": ["delve", "leverage", "robust", "seamless"]}, alignment="against-default",
        task="Write two sentences for a changelog describing a new read-through caching layer.",
        negative="Do not use the words delve, leverage, robust, or seamless.",
        positive="In place of delve, leverage, robust, and seamless, choose plain everyday synonyms.",
    ),
    dict(
        id="url-01", checker="no_bare_url", params={}, alignment="with-default",
        task="Recommend one good way for a beginner to learn regular expressions.",
        negative="Do not include any URLs.",
        positive="Refer to any source by its name alone.",
    ),
]


def main() -> int:
    seen = set()
    for pair in PAIRS:
        if pair["id"] in seen:
            raise SystemExit(f"duplicate pair id: {pair['id']}")
        seen.add(pair["id"])
        missing = {"id", "checker", "params", "alignment", "task", "negative", "positive"} - set(pair)
        if missing:
            raise SystemExit(f"{pair['id']}: missing fields {sorted(missing)}")
        if pair["alignment"] not in {"with-default", "against-default"}:
            raise SystemExit(f"{pair['id']}: unknown alignment {pair['alignment']!r}")

    out = Path(__file__).parent / "pairs.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for pair in PAIRS:
            fh.write(json.dumps(pair, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {len(PAIRS)} pairs to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
