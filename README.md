<div align="center">

# yesand

**An Agent Skill that rewrites LLM instructions into positive form, so every line names the action to take — and the model follows it more reliably.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sem-sea/SayYes/actions/workflows/ci.yml/badge.svg)](https://github.com/sem-sea/SayYes/actions/workflows/ci.yml)
[![Agent Skills spec](https://img.shields.io/badge/Agent%20Skills-spec%20compliant-7ee7a8)](https://agentskills.io/specification)
[![Stars](https://img.shields.io/github/stars/sem-sea/SayYes?style=flat)](https://github.com/sem-sea/SayYes/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/sem-sea/SayYes)](https://github.com/sem-sea/SayYes/commits)

</div>

```diff
- Do not use markdown in your response.
+ Your response should be composed of smoothly flowing prose paragraphs.

- Don't be verbose. Keep it short.
+ Answer in 4 sentences or fewer.

- NEVER create new files.
+ Edit existing files in place.
```

Install it in one line:

```bash
npx skills add sem-sea/SayYes
```

## Why

Anthropic's prompting guide lists this first among the ways to steer a model's
output format:

> **Tell Claude what to do instead of what not to do**
>
> - Instead of: "Do not use markdown in your response"
> - Try: "Your response should be composed of smoothly flowing prose paragraphs."
>
> — [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic

Google's guidance points the same way: "Giving the model instructions on what to
do is an effective and efficient way to customize model behavior."

The research explains the mechanism. [ReboundBench](https://arxiv.org/abs/2511.12381)
released 5,000 systematically varied negation prompts and found that ironic
rebound — the suppressed idea becoming *more* accessible — "consistently arises
immediately after negation and intensifies with longer or semantic distractors."

Most prompts are written the other way round anyway. A CLAUDE.md accumulates
"don't", "never", and "avoid" one incident at a time, and each one leaves the
model holding a thing to remember rather than a move to make. yesand converts
them.

## Install

<details open>
<summary><b>Claude Code — as a plugin</b></summary>

```bash
claude plugin marketplace add sem-sea/SayYes
claude plugin install yesand@sayyes
```

</details>

<details open>
<summary><b>Any of 77 agents — via the skills CLI</b></summary>

```bash
# install into every agent the CLI detects on this machine
npx skills add sem-sea/SayYes

# or target one agent
npx skills add sem-sea/SayYes -a cursor
```

| Agent | Flag | Installs to |
| --- | --- | --- |
| Claude Code | `-a claude-code` | `.claude/skills/` |
| Cursor | `-a cursor` | `.agents/skills/` |
| Codex | `-a codex` | `.agents/skills/` |
| GitHub Copilot | `-a github-copilot` | `.agents/skills/` |
| Gemini CLI | `-a gemini-cli` | `.agents/skills/` |
| Windsurf | `-a windsurf` | `.windsurf/skills/` |
| OpenCode | `-a opencode` | `.agents/skills/` |
| Amp | `-a amp` | `.agents/skills/` |
| Cline | `-a cline` | `.agents/skills/` |
| Zed | `-a zed` | `.agents/skills/` |
| Goose | `-a goose` | `.goose/skills/` |
| Droid (Factory) | `-a droid` | `.factory/skills/` |

Run `npx skills add sem-sea/SayYes -l` to list what the CLI finds, and
`npx skills --help` for the full agent roster. Flags and paths above come from
[`skills`](https://github.com/vercel-labs/skills) v1.5.23.

</details>

<details>
<summary><b>By hand</b></summary>

Copy `skills/yesand/` into your agent's skills directory, keeping the folder
name `yesand` — the Agent Skills spec requires the folder name to match the
`name` in the frontmatter.

</details>

## How it works

1. Ask an agent to rewrite a block of instructions — a system prompt, a
   CLAUDE.md, an AGENTS.md, a tool description, or another skill.
2. yesand activates on that phrasing and reads its eight rewrite rules.
3. Each prohibition becomes the action it implies. Vague limits become
   quantities: "keep it short" becomes "4 sentences or fewer".
4. Safety refusals, legal clauses, and licence terms pass through **verbatim**,
   with anything ambiguous kept as it was and flagged for a human.
5. You get the rewritten block plus a `was → now` line per change, so every edit
   is reviewable before it lands.

The skill body is 282 words and costs about 120 tokens to keep resident at
discovery time. See [`skills/yesand/SKILL.md`](skills/yesand/SKILL.md) — it is
short enough to read in a minute, and it is the whole product.

## Benchmark

The harness in [`benchmark/`](benchmark/) runs 41 instruction pairs across 19
constraint types. Each pair holds one task and two phrasings of one identical
constraint; the system prompt carries the instruction, the model, temperature,
and token cap stay fixed, and arm order is shuffled from a seed. Nineteen
deterministic checkers score compliance — a judge model was rejected on purpose,
since it would make the result depend on the judge's own handling of negation.

```bash
make check        # 19 checkers against 75 fixtures, plus spec + link validation
make bench-smoke  # the runner end to end against a local mock endpoint
make bench        # a real run (set ANTHROPIC_API_KEY or OPENAI_API_KEY)
```

**No model has been run yet, so this project publishes no compliance number of
its own.** The harness works and the table is empty. Read
[docs/HONEST-NUMBERS.md](docs/HONEST-NUMBERS.md) for what that means, where
yesand is known in advance to do nothing, and what a run costs.

## FAQ

**Does telling an LLM what not to do actually make it worse?**
It measurably makes negation-shaped failures more likely. ReboundBench
(arXiv:2511.12381) documents rebound immediately after a negation. The honest
counterweight: arXiv:2503.22395 found *larger* models handle negation better,
and results vary by language. Direction, yes; a headline percentage, no.

**What is the difference between yesand and [caveman](https://github.com/JuliusBrussee/caveman)?**
caveman compresses what the model writes back. yesand rewrites the instructions
going in. Different halves of the exchange.

**Can I use both?**
Yes, and they stack cleanly — one shortens output, the other hardens
instructions. Neither touches what the other operates on.

**Does this save tokens?**
Sometimes, modestly, and sometimes not at all. A positive rewrite is often
*longer* than the ban it replaces; savings appear where one positive line
collapses several prohibitions. Lead with reliability. The token arithmetic is
in [HONEST-NUMBERS.md](docs/HONEST-NUMBERS.md).

**What happens to my safety rules?**
They stay exactly as written. Recasting "refuse to write malware" as "write only
benign code" turns a hard boundary into a soft preference, so yesand keeps
refusals, legal clauses, and licence terms verbatim, and flags anything
uncertain rather than rewriting it.

**Where is the 9.3 percentage-point figure I saw quoted?**
Removed. It traced to arXiv:2604.07192, which is a token-economics paper about
code-generation constraints; its Δ = 9pp separates conventional from
counter-intuitive constraints, not positive from negative phrasing.
[The full correction is in METHODOLOGY.md](docs/METHODOLOGY.md#a-claim-removed-on-inspection).

## Docs

- [METHODOLOGY.md](docs/METHODOLOGY.md) — the eight rules, the sources, the benchmark design
- [HONEST-NUMBERS.md](docs/HONEST-NUMBERS.md) — what is measured, what is not, and where yesand does nothing
- [examples/before-after.md](examples/before-after.md) — ten self-contained rewrites
- [CLAUDE.md](CLAUDE.md) — maintainer notes

## Sources

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — Anthropic
- [Give clear and specific instructions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/clear-instructions) — Google Cloud
- [Agent Skills specification](https://agentskills.io/specification)
- [arXiv:2402.07896](https://arxiv.org/abs/2402.07896) — Suppressing Pink Elephants with Direct Principle Feedback
- [arXiv:2503.22395](https://arxiv.org/abs/2503.22395) — Negation: A Pink Elephant in the Large Language Models' Room?
- [arXiv:2511.12381](https://arxiv.org/abs/2511.12381) — Don't Think of the White Bear (ReboundBench)
- [arXiv:2311.07911](https://arxiv.org/abs/2311.07911) — IFEval, the model for this benchmark's design

## A note on this README

Every instruction here is phrased positively. The negatives you can see are
quoted inputs in the before/after examples, and the safety allowlist — which is
the honest exception the skill itself carries.

## License

[MIT](LICENSE). Copy it, fork it, paste the rules straight into your own prompt.

<div align="center">

[![Star history](https://api.star-history.com/svg?repos=sem-sea/SayYes&type=Date)](https://star-history.com/#sem-sea/SayYes&Date)

</div>
