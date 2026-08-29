# Results

Raw benchmark rows land here, one JSONL file per model, one row per completion.

No runs recorded yet. See
[../../docs/HONEST-NUMBERS.md](../../docs/HONEST-NUMBERS.md).

## Producing a file

```bash
export ANTHROPIC_API_KEY=...
python3 ../run.py --provider anthropic --model claude-sonnet-5 --repeat 3
```

## Row shape

Each line is one completion, keeping the full model output so anyone can
re-score it without spending a token:

```json
{
  "run_started_utc": "...",
  "provider": "anthropic",
  "model": "...",
  "temperature": 0.0,
  "repeat_index": 0,
  "pair_id": "md-01",
  "checker": "no_markdown",
  "params": {},
  "alignment": "against-default",
  "arm": "negative",
  "instruction": "...",
  "task": "...",
  "output": "...",
  "compliant": false,
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
```

Files here are append-only. A figure published anywhere in this repository
traces back to rows in this directory, via `python3 ../report.py`.
