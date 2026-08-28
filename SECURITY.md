# Security

## Scope

`skills/yesand/SKILL.md` is instructions in Markdown. It bundles no scripts,
requests no network access, and declares no `allowed-tools`, so installing it
adds text to an agent's context and nothing else.

The Python under `benchmark/` and `scripts/` runs only when a maintainer invokes
it. `benchmark/run.py` is the sole component that reaches the network, and only
to the model endpoint named on its command line.

## Reporting a vulnerability

Open a [security advisory](https://github.com/sem-sea/SayYes/security/advisories/new)
for anything that should stay private until fixed. For everything else, a public
issue is fine.

Reports worth sending:

- text in `SKILL.md` that an agent could read as an instruction from an
  attacker rather than from the user
- a rewrite rule that weakens a safety refusal (see below)
- anything in `benchmark/` that reads a file or reaches a host it should leave
  alone

## The safety allowlist

Rule 8 exists because rewriting a refusal into a positive frame can weaken it.
Recasting "refuse to write malware" as "write only benign code" turns a hard
boundary into a soft preference.

The skill preserves verbatim: refusals covering harmful, illegal,
privacy-violating, or abusive content; hard legal and compliance clauses; and
licence and attribution terms. Lines whose status is unclear are kept as they
are and flagged for a human.

**A case where yesand rewrites a genuine safety line is a security bug.** Report
it with the input, the output, and the agent and model, using the
[rewrite issue template](.github/ISSUE_TEMPLATE/rewrite-miss.md).

## Reviewing before you install

The skill is one file, 63 lines. Read it:
[`skills/yesand/SKILL.md`](skills/yesand/SKILL.md). Skills run inside your
agent's context with your agent's permissions, so this is worth doing for any
skill, this one included.
