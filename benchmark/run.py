#!/usr/bin/env python3
"""Run the yesand compliance benchmark against one model.

For every pair in pairs.jsonl the runner sends the same task twice: once with
the negatively phrased instruction as the system prompt, once with the
positively phrased one. Everything else stays identical, so the phrasing is the
only variable. A deterministic checker from checkers.py scores each reply.

Results append to benchmark/results/<provider>-<model>.jsonl, one row per
completion, with the raw output kept so any reader can re-score it.

    export ANTHROPIC_API_KEY=...
    python3 benchmark/run.py --provider anthropic --model claude-sonnet-5 --repeat 3

    export OPENAI_API_KEY=...
    python3 benchmark/run.py --provider openai --model gpt-5 --repeat 3

    # Any OpenAI-compatible endpoint, including a local Ollama server:
    python3 benchmark/run.py --provider openai --base-url http://localhost:11434/v1 \
        --model qwen3:8b --repeat 3

Only the standard library is used, so the runner needs no install step.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checkers  # noqa: E402

HERE = Path(__file__).parent
PAIRS_PATH = HERE / "pairs.jsonl"
RESULTS_DIR = HERE / "results"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
OPENAI_URL = "https://api.openai.com/v1"


class ProviderError(RuntimeError):
    pass


def _post(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(model: str, system: str, user: str, max_tokens: int,
                   temperature: float, base_url: str | None, timeout: int,
                   max_tokens_field: str | None = None) -> tuple[str, dict]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ProviderError("set ANTHROPIC_API_KEY to run against Anthropic models")
    url = f"{base_url.rstrip('/')}/v1/messages" if base_url else ANTHROPIC_URL
    body = _post(
        url,
        {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
        timeout,
    )
    text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
    usage = body.get("usage", {})
    return text, {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


def call_openai(model: str, system: str, user: str, max_tokens: int,
                temperature: float, base_url: str | None, timeout: int,
                max_tokens_field: str | None = None) -> tuple[str, dict]:
    key = os.environ.get("OPENAI_API_KEY", "unused")
    root = (base_url or OPENAI_URL).rstrip("/")
    # api.openai.com takes max_completion_tokens; most compatible servers take max_tokens.
    field = max_tokens_field or ("max_completion_tokens" if base_url is None else "max_tokens")
    body = _post(
        f"{root}/chat/completions",
        {
            "model": model,
            field: max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        {"content-type": "application/json", "authorization": f"Bearer {key}"},
        timeout,
    )
    choice = body.get("choices", [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    usage = body.get("usage", {})
    return text, {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
    }


PROVIDERS = {"anthropic": call_anthropic, "openai": call_openai}


def load_pairs(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def call_with_retry(fn, attempts: int, **kwargs) -> tuple[str, dict]:
    delay = 2.0
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn(**kwargs)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            status = getattr(exc, "code", None)
            if status is not None and 400 <= status < 500 and status not in (408, 409, 429):
                raise ProviderError(f"{status} from provider: {exc}") from exc
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
    raise ProviderError(f"provider call failed after {attempts} attempts: {last}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=None, help="override the provider endpoint root")
    ap.add_argument("--repeat", type=int, default=3, help="completions per arm per pair (default 3)")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--max-tokens-field", default=None,
                    choices=["max_tokens", "max_completion_tokens"],
                    help="override the OpenAI-compatible token-cap field name "
                         "(default: max_tokens for a custom --base-url, "
                         "max_completion_tokens for api.openai.com)")
    ap.add_argument("--attempts", type=int, default=4, help="retries per call on transient errors")
    ap.add_argument("--seed", type=int, default=20260827, help="seed for arm-order shuffling")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N pairs")
    ap.add_argument("--label", default=None, help="results filename stem (default provider-model)")
    ap.add_argument("--pairs", type=Path, default=PAIRS_PATH)
    ap.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    args = ap.parse_args(argv)

    pairs = load_pairs(args.pairs)
    if args.limit:
        pairs = pairs[: args.limit]

    stem = args.label or f"{args.provider}-{args.model}".replace("/", "_").replace(":", "_")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{stem}.jsonl"

    # Alternate which phrasing goes first so ordering cannot favour one arm.
    rng = random.Random(args.seed)
    jobs: list[tuple[dict, str, int]] = []
    for rep in range(args.repeat):
        for pair in pairs:
            arms = ["negative", "positive"]
            rng.shuffle(arms)
            for arm in arms:
                jobs.append((pair, arm, rep))

    call = PROVIDERS[args.provider]
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    done = 0
    failures = 0

    with out_path.open("a", encoding="utf-8") as fh:
        for pair, arm, rep in jobs:
            done += 1
            try:
                text, usage = call_with_retry(
                    call,
                    args.attempts,
                    model=args.model,
                    system=pair[arm],
                    user=pair["task"],
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    base_url=args.base_url,
                    timeout=args.timeout,
                    max_tokens_field=args.max_tokens_field,
                )
            except ProviderError as exc:
                failures += 1
                print(f"  ! {pair['id']}/{arm}/r{rep}: {exc}", file=sys.stderr)
                continue

            compliant = checkers.run(pair["checker"], text, pair["params"])
            fh.write(
                json.dumps(
                    {
                        "run_started_utc": started,
                        "provider": args.provider,
                        "model": args.model,
                        "temperature": args.temperature,
                        "repeat_index": rep,
                        "pair_id": pair["id"],
                        "checker": pair["checker"],
                        "params": pair["params"],
                        "alignment": pair["alignment"],
                        "arm": arm,
                        "instruction": pair[arm],
                        "task": pair["task"],
                        "output": text,
                        "compliant": compliant,
                        "usage": usage,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            fh.flush()
            mark = "ok" if compliant else "VIOLATION"
            print(f"[{done}/{len(jobs)}] {pair['id']:<7} {arm:<8} r{rep} {mark}")

    print(f"\nwrote {done - failures} rows to {out_path}")
    if failures:
        print(f"{failures} calls failed and were skipped", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
