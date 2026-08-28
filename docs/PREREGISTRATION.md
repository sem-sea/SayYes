# Preregistration

The analysis plan for yesand's compliance benchmark, committed **before any
result exists**.

Anyone can verify the ordering: `benchmark/results/` holds no rows in the commit
that adds this file, and `git log --follow docs/PREREGISTRATION.md` dates the
plan. A result published later either meets a criterion written here or misses
it, and both outcomes were named in advance.

This exists because the author of this benchmark wrote its test set and wants
the hypothesis to be true. That combination produces favourable results whether
or not the effect is real. Fixing the decision rule beforehand is the cheapest
available defence.

## Hypothesis

Instructions phrased as an action to take are complied with more often than
prohibitions of identical meaning, on constraints that push against a model's
default behaviour.

## Design

- 41 pairs, each one task plus two phrasings of one identical constraint.
- Instruction in the system prompt, task in the user message.
- 3 completions per arm per pair, temperature 0, 1,024-token cap.
- **246 completions per model**, fixed in advance.
- Arm order shuffled per pair from seed 20260827, so position cannot favour
  either phrasing.
- Three models: one Anthropic, one OpenAI, one open-weight served locally. The
  open-weight run matters because it costs a replicator nothing.

## Primary outcome

The paired difference in compliance rate, **positive minus negative**, over the
36 `against-default` pairs, computed per model, with a 95% bootstrap interval
resampled over pair ids.

Pair ids, rather than individual completions: three repeats of one pair are
correlated, and treating them as independent would understate the interval.

## Decision rules

Fixed now. Whichever row the primary outcome lands in is the framing that ships.

| Result | What the project then claims |
| --- | --- |
| ≥ +5pp, interval excludes 0, same sign on all three models | The reliability framing stands. README leads with the measured range. |
| +3 to +5pp, or interval excludes 0 on some models only | Reframe to readability and maintainability of positive instructions. The reliability claim is dropped to "directional, model-dependent". |
| Interval includes 0 on two or more models | **Report no effect.** Positive phrasing is presented as a style and maintainability recommendation carrying vendor guidance, with no compliance claim. |
| ≤ −3pp with the interval excluding 0 on any model | **Publish prominently.** A result contradicting the pitch leads `docs/HONEST-NUMBERS.md` and is stated in the README. |

## Falsification test on the instrument

The 5 `with-default` pairs are a control, not a measurement. Their constraints
agree with what the model would do untold, so they comply near ceiling either
way and phrasing has almost no headroom to act in. arXiv:2604.07192 reports
99%+ compliance for conventional constraints.

**Expected: a difference within ±3pp on the control group.**

A difference outside that band is evidence that the pair set is biased, meaning
the positive arms are winning on specificity, clarity, or ease rather than on
phrasing. If it happens, the primary result is **withheld rather than
published**, the pairs go back through the review in
[PAIR-REVIEW.md](PAIR-REVIEW.md), and any subsequent run says that it followed a
revision.

The control group is small, so it detects gross bias rather than subtle bias.
It is a smoke alarm, not a proof of cleanliness.

## Stopping rule

The sample size above is final. Adding repeats after seeing a result, or
stopping early once a run looks favourable, both turn the interval into
decoration.

A run may be discarded **in whole, per model**, for provider failures affecting
more than 5% of calls, or for a checker defect found afterwards. The discard and
its reason get recorded in `docs/HONEST-NUMBERS.md`. Discarding selected rows is
excluded.

## Locked before data

Changing any of these after seeing results invalidates the preregistration:

- the contents of `benchmark/pairs.jsonl`, including every `alignment` tag
- the checker implementations in `benchmark/checkers.py`
- the analysis in `benchmark/report.py`
- the decision rules above

A checker defect discovered after a run is fixable, and the fix requires
re-running **every** model from scratch under the corrected checker, with the
old rows kept in git history.

## Permitted after data, labelled exploratory

Per-checker and per-alignment breakdowns are descriptive. They are useful for
understanding where an effect lives, and they carry no confirmatory weight: with
19 checkers over 41 pairs, some will look significant by chance alone. Any such
finding gets published as a hypothesis for a future run.

## Amendments

Editing this file after results exist is allowed and must be visible: the commit
message says the plan changed after data, and gives the reason. The
pre-amendment version stays in git history, where a reader can diff it.

## How a run is executed

Either `make bench` locally, or **Actions → Benchmark → Run workflow**, which
runs the same command on a GitHub runner and pushes the rows to a `results/…`
branch. The workflow hard-codes the sample size from this document rather than
exposing it as an input, and stays manual rather than scheduled.

CI adds provenance, not validity: a public log, a commit SHA, and a timestamp
the author did not type. A local run producing the same rows is equally good
evidence, and both are weaker than someone else reproducing it.

## Status

**No run has been performed.** `benchmark/results/` is empty, and the table in
[HONEST-NUMBERS.md](HONEST-NUMBERS.md) stays empty until one is.
