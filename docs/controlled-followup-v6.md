# Previously problematic B trajectories under v6 constraints

These four exposed task/repetition pairs were selected previously, not a new independent test set. Primary scores remain unchanged. The v6 workflow changes B capabilities and typing; it is not a lesson-only comparison.

## capsule-0504157, repetition 2

| Run | Answer solved | Calls | Values | Execution assessment |
|---|---|---:|---|---|
| [v5 B](../reports/runs/20261118T093113458234Z-capsule-0504157-run-B2/report.html) | True | 13 | `{"q1": "1000"}` | Not instrumented in v5 |
| [v6 A](../reports/runs/20261118T183437443119Z-capsule-0504157-run-A2/report.html) | True | 12 | `{"q1": 1000}` | unverified |
| [v6 B](../reports/runs/20261118T183322151263Z-capsule-0504157-run-B2/report.html) | False | 16 | `{"q1": null}` | unverified |

Original manuscript execution stops at an unavailable github.com dependency. B attempts a numeric 1000 answer from source citations; provenance enforcement rejects it and retains that rejected payload. The accepted report is null with the actual execution error. Unlike v5 B repeat 2, it neither rebuilds the EC aggregation while omitting preprocessing nor accepts string 1000. This is a preserved reproduction failure and reduced raw score, not a faithful-success claim.

## capsule-2708693, repetition 1

| Run | Answer solved | Calls | Values | Execution assessment |
|---|---|---:|---|---|
| [v5 B](../reports/runs/20261118T085150930191Z-capsule-2708693-run-B1/report.html) | True | 14 | `{"q1": 81, "q2": 620}` | Not instrumented in v5 |
| [v6 A](../reports/runs/20261118T174333272267Z-capsule-2708693-run-A1/report.html) | True | 15 | `{"q1": 81, "q2": 620}` | unverified |
| [v6 B](../reports/runs/20261118T174434521537Z-capsule-2708693-run-B1/report.html) | True | 15 | `{"q1": 81, "q2": 620}` | verified_original_execution |

B runs all original manuscript R chunks and cites the emitted Table 1 and Table 3 HTML, with verified execution provenance and numeric 81/620. The Table 3 header explicitly distinguishes k=21 from n=620. Unlike v5 B targeted arithmetic, no model-authored metaprop calculation is dispatched. This is successful analytical-block execution, not a claim of full PDF rendering.

## capsule-9054015, repetition 1

| Run | Answer solved | Calls | Values | Execution assessment |
|---|---|---:|---|---|
| [v5 B](../reports/runs/20261118T082236563632Z-capsule-9054015-run-B1/report.html) | True | 12 | `{"q1": 90, "q2": 1.24}` | Not instrumented in v5 |
| [v6 A](../reports/runs/20261118T171757649766Z-capsule-9054015-run-A1/report.html) | True | 9 | `{"q1": "90%", "q2": 1.24}` | unverified |
| [v6 B](../reports/runs/20261118T172003850773Z-capsule-9054015-run-B1/report.html) | True | 11 | `{"q1": 90, "q2": 1.24}` | verified_original_execution |

B executes the original pancancer_calculation.R and cites its generated sensitivity figure and probability table. The black 90% line is highest at 1.0% prevalence; numeric 90 and 1.24 are accepted with execution provenance. No model-authored CD formula is executed, unlike v5 B repeat 1. A still submits a percent string despite passing the primary scorer.

## capsule-9054015, repetition 2

| Run | Answer solved | Calls | Values | Execution assessment |
|---|---|---:|---|---|
| [v5 B](../reports/runs/20261118T092341047794Z-capsule-9054015-run-B2/report.html) | True | 9 | `{"q1": 90, "q2": 1.24}` | Not instrumented in v5 |
| [v6 A](../reports/runs/20261118T182803613038Z-capsule-9054015-run-A2/report.html) | True | 12 | `{"q1": "90%", "q2": "1.24%"}` | unverified |
| [v6 B](../reports/runs/20261118T182606504182Z-capsule-9054015-run-B2/report.html) | True | 13 | `{"q1": 90, "q2": 1.24}` | verified_original_execution |

B preserves the already-valid v5 route: original pancancer_calculation.R generates the correct sensitivity figure and table. Cited figure shows black 90% as highest at 1.0% prevalence, and the generated breast age-50 row gives 1.24. Both values are numbers with successful-original-execution provenance; no replacement CD formula is executed.

[Previous detailed trajectory analysis](adverse-pair-followup-v5.md) · [Full comparison](controller-comparison.md) · [Semantic review](../reports/semantic-review-v6.json)
