# yesand documentation

Documentation for [yesand](../README.md), an Agent Skill that rewrites LLM and
agent instructions into positive form. Start here to find the page you need.

## The technique

**[METHODOLOGY.md](METHODOLOGY.md)** covers what positive prompting is, the
eight rewrite rules, and the evidence behind them. It quotes Anthropic's
prompting guidance and Google's, and reviews three papers on how language
models handle negation, including ReboundBench and its 5,000 negation prompts.
It also documents a claim this project removed after checking the citation.

**[../examples/before-after.md](../examples/before-after.md)** shows ten
rewrites in full: output format, file handling, response length, tool use,
scope control, structured output, tone, and one safety line deliberately left
as it was.

## The evidence

**[HONEST-NUMBERS.md](HONEST-NUMBERS.md)** states what has been measured, what
has not, and the four situations where yesand changes nothing at all. Read it
before quoting any figure from this repository. As of today it reports no
compliance percentage, because no model has been run.

**[PREREGISTRATION.md](PREREGISTRATION.md)** fixes the analysis plan before any
result exists: the primary outcome, the sample size, the stopping rule, and
four decision thresholds covering every outcome including "no effect" and
"contradicts the pitch".

**[PAIR-REVIEW.md](PAIR-REVIEW.md)** describes the blind review that checks
whether the 41 benchmark pairs measure instruction phrasing rather than
specificity. **[reviews/](reviews/)** holds completed review sheets.

## Running things

**[../benchmark/](../benchmark/)** holds the instruction-following benchmark:
41 paired prompts across 19 deterministically checkable constraint types,
designed after IFEval.

**[REPO-SETTINGS.md](REPO-SETTINGS.md)** records the values that live in GitHub
settings rather than in the tree, including the repository description and
topics, applied by
[`../scripts/apply_repo_settings.sh`](../scripts/apply_repo_settings.sh).

**[../CONTRIBUTING.md](../CONTRIBUTING.md)** covers contributing a benchmark
run, a pair, or a checker. **[../SECURITY.md](../SECURITY.md)** covers what the
skill can reach and how to report a rewrite that weakens a safety refusal.

## Frequently asked

- **What is positive prompting?** Writing an instruction as the action to take
  rather than the outcome to avoid. See
  [the definition in the README](../README.md#what-is-positive-prompting-in-prompt-engineering).
- **Does it save tokens?** Sometimes, modestly, and sometimes not at all. See
  [Token savings](HONEST-NUMBERS.md#token-savings).
- **What happens to safety rules?** They are preserved verbatim. See
  [Where rule 8 applies](METHODOLOGY.md#where-rule-8-applies).
- **How do I measure it on my own prompt?** Use `benchmark/ab.py`. See
  [Measure it yourself](HONEST-NUMBERS.md#measure-it-yourself).
