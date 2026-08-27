# Methodology

What yesand does, why the underlying claim is credible, and exactly how far the
evidence reaches. For measured results and their limits, read
[HONEST-NUMBERS.md](HONEST-NUMBERS.md).

## The rewrite rules

Each rule converts a prohibition into the action to take. The meaning stays
identical; only the frame changes.

| # | Pattern | Rewrite |
| --- | --- | --- |
| 1 | ban on a tool or token | name the wanted alternative — "use X" |
| 2 | ban on a location | name the wanted location — "edit the existing file in place" |
| 3 | ban on verbosity | give length a number — "answer in 3 sentences or fewer" |
| 4 | ban on a format | name the wanted format — "write plain prose paragraphs" |
| 5 | ban on guessing | name the wanted step — "verify with a tool, then answer" |
| 6 | ban on pleasantries | name the wanted opening — "open with the answer" |
| 7 | vague limit | turn it into a quantity, a format, or a named step |
| 8 | safety refusal | copy it through verbatim |

Rule 7 carries most of the practical weight. "Keep it short" and "be concise"
give a model nothing to check itself against; "4 sentences or fewer" gives it a
countable target. Rule 8 is the deliberate exception, and it is why the skill
body contains negations of its own: some lines earn their negative frame.

### Where rule 8 applies

Copy through verbatim:

- refusals covering harmful, illegal, privacy-violating, or abusive content
- hard legal and compliance clauses, including contractual "must not" language
- license and attribution terms

A refusal states a boundary rather than a task. Recasting "refuse to write
malware" as "write only benign code" narrows a hard boundary into a soft
preference, and that is a downgrade. Treating an uncertain line as a safety line
costs one flagged line for a human to read; treating it as an ordinary one costs
a weakened guardrail.

## Why the frame matters

Two vendor guides and three papers support the direction. Together they
establish that positive phrasing is recommended practice and that negation has a
documented failure mode. They do not establish a specific effect size, which is
what the benchmark exists to measure.

### Vendor guidance

Anthropic's prompting best practices list this first among ways to steer output
format:

> **Tell Claude what to do instead of what not to do**
>
> - Instead of: "Do not use markdown in your response"
> - Try: "Your response should be composed of smoothly flowing prose paragraphs."

