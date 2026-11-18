# Additional A baseline transitions: v5 to v6

This is descriptive trajectory analysis, not a causal effect of B lessons. A retains its v5 model-facing prompt and tool schemas. The original v4-to-v5 decline analysis remains unchanged.

| Transition | Pairs |
|---|---:|
| both_failure | 4 |
| both_success | 18 |
| regression | 2 |
| gain | 6 |

## capsule-7716865 repeat 1: regression

V5 `20261118T082506943877Z-capsule-7716865-run-A1` → V6 `20261118T172126858315Z-capsule-7716865-run-A1`.

After manuscript rendering fails, writes /tmp/compute.R and repeatedly reimplements power calculations with WebPower. The final calculation subsets raw regulation rows to ANOVA and reports 1.73. This is evidence of a newly assembled subset/calculation, not the full original manuscript preprocessing and output. It submits at 17 calls, so the failure is not a no-submission call-cap event.

## capsule-0504157 repeat 1: gain

V5 `20261118T082740925747Z-capsule-0504157-run-A1` → V6 `20261118T172405407159Z-capsule-0504157-run-A1`.

After original manuscript render fails, builds new R aggregation from ratingData5, reconstructs USval, computes EC differences and recodes presentation times. Reports numeric 1000 from that targeted computation. Correct scoring does not establish the full original preprocessing or requested figure reproduction.

## capsule-2804717 repeat 1: gain

V5 `20261118T083053205159Z-capsule-2804717-run-A1` → V6 `20261118T172724418255Z-capsule-2804717-run-A1`.

Attempts render and knit, inspects plotMultipleTimeSeries defaults and runs an additional getDynamicFollNet call. It then writes a replacement HTML page containing asserted figure answers. Time and TS#1 score correctly, but citations are source/default-function text and the HTML is a model-authored placeholder, not a completed notebook rendering. No replaced scientific formula is visible; output fabrication and incomplete execution remain separate fidelity concerns.

## capsule-2708693 repeat 1: gain

V5 `20261118T085034431301Z-capsule-2708693-run-A1` → V6 `20261118T174333272267Z-capsule-2708693-run-A1`.

After render/pandoc failure and shell-expansion mistakes, calculates discipline counts and reconstructs a metaprop analysis from selected raw columns. Submits 81/620 at 15 calls. Correct answers arise from targeted model-authored analysis rather than the original full manuscript tables.

## capsule-4671827 repeat 1: regression

V5 `20261118T085245071914Z-capsule-4671827-run-A1` → V6 `20261118T174707547955Z-capsule-4671827-run-A1`.

Executes original notebook using --allow-errors, then searches source/HTML and submits Combination based on source cell 7 lines 19–20 rather than a generated timing figure. No rewritten scientific calculation observed; the unsuccessful answer was submitted at 12 calls, so it is an interpretation/evidence-selection failure rather than call-cap exhaustion.

## capsule-7716865 repeat 2: gain

V5 `20261118T092835302317Z-capsule-7716865-run-A2` → V6 `20261118T183151942876Z-capsule-7716865-run-A2`.

After render failure, repeatedly reimplements WebPower branches and nonpilot summaries in new R code. Final output gives the requested mean 1.31, but also copies mean rows into rows labeled Median. Correct scoring of the requested mean does not validate this reconstructed table or full original pipeline.

## capsule-0504157 repeat 2: gain

V5 `20261118T093218449941Z-capsule-0504157-run-A2` → V6 `20261118T183437443119Z-capsule-0504157-run-A2`.

After manuscript network failure, writes a new R pipeline with explicit participant exclusions, US-valence recoding, reshape, EC differences and presentation-time means. Numeric 1000 scores correctly but is derived from the new calculation, not the original completed manuscript/figure. Inclusion of some exclusions does not establish full preprocessing equivalence.

## capsule-1724988 repeat 2: gain

V5 `20261118T095335368824Z-capsule-1724988-run-A2` → V6 `20261118T185120419430Z-capsule-1724988-run-A2`.

Runs all four original R scripts, then recomputes participant-filtered LSS1 and LSS2 medians in new R code and cites that output. Walk/Search is interpreted correctly this time, unlike the prior v5 repeat-2 contradiction, but this is an additional scientific calculation rather than figure evidence.

All thirty manual A observations and paired scores are available in [the JSON report](../reports/baseline-transition-v6.json). Explicit model-authored calculations are separated from source edits; intact originals alone do not establish fidelity.
