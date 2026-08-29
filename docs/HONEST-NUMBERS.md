# Honest numbers

Where yesand helps, where it does nothing, and what has been measured. Read
this before quoting any figure from this repository.

## The compliance table

The harness is built and verified: 19 checkers passing 75 fixtures, the runner
tested end to end. The benchmark has not been run against a live model, so the
table below is empty and yesand quotes no compliance percentage.

| Model | Pairs | Negative phrasing | Positive phrasing | Difference (pp) |
| --- | ---: | --- | --- | --- |
| _(unrun)_ | 41 | n/a | n/a | n/a |

Filling this in takes one command and an API key:

```bash
export ANTHROPIC_API_KEY=...
make bench
```

`benchmark/report.py` regenerates the table from the committed raw rows, so
every published figure traces back to an output any reader can re-score.

The thresholds that will decide how this result is framed are already fixed in
[PREREGISTRATION.md](PREREGISTRATION.md), including the case where the answer is
"no effect" and the case where it contradicts the pitch.

## What can be said today

Directional, and sourced. Full citations are in
[METHODOLOGY.md](METHODOLOGY.md).

- **Positive phrasing is documented vendor guidance.** Anthropic lists "Tell
  Claude what to do instead of what not to do" first among its output-format
  techniques, with "Do not use markdown in your response" as the example to
  avoid. Google's guidance recommends the same direction.
- **Ironic rebound after negation is real and measured.** ReboundBench
  (arXiv:2511.12381) released 5,000 negation prompts and found rebound "arises
  immediately after negation and intensifies with longer or semantic
  distractors."
- **The mechanism has a documented counter-current.** arXiv:2503.22395 found
  that *larger* models handled negation better, and that results varied by
  language. A flat "models cannot process negation" overstates the evidence.

No published study we located reports a positive-versus-negative compliance gap
of any specific size. If you have seen one quoted, ask for the paper.

## Where yesand does nothing

These cases are known in advance, and the benchmark is built to surface them
rather than hide them.

**Constraints the model already agrees with.** arXiv:2604.07192 reports that
"conventional constraints achieve 99%+ compliance" while "counter-intuitive
constraints opposing model defaults fail at 10--100%." At 99% compliance there
is under a point of headroom, so phrasing cannot help. Five of the 41 pairs are
tagged `with-default` as a control that should show approximately zero effect.

A lift on that group is a warning rather than a win: it means either a checker
is scoring the arms differently for a reason unrelated to compliance, or the
pairs are confounded and the positive arms are simply easier to satisfy.
[PREREGISTRATION.md](PREREGISTRATION.md) sets the band at ±3pp and commits to
withholding the primary result rather than publishing it if the control breaches
that.

**Instruction blocks already written positively.** yesand rewrites
prohibitions. A prompt with none is returned unchanged, and the change list is
empty. That is the correct result and not a failure.

**Genuine safety refusals.** These are preserved verbatim by design. On a
prompt that is mostly refusals, yesand changes almost nothing.

**Vague instructions with no natural quantity.** "Write in a friendly tone" has
no countable target. Rule 7 has nothing to convert, and the line survives as it
was.

## Token savings

Secondary, modest, and sometimes zero or negative.

A positive rewrite replaces a short prohibition with a longer specification.
"Don't be verbose" is 3 tokens; "answer in 3 sentences or fewer" is about 7.
Savings appear only where one positive line collapses several prohibitions, as
when four separate bans on formatting become one instruction naming the wanted
format.

`run.py` records `input_tokens` and `output_tokens` on every row, so a run
produces this figure as a by-product. Reliability is the claim to lead with
regardless.

## Cost of a full run

The arithmetic: 41 pairs × 2 arms ×
3 repeats = **246 completions per model**. Prompts are short (a one-line system
instruction plus a one-line task) and outputs are capped at 1,024 tokens, most
landing far below that. At current frontier per-token prices that lands in
low single-digit US dollars per model, so three models sit in roughly the
$5 to $15 range.

An order of magnitude rather than a quote. The measured figure is recorded here
after the first run, computed from the `usage` field on the committed rows.

## Measure it yourself

Your own A/B outranks anything this repository publishes, including whatever
eventually fills the table above. This repo's pairs are 41 constraints chosen by
its author; your prompt is the one you actually run.

**1. Compare two phrasings on your task.**

```bash
export ANTHROPIC_API_KEY=...
python3 benchmark/ab.py --a original.txt --b rewritten.txt --task task.txt \
    --checker no_bullets --repeat 20 --provider anthropic --model claude-sonnet-5
```

`ab.py` alternates arm order, scores both with one deterministic checker, and
prints a 95% Wilson interval per arm. It states plainly when the intervals
overlap, which means the run distinguished nothing.

**2. Compare provider-billed totals, when cost is the question.** Run the same
task under both phrasings and read your provider's usage page. Billed totals
outrank the output-token counts `ab.py` prints, because prompts, cached context,
and retries all land on your bill and none of them appear in a completion
length.

**3. Reproduce this repository's numbers** with `make bench`.

### Reading a result honestly

- An interval spanning zero is not a small effect; it is an unmeasured one.
  Raise `--repeat` or report no effect.
- A single task is a single task. A win on one prompt generalises to your other
  prompts only as far as the constraint type generalises.
- Run the arms in both orders, which `ab.py` does, so position cannot masquerade
  as phrasing.
- Temperature 0 hides the variance you actually live with. `ab.py` defaults to
  1.0 for that reason.

If your measurement contradicts anything on this page,
[open an issue](https://github.com/sem-sea/SayYes/issues) with the raw rows from
`--save`. A contradicting result gets added here.

## Limits of the design

Worth knowing before quoting a result from this harness.

- **41 pairs is a small sample.** It supports a directional finding across
  constraint types; it does not support a precise per-constraint-type effect
  size. Several checkers carry only two pairs.
- **The checkers are heuristics.** `count_sentences` splits on terminal
  punctuation with a short abbreviation guard; `no_preamble` matches a fixed
  phrase list. Both will mis-score some outputs. The raw text is committed
  precisely so a disagreement can be settled by reading it.
- **The instruction sits in the system prompt.** Results may not transfer to
  instructions buried mid-context or arriving late in a long conversation,
  which is where a lot of real agent instruction-following actually happens.
- **English only.** arXiv:2503.22395 found negation handling varies by
  language, so these results speak for English alone.
- **Model versions move.** Any published table is a snapshot of the models named
  in it on the date recorded in the rows.

## yesand and caveman

[caveman](https://github.com/JuliusBrussee/caveman) (MIT, roughly 100k stars at
the time of writing, a moving number) compresses model **output**. yesand
rewrites the **instructions** going in. They act on different halves of the
exchange and stack without conflict.

yesand has no benchmark result to compare against caveman's, and will not claim
a comparison until it does.
