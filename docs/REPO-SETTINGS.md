# Repository settings

Values that live in GitHub's settings rather than in the tree, recorded here so
they survive a transfer or a fresh clone. Apply them under **Settings → General**
and on the repository home page.

## Applying these in one command

```bash
./scripts/apply_repo_settings.sh
```

The script holds the description, homepage, and topics below, validates them
against GitHub's limits, applies them through the gh CLI or a token, and prints
the result. `DRY_RUN=1` shows the payloads without sending them.

Keeping these under version control means they survive a repository transfer,
they show up in a diff when they change, and nobody has to retype a 318
character string into a web form.

## About: description

The single highest-weight field after the repository name. Paste into "About" on
the repository home page:

```text
yesand: positive prompting for agent instructions. An Agent Skill that rewrites prohibitions in your system prompt, CLAUDE.md or AGENTS.md into the action to take, following Anthropic and Google prompt-engineering guidance. Ships a preregistered instruction-following benchmark. Claude Code, Cursor, Codex and 74 more.
```

318 of 350 characters. Three things it is doing:

- **It leads with `yesand`.** The repository is named `SayYes` while the product
  is `yesand`, so this is the only high-weight surface carrying the name people
  read in every install command. Without it, a search for the product name finds
  nothing.
- **It names the artifacts people search for**: system prompt, CLAUDE.md,
  AGENTS.md, Claude Code, Cursor, Codex.
- **It attributes rather than asserts.** The guidance is credited to Anthropic
  and Google instead of claiming a reliability gain this project has yet to
  measure. `docs/HONEST-NUMBERS.md` says no compliance number is published, and
  the About field is the line most likely to be quoted back, so it must not
  out-claim that page.

## About: website

```text
https://github.com/sem-sea/SayYes/blob/main/docs/METHODOLOGY.md
```

## Topics

GitHub allows 20. Add all of these. Topic pages are a real browsing surface, and
a repository with none is invisible there.

```text
prompt-engineering
positive-prompting
instruction-following
agent-skills
agent-skill
claude-skills
claude-code
claude-code-plugin
claude
anthropic
llm
system-prompt
prompt-optimization
ai-agents
benchmark
llm-evaluation
cursor
codex
```

The first six carry most of the weight: they combine the terms this project
should own with the tags established skills in this category already use.

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
| `ANTHROPIC_WORKSPACE_ID` | required when the Claude key is identity-linked |
| `OPENAI_API_KEY` | running against an OpenAI model |

An identity-linked Claude key rejects every request without a workspace id,
answering `anthropic-workspace-id is required`. The id starts with `wrkspc_`
and appears in the Console under the workspace's settings.

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

- [`skills` registry](https://github.com/vercel-labs/skills), the CLI behind
  `npx skills add`
- `awesome-claude-skills` and `awesome-agent-skills` lists, where you open a PR
  matching each list's CONTRIBUTING format
- [agentskills.io](https://agentskills.io) client and skill directories

A note on submission hygiene: some directories run static analysis over skill
content looking for prompt-injection patterns. `skills/yesand/SKILL.md` uses no
scripts, no network access, and no angle brackets, which keeps it clean through
those scans.

## What stays off this list

No `FUNDING.yml`. This project takes no money, and a sponsor button on a
credibility-first repository invites the wrong read.
