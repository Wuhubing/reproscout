# Controller, network, and lesson revision comparison

V5 completed sixty scientific cells under one unchanged freeze. Infrastructure attempts are separately retained and cannot satisfy a cell. Scientific failures are final.

| Metric | v2 | v3 | v4 | v5 |
|---|---:|---:|---:|---:|
| Retained attempts | 60 | 60 | 61 | 60 |
| Answer-solved / 60 | 20/60 (33.3%) | 1/60 (1.7%) | 46/60 (76.7%) | 46/60 (76.7%) |
| A solved / 30 | 11/30 | 0/30 | 25/30 | 20/30 |
| B solved / 30 | 9/30 | 1/30 | 21/30 | 26/30 |
| Original-input hashes unchanged / changed / missing | 59 / 0 / 1 | 60 / 0 / 0 | 58 / 2 / 1 | 60 / 0 / 0 |
| Answer solved with original hashes unchanged | 20 | 1 | 46 | 46 |
| Old byte-bound stops | 39 | 0 | 0 | 0 |
| Native context stops | 0 | 0 | 0 | 0 |
| 20-call stops | 0 | 0 | 8 | 4 |
| Terminal count failures | 0 | 59 | 0 | 0 |
| Infrastructure attempts | 1 | 59 | 1 | 0 |
| Model generations | 423 | 39 | 721 | 664 |
| Sample time, minutes (all attempts) | 75.67 | 23.69 | 143.07 | 130.39 |
| Calendar interval, minutes | 76.93 | 57.03 | 147.75 | 134.55 |
| Estimated model cost (all attempts) | $0.75550 | $0.05651 | $1.84094 | $1.50081 |
| Uncached cost upper bound | $1.49456 | $0.14628 | $4.67572 | $3.91940 |

V3 is infrastructure-invalid: its low cost and success rate reflect DNS aborts, not an informative scientific comparison. V4 repaired transport and request accounting; v5 revises only the B lesson treatment, with the same base prompt, scientific tools, model, scorer, inputs and limits. The shared retry guard now recognizes v5 IDs. Cross-version results also include sampling and time effects.

V5 A solved 20/30 and B 26/30. Within v5, A-only pairs: 1; B-only: 7; both solved: 19; neither: 3. Thirty paired observations reuse fifteen tasks. No significance claim applies.

All 664 generations are retained; native counts matched usage on 664. Application operations including preflights: 1448; failed operations: 0. These are application logs, not TCP packet traces.

Compared with v4, B gains five scored successes while the unchanged A condition loses five; the combined score remains 46/60. This baseline movement prevents attributing the entire cross-version change to the lesson text. Calendar time decreases from 147.75 to 134.55 minutes and estimated model cost from $1.84094 to $1.50081. Within v5, all four call-cap failures are in A; B has none.

## Four previously adverse pairs

| Task | Repeat | v4 A / B | v5 A / B | v5 B evidence |
|---|---:|---|---|---|
| capsule-0504157 | 2 | True / False | False / True | [Run](../reports/runs/20261118T093113458234Z-capsule-0504157-run-B2/report.html) |
| capsule-2708693 | 1 | True / False | False / True | [Run](../reports/runs/20261118T085150930191Z-capsule-2708693-run-B1/report.html) |
| capsule-9054015 | 1 | True / False | True / True | [Run](../reports/runs/20261118T082236563632Z-capsule-9054015-run-B1/report.html) |
| capsule-9054015 | 2 | True / False | True / True | [Run](../reports/runs/20261118T092341047794Z-capsule-9054015-run-B2/report.html) |

## Fidelity and interpretation

The original-input hash audit does not detect modifications to newly created scientific copies, nor prove semantic support. The v4 adverse-pair analysis identifies such a case even among answer-solved runs. Do not label the hash-and-answer intersection as fully faithful reproduction. Source exceptions and supplemental trajectory review remain separate from the unchanged scorer.

This revision was informed by exposed test trajectories and validated on five training tasks. It is a test-informed regression study, not a new held-out generalization test. Formatting counterfactuals in the old analysis do not alter historical scores. All failures remain visible.

Costs use returned token usage and conservative reservations, exclude development/host/image costs, and are not invoices. Sample time includes in-task execution; calendar time also includes preflights, cooldowns and scheduling.

The four previously failing B samples now all pass the scorer, but targeted review finds continued scientific reimplementation in two of them (0504157 repeat 2 and 9054015 repeat 1). The former also submits a numeric string, contrary to the lesson. Read the [four-pair follow-up](adverse-pair-followup-v5.md) and [limited manual review](../reports/trajectory-review-v5.json); these are score recoveries, not four certified faithful reproductions.

## Evidence

- [Four-pair diagnosis](lesson-pair-analysis-v4.md)
- [Revision protocol](lesson-revision-protocol.md)
- [Development results and gate amendment](lesson-development-results.md)
- [Development validation](../reports/development-v5-validation.json)
- [Full metrics](../reports/controller-comparison.json)
- [All outcomes](results.md)
- [Portable app](../reports/index.html)
- [Source exceptions](../reports/source-integrity-v5.json)
- [Application request ledger](../reports/network-audit-v5.json)
- [Archived v4 interpretation](../reports/archive-v4/controller-comparison.md)
