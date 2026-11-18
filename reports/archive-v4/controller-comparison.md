# Controller and network recovery comparison

Prepared-v4 completed all sixty scientific cells under one unchanged freeze. Infrastructure attempts are retained separately and never satisfy a cell. An unsolved scientific outcome remains final.

| Metric | v2 | v3 | v4 |
|---|---:|---:|---:|
| Retained attempts | 60 | 60 | 61 |
| Answer-solved / 60 planned cells | 20/60 (33.3%) | 1/60 (1.7%) | 46/60 (76.7%) |
| A solved / 30 | 11/30 | 0/30 | 25/30 |
| B solved / 30 | 9/30 | 1/30 | 21/30 |
| Solved with unchanged prepared inputs | 20 | 1 | 46 |
| Legacy byte-bound stops | 39 | 0 | 0 |
| Native-token context stops | 0 | 0 | 0 |
| Terminal counting failures | 0 | 59 | 0 |
| Infrastructure attempts | 1 | 59 | 1 |
| Zero-generation attempts | 1 | 55 | 1 |
| Source unchanged / changed / missing | 59 / 0 / 1 | 60 / 0 / 0 | 58 / 2 / 1 |
| Model generations | 423 | 39 | 721 |
| Sum of recorded sample time (minutes) | 75.67 | 23.69 | 143.07 |
| First-start to last-completion interval (minutes) | 76.93 | 57.03 | 147.75 |
| Estimated returned model-usage cost | $0.75550 | $0.05651 | $1.84094 |
| Uncached cost upper bound (including reservations) | $1.49456 | $0.14628 | $4.67572 |
| 20-call budget stops | 0 | 0 | 8 |
| Monetary admission stops | 0 | 0 | 0 |
| Other Inspect sample limits | {} | {} | {} |

The 20-call cap is a separate, unchanged policy from the repaired request-size guard. Scientific budget stops remain final unsolved outcomes, rather than infrastructure retries.

## Interpretation

Prepared-v3 was infrastructure-invalid: 59 DNS failures, 55 zero-generation attempts, and only one answer-solved attempt. Its low cost and time reflect early aborts, not efficiency. v2 had 39 premature byte-bound stops and one startup failure. Neither problem should be interpreted as evidence against lessons.

Under v4, A solved 12/15 and 13/15; B solved 10/15 and 11/15. Average B-minus-A solved count is -2.0. This is a descriptive observation on fifteen reused tasks, not a statistical-significance or unseen-generalization claim. Cross-version differences also include temporal and model-sampling variation.

Native counts matched returned input usage on 721 of 721 generations. 297 generated requests crossed the former byte guard. Retained request-level failures: 0; retained infrastructure attempts: 1. All-attempt answer success: 46/61.

Sample timers include in-task retries and scientific execution. The calendar interval also includes between-cell preflights, cooldowns and scheduling gaps; neither is CPU time. Costs use returned token usage, exclude host/image/development costs, and are not an invoice. Unknown usage remains represented by conservative reservations. All infrastructure attempt time and cost are included.

Source integrity is a separate criterion: correct answers produced after changing scientific inputs are not faithful unchanged-input reproductions. Audit absence is never treated as unchanged. See every run, including failed attempts, for evidence.

## Verification and retained evidence

- [Frozen recovery protocol](network-recovery-protocol.md)
- [Development validation](../reports/development-v4-validation.json)
- [Live network and injected recovery validation](../reports/network-development-v4/validation.json)
- [Full comparison data](../reports/controller-comparison.json)
- [Per-task results](results.md)
- [Portable evidence browser](../reports/index.html)
- [All 59 historical DNS failures](../reports/transport-failures-v3.json)
- [Archived v3 interpretation](../reports/archive-v3/controller-comparison.md)

The release retains v1, v2 and v3 experiments and their original public releases. The exact historical DNS root cause remains unknown; successful current requests and retry validation do not retroactively diagnose it.

## Request and source exception audit

Application operations recorded, including preflights: 1564. Failed application operations: 0. [Complete network ledger](../reports/network-audit-v4.json). These logs observe application requests, not individual TCP connection attempts. The historical DNS resolver root cause remains unknown; successful live traffic and injected retry recovery do not prove that retries caused the observed recovery.

- `capsule-0504157` A1: source audit not recorded; answer-solved=False. [Run report](../reports/runs/20261118T053006883732Z-capsule-0504157-run-A1/report.html). Changed or missing original files: `[]`.
- `capsule-0504157` A1: changed original input; answer-solved=False. [Run report](../reports/runs/20261118T053043940539Z-capsule-0504157-run-A1/report.html). Changed or missing original files: `['/code/manuscript_croco4_5.Rmd']`.
- `capsule-3262218` B1: changed original input; answer-solved=False. [Run report](../reports/runs/20261118T060115837998Z-capsule-3262218-run-B1/report.html). Changed or missing original files: `['/data/processed/d_round2access.rds', '/data/processed/d_reference.rds', '/data/processed/d_contentAnalysis.rds', '/data/processed/d_citations.rds', '/data/processed/d_repCitations.rds', '/data/processed/d_coauthors.rds']`.

[Source exception data](../reports/source-integrity-v4.json) retains absent audits separately from changed files.

Across thirty task/repetition pairs, B-only answer success occurred 0 times and A-only success 4 times; both solved 21 and neither solved 5. These are descriptive paired observations on fifteen reused tasks. [Pair-level data](../reports/paired-outcomes-v4.json).

The later [power-state incident analysis](network-incident-analysis.md) correlates all 59 v3 failure completions with sleep/background-wake transitions and retains the one successful DarkWake control. This is post-hoc association, not proof of the exact DNS mechanism.
