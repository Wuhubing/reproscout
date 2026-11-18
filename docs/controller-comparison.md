# V6: scoring and controlled scientific execution

All sixty scientific cells completed under one unchanged freeze. V3 remains infrastructure-invalid; its score/time are not scientific or efficiency evidence. V6 changes B tools and submission enforcement, not only lesson text. A retains the original unrestricted baseline.

| Metric | v2 | v3 | v4 | v5 | v6 |
|---|---:|---:|---:|---:|---:|
| Answer solved / 60 | 20 | 1 | 46 | 46 | 44 |
| A solved / 30 | 11 | 0 | 25 | 20 | 24 |
| B solved / 30 | 9 | 1 | 21 | 26 | 20 |
| Retained attempts | 60 | 60 | 61 | 60 | 60 |
| Infrastructure failures | 1 | 59 | 1 | 0 | 0 |
| Original hashes unchanged / changed / missing | 59 / 0 / 1 | 60 / 0 / 0 | 58 / 2 / 1 | 60 / 0 / 0 | 59 / 1 / 0 |
| Old byte-bound stops | 39 | 0 | 0 | 0 | 0 |
| Native-count failures | 0 | 59 | 0 | 0 | 0 |
| 20-call stops | 0 | 0 | 8 | 4 | 3 |
| Generations | 423 | 39 | 721 | 664 | 694 |
| Sample minutes | 75.67 | 23.69 | 143.07 | 130.39 | 133.87 |
| Calendar minutes | 76.93 | 57.03 | 147.75 | 134.55 | 138.03 |
| Estimated model cost USD | 0.7555 | 0.05651 | 1.84094 | 1.50081 | 1.64149 |

## Separate outcomes

| Outcome | A | B |
|---|---:|---:|
| answer_solved | 24 | 20 |
| typed_submissions | 26 | 29 |
| type_noncompliant_submissions | 2 | 0 |
| missing_submissions | 2 | 1 |
| null_answers | 0 | 11 |
| runs_with_nulls | 0 | 8 |
| solved_and_verified_execution | 0 | 20 |
| call_cap_failures | 2 | 1 |
| model_calls | 347 | 347 |
| sample_seconds | 4896.230562124867 | 3135.9624087064294 |
| estimated_cost_usd | 0.78367635 | 0.85781145 |

Execution fidelity statuses: A `{'unverified': 30}`; B `{'verified_original_execution': 22, 'unverified': 7, 'violated': 1}`.

**Do not interpret A unverified as a zero faithful-reproduction rate.** A has unrestricted commands and lacks B's execution ledger. Verified execution means original-file dispatch, input integrity and current-output provenance; it does not prove complete experimental coverage or semantic support. A correct answer, a typed answer, an intact source file and a faithful explanation are distinct properties. Nulls are retained failures, not improved accuracy.

All 60 attempts remain available. Application operations including preflights: 1508, failed: 0. Native input counts match on 694/694 generations. Rejected controlled operations/submissions: 4. Costs exclude host, image and development work and are usage estimates, not invoices.

## Interpretation and evidence

This is a test-informed regression study on fifteen exposed tasks, each repeated twice. No fresh held-out generalization or significance claim applies. Cross-version A movement reflects different trajectories and sampling/time effects, not a treatment delivered to A. See the six-regression/one-gain analysis. Scientific failures are final; infrastructure attempts never satisfy a cell.

- [A decline analysis](baseline-decline-v5.md)
- [Frozen fidelity protocol](fidelity-protocol-v6.md)
- [Development gate](../reports/development-v6-validation.json)
- [All fidelity outcomes](../reports/fidelity-outcomes-v6.json)
- [Complete results](results.md)
- [Evidence app](../reports/index.html)
- [Previous v5 report](../reports/archive-v5/controller-comparison.md)

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
