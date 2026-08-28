# Repository settings

Values that live in GitHub's settings rather than in the tree, recorded here so
they survive a transfer or a fresh clone. Apply them under **Settings → General**
and on the repository home page.

## About — description

Paste into the "About" field on the repository home page:

```text
Agent Skill that rewrites LLM instructions into positive form for more reliable instruction-following. Ships a reproducible compliance benchmark. The reliability complement to caveman.
```

## About — website

```text
https://github.com/sem-sea/SayYes/blob/main/docs/METHODOLOGY.md
```

## Topics

Add all of these. The first six carry most of the discovery weight, since they
are the tags the established skills in this category already use.

```text
claude
claude-code
claude-skills
agent-skills
prompt-engineering
llm
anthropic
agent-skill
claude-code-plugin
instruction-following
system-prompt
ai
```

## Social preview

Upload `docs/assets/social-preview.png` under **Settings → General → Social
preview**. It is 1280×640 (the 2:1 GitHub renders), roughly 48 KB, and carries
no star count or version number, so it stays accurate as the project moves.
Regenerate it with `make preview`.

## Releases

Tag `vX.Y.Z` and cut a GitHub Release for each version. The release notes should
name what changed in `skills/yesand/SKILL.md`, since that is the file people
actually run.

## Citation

`CITATION.cff` sits at the repository root, so GitHub renders a **Cite this
repository** button in the sidebar and generates APA and BibTeX from it. Nothing
to configure.

## Benchmark secret

`.github/workflows/benchmark.yml` runs the preregistered benchmark on demand and
pushes the raw rows to a `results/…` branch, giving each result a public log, a
commit SHA, and a timestamp nobody typed. It needs one key.

Add under **Settings → Secrets and variables → Actions**:

| Secret | For |
| --- | --- |
| `ANTHROPIC_API_KEY` | running against a Claude model |
| `OPENAI_API_KEY` | running against an OpenAI model |

Either one is enough; the workflow stops with a clear error when the key for the
chosen provider is absent. Trigger it from **Actions → Benchmark → Run
workflow**, naming the provider and model.

Three properties worth keeping:

- **It is manual, not scheduled.** A cron job that repeats until a favourable
  result appears is the multiple-comparisons problem wearing a schedule.
- **The sample size is hard-coded**, not a workflow input.
  `docs/PREREGISTRATION.md` fixes it at 3 repeats, and exposing it as a dial
  would let a run quietly extend itself until the interval stopped spanning
  zero.
- **Rows land on a branch, never on main.** A figure reaches the published table
  by review, after the with-default control group has been checked.

A local run is equally valid, and `make bench` produces identical rows. CI adds
provenance rather than correctness.

## Directory submissions

Places worth listing the skill, each with its own contribution format to follow:

- [`skills` registry](https://github.com/vercel-labs/skills) — the CLI behind
  `npx skills add`
- `awesome-claude-skills` and `awesome-agent-skills` lists — open a PR matching
  each list's CONTRIBUTING format
- [agentskills.io](https://agentskills.io) client and skill directories

A note on submission hygiene: some directories run static analysis over skill
content looking for prompt-injection patterns. `skills/yesand/SKILL.md` uses no
scripts, no network access, and no angle brackets, which keeps it clean through
those scans.

## What stays off this list

No `FUNDING.yml`. This project takes no money, and a sponsor button on a
credibility-first repository invites the wrong read.
