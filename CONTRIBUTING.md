# Contributing

Contributions welcome, especially benchmark runs. This project publishes no
compliance number of its own yet, so the highest-value contribution is a real
run with its raw rows attached.

## Before opening a PR

```bash
make check
```

That runs the Agent Skills spec validation, 75 checker fixtures, the pair
integrity check, and the relative-link check. CI runs the same thing plus a
mock-endpoint smoke test of the runner.

## Contributing a benchmark run

1. `export ANTHROPIC_API_KEY=...` (or `OPENAI_API_KEY`).
2. `make bench`.
3. Commit `benchmark/results/<provider>-<model>.jsonl` — the whole file,
   including the `output` field on every row.
4. Paste `python3 benchmark/report.py --by-alignment` output into the PR.

**A result with no raw rows behind it stays out of the published table**, and
that holds for results that favour yesand as much as results that do not. The
rows are what let a reader disagree with a checker and settle it by reading the
model's actual output.

## Contributing a pair

Add it to `PAIRS` in `benchmark/build_pairs.py`, then run `make pairs`. Two
things make or break a pair:

- **Both arms must mean the same thing.** If the positive version is also
  clearer, more specific, or differently scoped, the pair measures that instead
  of phrasing, and the result is worthless.
- **Tag `alignment` honestly.** `against-default` where the constraint pushes
  against what the model would do untold; `with-default` where it agrees.
  Mislabelling inflates or hides the effect.

## Contributing a checker

Register it in `benchmark/checkers.py` with `@checker("name")`, then add
compliant and violating fixtures to `CASES` in `benchmark/selftest.py`. The
self-test fails on any checker without fixtures, by design.

Checkers stay deterministic. A judge model would make the headline result
depend on the judge's own handling of negation, which is the variable under
test.

## Contributing to the skill

`skills/yesand/SKILL.md` is the running cost of this project on every
activation, so the bar for adding to it is high: a change should alter what the
agent does, not merely explain it better. Explanatory material belongs in
`docs/`.

Keep the spec constraints intact — folder name matching frontmatter `name`,
description within 1024 characters, spec fields only. `make validate` checks
all of it.

## Style

Reader-facing instructions in this repository are phrased positively, the way
the skill says to write them. Quoted "before" examples and the safety allowlist
are the marked exceptions.

## Claims and citations

Open every source before citing it and quote it verbatim. This project removed
a headline statistic once already because the arXiv ID behind it turned out to
point at a different paper — the account is in
[docs/METHODOLOGY.md](docs/METHODOLOGY.md#a-claim-removed-on-inspection). A PR
that adds a number without a traceable source will be asked for the source.
