---
name: yesand
description: >-
  Rewrite instructions and prompts into positive form, so every line names the
  action to take rather than a prohibition to remember. Use when authoring or
  editing a system prompt, CLAUDE.md, AGENTS.md, agent rules, a tool
  description, or another skill; when a rule keeps getting ignored; or when the
  user asks to make instructions more reliable, tighten a prompt, or clean up a
  block full of "do not", "never", and "avoid". Preserves genuine safety
  refusals exactly as written.
license: MIT
compatibility: Works in any agent that loads Agent Skills; uses no scripts, network, or system packages.
metadata:
  version: "1.0.0"
  homepage: "https://github.com/sem-sea/SayYes"
---

# yesand

Rewrite instructions so each line names an action to take. Keep the meaning
identical.

## Rewrite rules

Apply these to every instruction you write or edit.

1. Name the wanted alternative — "use X" in place of a ban on Y.
2. Name the wanted location — "edit the existing file in place" in place of a
   ban on new files.
3. Give length a number — "answer in 3 sentences or fewer" in place of a ban on
   verbosity.
4. Name the wanted format — "write plain prose paragraphs" in place of a ban on
   markdown.
5. Name the wanted step — "verify with a tool, then answer" in place of a ban on
   guessing.
6. Name the wanted opening — "open with the answer" in place of a ban on
   pleasantries.
7. Turn every vague limit into a quantity, a format, or a named step.
8. Keep the safety allowlist below exactly as written.

When the wanted behavior resists naming, keep the original line and flag it for
the human with a one-line reason.

## Safety allowlist

Copy these through verbatim:

- refusals covering harmful, illegal, privacy-violating, or abusive content
- hard legal and compliance clauses, including contractual "must not" language
- license and attribution terms

Rewriting a refusal into a positive frame can weaken it. Treat any line you are
unsure about as belonging here: keep it, and flag it.

## Output

Return the rewritten block, then a change list with one `was → now` line per
edit. Reproduce code, paths, URLs, and quoted strings byte for byte.

## Scope

Rewrite the instructions the user hands you. Leave surrounding prose,
documentation, and commit messages as they are.
