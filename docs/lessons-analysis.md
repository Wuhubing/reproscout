# V6: what constraints fix, and what they do not

A scored 24/30 and constrained B 20/30 in sixty frozen scientific cells. B changes
execution capabilities and output validation, so this is not a pure lesson-text
ablation. V5's B 26/30 included scientific reimplementations. A higher raw score is
not proof of faithful reproduction, and more abstention is not improved accuracy.

## Separate evaluations

| Measure | A | B |
|---|---:|---:|
| Answer solved | 24/30 | 20/30 |
| Strictly typed submissions | 26/30 | 29/30 |
| Accepted type violations | 2 | 0 |
| Missing reports | 2 | 1 |
| Runs containing nulls | 0 | 8 |
| Solved + verified original execution | 0/30 | 20/30 |
| Call-cap failures | 2 | 1 |

A execution statuses: `{'unverified': 30}`. B statuses:
`{'verified_original_execution': 22, 'unverified': 7, 'violated': 1}`. The automatic audit has asymmetric observability:
A's unrestricted shell cannot establish provenance merely by leaving original
hashes intact. Its unverified count is not a measured failure rate. The joint count
is a conservative instrumented intersection, not a universal fidelity ranking.

## Mechanism and limits

B has no arbitrary code-writing or shell capability. Every dispatched author file
must match its frozen inventory and all original inputs are hashed before execution.
Controller wrappers execute whole original notebooks or extract all R Markdown
chunks using knitr; they do not accept model-authored scientific fragments. This
is analytical-block execution when rendering fails, not proof of full-document
rendering or equivalent knitting semantics under every author chunk option.

The submission validator rejects wrong numeric types rather than coercing them.
Non-null citations must come from successful execution stdout or newly generated
outputs. Output provenance does not prove the selected figure, population, metric,
units or interpretation is correct. Original programs can also be scientifically
wrong. Read the [execution audit](../reports/controlled-execution-audit-v6.json),
[semantic review](../reports/semantic-review-v6.json) and answer scores separately.
The semantic review is assistant-assisted artifact inspection, not independent
human agreement or a complete scientific audit.

## Why A declined previously

[All seven changed A pairs](baseline-decline-v5.md) explain the v4 25/30 to v5 20/30
movement: six regressions, one gain, nineteen successes in both and four failures
in both. Several regressions already had adequate output but selected the wrong
quantity or never submitted. Others rewrote scientific calculations. The same A
prompt/tools/configuration were used; sampling, execution choices and time remain
confounders. B lessons were never supplied to A. The v6 parity report verifies that
the baseline's model-facing prompt and tool schemas still match v5 exactly.

## Development and exposure

The gate was specified before ten new training outcomes: all B reports, types,
provenance and original hashes; at least two verified B successes; software and
runtime boundary checks. B achieved three. A scored four, but its additional
notebook success replaced a loader in memory. One infrastructure setup failure and
an initial synthetic plotting-probe failure remain retained. The fixture was fixed
without changing the scientific candidate. No acceptance threshold changed.

All fifteen formal tasks were exposed before this revision. No fresh held-out,
significance, or unrestricted benchmark claim applies. All failures remain final.
A future study should use an unexposed cohort and independent semantic annotations;
neither is claimed here.

[Focused B follow-up](controlled-followup-v6.md) · [Protocol](fidelity-protocol-v6.md) · [Development](fidelity-development-v6.md) ·
[Full comparison](controller-comparison.md) · [Results](results.md)

## Separate artifact interpretation review

The additional review inspected each accepted B question citation and all thirty A
visible command sequences. It is assistant-assisted, not independent human
agreement or a complete audit of scientific validity. It does not change scores.

| B question-level evidence status | Count |
|---|---:|
| abstained | 11 |
| supported_within_visible_evidence | 27 |
| unsupported_or_contradicted | 4 |
| no_submission | 2 |

Another B example, `capsule-1175539` repeat 2, scores correctly with SCZ but cites an adjusted regression coefficient instead of group medians. This is marked unsupported even though the primary scorer accepts the answer.

These question counts have a different denominator from the thirty run-level
successes. Supported means the visible cited artifact and inspected context support
the submitted value; it does not certify all scientific assumptions. A table citation
for a visual question can support content without proving compliance with the
requested visual method. Null and missing answers do not count as supported.

A concrete counterexample is B `capsule-7716865` repeat 1: original R chunks
successfully generate the requested table, but B selects 0.77 from the Original
section rather than 1.31 from Recalculated. Type and provenance checks both pass;
semantic support fails. This failure remains unchanged. B `capsule-1624349` repeat 1
uses the generated information-gain table for a figure question; the feature name is
supported, but visual-method compliance is not certified.

B `capsule-3262218` repeat 2 exposes a wrapper limitation: all original chunks produce the requested count, then `render_appendix()` fails because extracted execution lacks the active R Markdown context. The controller rejects the count from that failed execution and accepts null. Thus original-file dispatch is not equivalent to complete knitting semantics, and the stricter success rule can discard partial valid output. B `capsule-2708693` repeat 2 successfully executes all chunks but reaches the call cap without a report; its automatic unverified status reflects the missing validated submission, not absence of successful execution.

Conversely, B `capsule-4671827` repeat 1 selects the correct generated
Semantic-based/Label-based plot; A cites a different Greedy/Combination source cell.
On `capsule-2708693` repeat 1, original-chunk table headers resolve k=21 versus n=620.
These are inspected trajectory mechanisms, not causal effect estimates.

The original-input audit is **59 unchanged, 1 changed**, not 60 unchanged. B `capsule-3262218` repeat 2 calls the original preprocessing script, which regenerates six inventoried processed RDS files; the automatic `violated` status is retained. No model-authored scientific command is dispatched, but original-code execution itself can modify inputs. All 506 host freeze hashes remain unchanged; that is a different check from in-container input integrity.

Failed host/API operations are distinct from author-code dependencies inside the
frozen isolated container. The manuscript's request to github.com, pandoc failures
and scientific execution timeouts remain blocked/failed scientific outcomes. They
are neither successful reproductions nor silently retried infrastructure cells.

The manual A review observes explicit additional/reimplemented scientific calculations in 14/30 trajectories. This is a narrow observation count, not a measured overall fidelity failure rate: source-only inference, authored placeholder outputs and incomplete executions are additional distinct concerns. The automatic A status remains unverified.

V5-to-v6 A transitions: `{'both_failure': 4, 'both_success': 18, 'regression': 2, 'gain': 6}`. See [all paired A transitions](baseline-transition-v6.md). The earlier six-regression/one-gain v4-to-v5 analysis is retained separately. Neither transition analysis attributes A movement to lessons that A did not receive.

[Question-level review and A observations](../reports/semantic-review-v6.json) · [Execution boundary audit](../reports/controlled-execution-audit-v6.json)

[What A and B mean, and why B scores lower](ab-interpretation-v6.md)
