# Blind pair review

A procedure for checking that the 41 benchmark pairs measure phrasing and
nothing else. Run it **before** the benchmark, as
[PREREGISTRATION.md](PREREGISTRATION.md) requires.

## The problem it addresses

Each pair is supposed to hold two phrasings of one identical constraint. If a
positive arm is also more specific, clearer, or simply a lower bar to clear,
then the benchmark measures specificity rather than phrasing — and returns a
clean, well-bounded, confidently-reported result about the wrong thing.

The author of the pairs cannot catch this. They know which arm is which and
they expect one to win, so every judgement runs downhill. A reviewer catches it
only while blind.

## Running it

```bash
python3 scripts/make_pair_review.py --seed 41 > review-sheet.md
```

The sheet shuffles pair order, labels the two instructions X and Y with the
positive arm placed as X in exactly half the items, and mentions positive,
negative, alignment, and yesand nowhere. Hand it to someone who has read no
other part of this repository.

For each item the reviewer answers two questions:

- **Q1 — do X and Y ask for the same thing?** `same` / `different` / `unsure`
- **Q2 — is one easier to satisfy, more specific, or clearer, setting aside how
  each is worded?** `X` / `Y` / `neither`

Q2 carries the weight. Q1 catches outright meaning drift, which is the obvious
error and the rarer one. Q2 catches the confound that would actually survive to
publication.

Recover the mapping afterwards:

```bash
python3 scripts/make_pair_review.py --seed 41 --unblind
```

## Reading the answers

**Q1.** Any item marked `different` is a broken pair. Fix it in
`benchmark/build_pairs.py`, run `make pairs`, and re-review that item under a
new seed. Items marked `unsure` are worth rewriting for clarity even though
they are not defects.

**Q2 is the real test.** Translate each `X` or `Y` answer into positive or
negative using the unblind table, then count.

- Roughly balanced, with `neither` common — the pairs isolate phrasing. Proceed.
- **A consistent lean toward the positive arm** — the pairs are confounded. The
  benchmark would return a lift caused by specificity rather than phrasing, so
  the leaning pairs get rewritten so both arms sit at equal specificity, and the
  review runs again under a new seed.
- A consistent lean toward the negative arm — also a confound, in the direction
  that would understate the effect. Same fix.

There is no threshold worth hard-coding here on 41 items; a clear pattern across
a third or more of the items is a signal, and a handful is noise. Record the
count either way.

## Reviewers

Best to worst:

1. **A person who has not read this repository.** They have no hypothesis to
   confirm.
2. **A model given the sheet alone**, with no context about yesand, negation, or
   what the answers are for. Cheap, repeatable, and weaker than a person —
   a model may carry its own prior about instruction phrasing.
3. **The pair author.** Nearly worthless for Q2, and listed only to be explicit
   that it does not count as a review.

Two or three independent reviewers beat one, and disagreement between them is
itself informative about which items are ambiguous.

## Recording the outcome

Commit the completed sheet and the seed under `docs/reviews/`, then note in
[HONEST-NUMBERS.md](HONEST-NUMBERS.md) that the pairs were reviewed, by how many
people, and what changed as a result. A review that changed nothing is still
worth recording — it is the evidence that the check happened.

If a review runs **after** a benchmark result exists, say so plainly. A pair set
revised in light of a result it produced is no longer preregistered, and the run
that follows is a new run rather than a correction of the old one.

## Status

**No review has been run.** The script works and produces a balanced, leak-free
sheet; nobody has filled one in.
