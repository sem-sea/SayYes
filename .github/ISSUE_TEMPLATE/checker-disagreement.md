---
name: A benchmark checker scored something wrong
about: A checker marked compliant output as violating, or the reverse
title: "checker: "
labels: benchmark
---

**Checker name**

From `benchmark/checkers.py`, for example `no_preamble`.

**The text it scored**

```text

```

**Score it gave, and the score you expected**

**Why the expected score is right**

Point at the rule the text does or does not satisfy. Raw rows in
`benchmark/results/` can be re-scored offline with
`python3 benchmark/report.py`, so a disagreement can be settled by reading the
committed output.
