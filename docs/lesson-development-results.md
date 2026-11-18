# Development results and acceptance history

Twenty scientific training outcomes are retained: fifteen in the original three-arm
comparison and five second-candidate confirmations. All five official training tasks
were used in each arm; no difficult task was silently replaced or selectively retried.
Candidate 2 ran later than its controls, limiting comparative interpretation.

| Arm | Answer solved | Original hashes unchanged | Generations | Estimated model cost |
|---|---:|---:|---:|---:|
| Baseline A | 3/5 | 4/5 | 46 | $0.06846 |
| Legacy B | 4/5 | 4/5 | 35 | $0.07084 |
| Rejected candidate 1 | 3/5 | 5/5 | 38 | $0.07511 |
| Confirmed candidate 2 | 3/5 | 5/5 | 32 | $0.06102 |

## Why candidate 1 was rejected

The first candidate submitted correctly typed reports but edited a notebook's loader
inside newly created copies. Its original-file hash audit passed, demonstrating the
same blind spot found in the v4 adverse-pair investigation. Its original raw-score
floor also failed. Both failures remain in the [original validation record](../reports/development-v5-candidate1-validation.json).

## Why the comparator was amended

Legacy B answered the notebook questions correctly only after changing the original
`my_datasets.py`; its input audit failed. The original raw-success floor would reward
matching this scientific substitution. Before any candidate-2 execution, an explicit
[protocol amendment](lesson-confirmation-protocol.md) replaced that comparator with
legacy success excluding observed scientific modifications, while retaining the
minimum three successful tasks and all fidelity, typing and submission checks.

Candidate 2 scored 3/5, versus legacy B's 4/5 raw and 3/5 fidelity-qualified. Thus the
**original raw-score floor still failed**. The amended gate passed. This is not a
claim of improved raw development accuracy, nor an externally registered superiority
test. The original protocol, failed gate, amendment and every attempt remain visible.

## What the final candidate actually did

On the two externally dependent tasks, it reported null values and execution blockers
without replacing the dataset loader. On the other tasks it produced numeric answers
with recorded evidence. Original hashes remained unchanged in all five runs.
Manual review found no scientific data/loader/formula/filter substitution in the final
candidate, with the following important bounds:

- The notebook still ran twice and searched HTML before inspecting structured errors.
  The efficiency advice was not fully followed; no universal compliance claim applies.
- On the R Markdown task, rendering failed. The agent executed the author's analytic
  block inline. Both function bodies matched the author text after whitespace and
  quote normalization; data imports and filters were retained. It added output
  printing/CSV serialization and omitted rendering wrappers and an unused setup seed.
  This is not a literal full-document render or proof of universal semantic fidelity.
- Review was Codex-assisted and based on visible commands and artifacts, not independent
  human annotation or access to hidden model reasoning.

The formal v5 study freezes these bytes and evaluates the same exposed fifteen-task
cohort. It must report any adverse effects and cannot treat this amended development
gate as evidence of unseen generalization.

[Final gate and all twenty rows](../reports/development-v5-validation.json) ·
[Manual review scope](../reports/development-confirmation-review-v5.json) ·
[Rejected-candidate evidence](../reports/lesson-development-v5/rejected-candidate.json)