— [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
Anthropic

Google's guidance frames the same preference from the other side:

> Giving the model instructions on what to do is an effective and efficient way
> to customize model behavior.

— [Give clear and specific instructions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/clear-instructions),
Google Cloud

### The negation literature

**[arXiv:2402.07896](https://arxiv.org/abs/2402.07896)** — *Suppressing Pink
Elephants with Direct Principle Feedback* (Castricato, Lile, Anand, Schoelkopf,
Verma, Biderman; February 2024). Establishes the "pink elephant" task: keeping a
model off a named topic while it discusses a preferred alternative. Its
contribution is a fine-tuning method, so it evidences that the failure mode is
real and worth engineering against, rather than that any prompt phrasing fixes
it.

**[arXiv:2503.22395](https://arxiv.org/abs/2503.22395)** — *Negation: A Pink
Elephant in the Large Language Models' Room?* (Vrabcová, Kadlčík, Sojka,
Štefánik, Spiegel; March 2025). Builds multilingual negation datasets. Its
findings cut both ways, and the honest reading includes both: larger models
handled negation **better**, and language structure mattered, with English
scoring higher than German or Czech. Anyone citing negation research as a flat
"models cannot handle negation" is overstating this paper.

**[arXiv:2511.12381](https://arxiv.org/abs/2511.12381)** — *Don't Think of the
White Bear: Ironic Negation in Transformer Models Under Cognitive Load* (Mann,
Saxena, Tandon, Sun, Toteja, Zhu; November 2025). Releases **ReboundBench**,
5,000 systematically varied negation prompts, and reports that "rebound
consistently arises immediately after negation and intensifies with longer or
semantic distractors." This is the closest published support for the mechanism
yesand targets: the suppressed concept becomes *more* accessible right after the
instruction that suppressed it.

### A claim removed on inspection

An earlier draft of this project carried a "~9.3 percentage-point compliance gap
between positive and negative phrasing," attributed to arXiv:2604.07192. That
citation was checked and does not support the claim, so the claim is gone.

[arXiv:2604.07192](https://arxiv.org/abs/2604.07192) is Hanzhang Tang's *Compact
Constraint Encoding for LLM Code Generation: An Empirical Study of Token
Economics and Constraint Compliance* (April 2026). It studies token economics of
constraint headers across 11 models and 16 tasks, and its Δ = 9 percentage-point
figure separates **conventional constraints from counter-intuitive ones**, which
is a different axis from positive-versus-negative phrasing. The paper never
reports 9.3pp, and no published study we located reports a positive-versus-
negative compliance gap of any specific size.

That paper does contribute something useful, and yesand's benchmark is built
around it: it reports that "counter-intuitive constraints opposing model defaults
fail at 10--100%, while conventional constraints achieve 99%+ compliance." A
constraint a model already agrees with complies at ceiling regardless of
phrasing, so phrasing can only matter where the constraint pushes against a
default. Every pair in `benchmark/pairs.jsonl` is tagged `with-default` or
`against-default` for exactly this reason, and the report splits on it.

## Benchmark design

Modelled on [IFEval](https://arxiv.org/abs/2311.07911) (Zhou et al., 2023):
constraints a program can verify, scored by code rather than by a judge model.

**Pairing.** Each of the 41 pairs holds one task and two phrasings of one
identical constraint. The system prompt carries the instruction, the user message
carries the task, and everything else — model, temperature, token cap — stays
fixed. Phrasing is the only variable.

**Deterministic scoring.** The 19 checkers in `benchmark/checkers.py` are regex
and parsing heuristics. A judge model was rejected deliberately: it would make
the headline number depend on the judge's own handling of negation, which is the
variable under test.

**Order control.** Which arm runs first is shuffled per pair from a fixed seed,
so ordering cannot systematically favour either phrasing.

**Repeats.** Three completions per arm per pair by default, at temperature 0.
Temperature 0 leaves real residual variance, and repeats make it visible.

**Statistics.** Wilson score intervals per arm; a paired bootstrap over pair ids
for the difference, because repeats of one pair are correlated and treating them
as independent would understate the interval.

**Coverage.** 19 constraint types over 41 pairs — 36 tagged `against-default`,
5 `with-default`. The `with-default` group is small, and it is there as a
control that should show roughly no effect, rather than as a measured population
in its own right.

### Why this harness rather than promptfoo

promptfoo is the conventional choice and would work. This harness uses the
Python standard library instead, for three reasons: the checkers stay in one
auditable file rather than split across YAML assertions; `make check` runs the
full checker suite in CI with no API key and no npm install; and the paired
bootstrap needs the raw per-pair rows, which a single tool owning both scoring
and reporting makes straightforward. The cost is that yesand does not inherit
promptfoo's provider matrix, so `run.py` speaks two protocols by hand: the
Anthropic Messages API, and anything OpenAI-compatible, which covers OpenAI,
most hosted open-weight endpoints, and a local Ollama server.

## Reproducing a run

```bash
export ANTHROPIC_API_KEY=...
python3 benchmark/run.py --provider anthropic --model claude-sonnet-5 --repeat 3
python3 benchmark/report.py --by-alignment --by-checker
```

Raw rows land in `benchmark/results/<provider>-<model>.jsonl`, one row per
completion, each keeping the full model output. Anyone can re-score the same
rows under different checkers without spending a token.

## What would change the conclusion

- A measured lift under about 3 to 5 percentage points, or one that fails to
  hold across models, moves the pitch to readability and maintainability of
  positive instructions and drops the reliability framing.
- A lift concentrated entirely in one constraint type means the finding belongs
  to that constraint type, and the README should say so.
- A negative result stands as a result. It would be published in
  [HONEST-NUMBERS.md](HONEST-NUMBERS.md) with the same prominence as a positive
  one.
