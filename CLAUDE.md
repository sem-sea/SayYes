# Maintainer notes

Context for anyone working on this repository, human or agent.

## What this repository is

One Agent Skill (`skills/yesand/`) plus the evidence for it. The skill is the
product; the benchmark is what makes the claim checkable. Both halves need to
stay true at once.

## File ownership

| Path | Role | Edit with care because |
| --- | --- | --- |
| `skills/yesand/SKILL.md` | the product | folder name must equal frontmatter `name`; body stays lean by design |
| `benchmark/checkers.py` | scoring | changing a checker invalidates already-committed rows scored under the old one |
| `benchmark/build_pairs.py` | pair source | run `make pairs` after editing; `pairs.jsonl` is generated from it |
| `benchmark/pairs.jsonl` | the test set | committed artifact; keep it in sync with `build_pairs.py` |
| `benchmark/ab.py` | user-facing A/B | the number a reader trusts most; keep its interval-overlap warning intact |
| `benchmark/results/*.jsonl` | raw evidence | append-only; a published figure must trace to rows here |
| `docs/PREREGISTRATION.md` | the decision rules | amending it after results exist requires a commit message saying so |
| `docs/HONEST-NUMBERS.md` | the honesty contract | update it in the same commit as any new result |
| `scripts/validate_skill.py` | spec gate | encodes the Agent Skills spec plus two labelled repo policies |

## Commands

```bash
make check        # everything CI runs: spec validation, checker fixtures, link check
make validate     # SKILL.md against https://agentskills.io/specification
make selftest     # 19 checkers against 75 fixtures, plus pairs.jsonl integrity
make links        # relative markdown links resolve
make pairs        # regenerate pairs.jsonl after editing build_pairs.py
make bench-smoke  # run.py and ab.py end to end against a local mock endpoint, no API key
make bench        # a real run; needs ANTHROPIC_API_KEY or OPENAI_API_KEY
make report       # rebuild the results table from benchmark/results/
make ab-smoke     # ab.py alone against a local mock endpoint
make preview      # regenerate docs/assets/social-preview.png (needs Pillow)
python3 scripts/make_pair_review.py --seed 41 > review-sheet.md   # blind pair review
./scripts/apply_repo_settings.sh                                  # description, homepage, topics
```

## Rules for this repository

**Every number traces to a committed row.** A figure in the README or the docs
comes from `benchmark/results/`, via `benchmark/report.py`. A figure with no row
behind it gets removed, the way the 9.3pp claim was. The full account is in
[docs/METHODOLOGY.md](docs/METHODOLOGY.md#a-claim-removed-on-inspection).

**Every citation gets opened before it ships.** The 9.3pp claim survived several
drafts because the arXiv ID looked plausible. Read the abstract, confirm it says
what the sentence claims, and quote it verbatim.

**Ranges, not point estimates.** `report.py` emits Wilson intervals per arm and
a paired bootstrap for the difference. Publish the interval alongside the point.

**Publish results that disagree with the pitch.** A null or negative result goes
into `docs/HONEST-NUMBERS.md` with the same prominence as a positive one. The
thresholds that would change the framing are written down in
[docs/METHODOLOGY.md](docs/METHODOLOGY.md#what-would-change-the-conclusion).

**Keep the skill body lean.** The activated body is the running cost of this
skill on every use. New material belongs in `references/` or `docs/` unless it
changes what the agent does.

**Write the docs the way the skill says to write instructions.** Reader-facing
instructions in this repository are phrased positively. Quoted "before" examples
and the safety allowlist are the exceptions, and they are marked as such.

## Adding a benchmark pair

1. Add the entry to `PAIRS` in `benchmark/build_pairs.py`.
2. Tag `alignment` honestly: `against-default` where the constraint pushes
   against what the model would do untold, `with-default` where it agrees.
   The split is the point. See the arXiv:2604.07192 discussion in
   [docs/METHODOLOGY.md](docs/METHODOLOGY.md).
3. Keep both arms semantically identical. Differing meaning makes the pair
   measure something other than phrasing.
4. Add fixtures to `CASES` in `benchmark/selftest.py` for any new checker.
5. Run `make pairs && make check`.

## Adding a checker

Register it in `benchmark/checkers.py` with the `@checker("name")` decorator,
then add compliant and violating fixtures to `benchmark/selftest.py`. The
self-test fails on any checker without fixtures, on purpose.

Prose-level checkers call `_strip_code()` first, so a question mark inside
`is_ready?` or a capital inside `README` counts as code rather than prose.

## Release

1. `make check` passes.
2. Bump `version` in `skills/yesand/SKILL.md` frontmatter metadata,
   `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and
   `CITATION.cff`.
3. Update `CITATION.cff` `date-released`.
4. Tag `vX.Y.Z` and cut a GitHub Release.

## Repository settings kept outside git

These live in GitHub settings rather than in the tree; the values to apply are
in [`docs/REPO-SETTINGS.md`](docs/REPO-SETTINGS.md).
