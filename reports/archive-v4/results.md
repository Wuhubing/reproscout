# Measured results: prepared-v4

This is a prepared-author-environment experiment on 15 official test
capsules. Author images are pre-provisioned and execution is offline. This is not
an unchanged CORE-Bench Medium score. Model and limits are recorded in the freeze.

## Complete paired comparison

| Cell | Solved capsules | Estimated model cost | Total seconds |
|---|---:|---:|---:|
| A1 | 12/15 | $0.37474 | 2197.5 |
| B1 | 10/15 | $0.50082 | 2459.7 |
| A2 | 13/15 | $0.46229 | 1725.1 |
| B2 | 11/15 | $0.50309 | 2198.5 |

Average B-minus-A solved count: **-2.0**.
All **60** planned scientific outcomes are present; no missing cells.
Retained infrastructure attempts: **1**; these do not fill scientific cells.
Total selected-outcome model cost: **$1.84094**. A receives no lessons; B receives the original frozen rules.
All-attempt cost, including infrastructure retries: **$1.84094**.
No earlier experiment run is counted in these totals. Costs exclude image
preparation, host compute, and development assistance.

## Group breakdown

| Group | A solved / attempts | B solved / attempts |
|---|---:|---:|
| Python | 8/10 | 8/10 |
| R | 17/20 | 13/20 |
| Text-labelled | 2/4 | 2/4 |
| Vision-labelled | 23/26 | 19/26 |
| Newly evaluated | 0/0 | 0/0 |
| Previously evaluated | 25/30 | 21/30 |

Counts combine two repetitions; repeats are not independent scientific tasks.
Previously evaluated capsules: 15; newly evaluated capsules: 0.
Prior exposure is disclosed rather than treating repeated evaluation as new data. The original lessons remain unchanged; controller changes were validated on development tasks before the new freeze. Task modality labels do not establish image-tool use.

## Per-task records

| Capsule | Cell | Correct questions | Solved | Model cost | Seconds | Inputs unchanged |
|---|---|---:|---|---:|---:|---|
| capsule-4180912 | A1 | 0/2 | False | $0.03159 | 687.0 | True |
| capsule-4180912 | B1 | 0/2 | False | $0.06128 | 1343.6 | True |
| capsule-1175539 | A1 | 1/1 | True | $0.01001 | 26.1 | True |
| capsule-1175539 | B1 | 1/1 | True | $0.01205 | 26.0 | True |
| capsule-0921079 | A1 | 1/1 | True | $0.00770 | 60.0 | True |
| capsule-0921079 | B1 | 1/1 | True | $0.01090 | 57.8 | True |
| capsule-1624349 | A1 | 2/2 | True | $0.01217 | 86.5 | True |
| capsule-1624349 | B1 | 2/2 | True | $0.01620 | 107.1 | True |
| capsule-9054015 | A1 | 2/2 | True | $0.02505 | 127.1 | True |
| capsule-9054015 | B1 | 1/2 | False | $0.01696 | 70.8 | True |
| capsule-7716865 | A1 | 1/1 | True | $0.04422 | 76.7 | True |
| capsule-7716865 | B1 | 1/1 | True | $0.03327 | 54.8 | True |
| capsule-0504157 | A1 | 0/1 | False | $0.03458 | 106.3 | False |
| capsule-0504157 | B1 | 0/1 | False | $0.04737 | 67.1 | True |
| capsule-8807709 | A1 | 2/2 | True | $0.01460 | 25.8 | True |
| capsule-8807709 | B1 | 2/2 | True | $0.01271 | 23.5 | True |
| capsule-2804717 | A1 | 2/2 | True | $0.05378 | 635.0 | True |
| capsule-2804717 | B1 | 2/2 | True | $0.03698 | 244.2 | True |
| capsule-3849634 | A1 | 1/1 | True | $0.02490 | 47.2 | True |
| capsule-3849634 | B1 | 1/1 | True | $0.03289 | 42.0 | True |
| capsule-1724988 | A1 | 2/2 | True | $0.02166 | 96.7 | True |
| capsule-1724988 | B1 | 2/2 | True | $0.02102 | 81.0 | True |
| capsule-9052293 | A1 | 1/1 | True | $0.00540 | 15.4 | True |
| capsule-9052293 | B1 | 1/1 | True | $0.00967 | 15.1 | True |
| capsule-2708693 | A1 | 2/2 | True | $0.03007 | 60.3 | True |
| capsule-2708693 | B1 | 0/2 | False | $0.05188 | 59.0 | True |
| capsule-4671827 | A1 | 1/1 | True | $0.02162 | 77.8 | True |
| capsule-4671827 | B1 | 1/1 | True | $0.07751 | 94.5 | True |
| capsule-3262218 | A1 | 0/1 | False | $0.03739 | 69.5 | True |
| capsule-3262218 | B1 | 0/1 | False | $0.06013 | 173.5 | False |
| capsule-4180912 | B2 | 0/2 | False | $0.03439 | 596.3 | True |
| capsule-4180912 | A2 | 0/2 | False | $0.03170 | 455.8 | True |
| capsule-1175539 | B2 | 1/1 | True | $0.00826 | 31.5 | True |
| capsule-1175539 | A2 | 1/1 | True | $0.01164 | 40.3 | True |
| capsule-0921079 | B2 | 1/1 | True | $0.00729 | 56.3 | True |
| capsule-0921079 | A2 | 1/1 | True | $0.00846 | 61.6 | True |
| capsule-1624349 | B2 | 2/2 | True | $0.02151 | 77.5 | True |
| capsule-1624349 | A2 | 2/2 | True | $0.00949 | 56.1 | True |
| capsule-9054015 | B2 | 1/2 | False | $0.03378 | 190.3 | True |
| capsule-9054015 | A2 | 2/2 | True | $0.04269 | 133.7 | True |
| capsule-7716865 | B2 | 1/1 | True | $0.04672 | 83.8 | True |
| capsule-7716865 | A2 | 1/1 | True | $0.03938 | 58.0 | True |
| capsule-0504157 | B2 | 0/1 | False | $0.04646 | 75.0 | True |
| capsule-0504157 | A2 | 1/1 | True | $0.04928 | 125.7 | True |
| capsule-8807709 | B2 | 2/2 | True | $0.01365 | 24.3 | True |
| capsule-8807709 | A2 | 2/2 | True | $0.01354 | 26.1 | True |
| capsule-2804717 | B2 | 1/2 | False | $0.04349 | 684.3 | True |
| capsule-2804717 | A2 | 0/2 | False | $0.05604 | 432.2 | True |
| capsule-3849634 | B2 | 1/1 | True | $0.01915 | 37.3 | True |
| capsule-3849634 | A2 | 1/1 | True | $0.01952 | 35.4 | True |
| capsule-1724988 | B2 | 2/2 | True | $0.02671 | 84.5 | True |
| capsule-1724988 | A2 | 2/2 | True | $0.03856 | 83.2 | True |
| capsule-9052293 | B2 | 1/1 | True | $0.00504 | 13.4 | True |
| capsule-9052293 | A2 | 1/1 | True | $0.00541 | 11.4 | True |
| capsule-2708693 | B2 | 2/2 | True | $0.05453 | 87.6 | True |
| capsule-2708693 | A2 | 2/2 | True | $0.04359 | 64.4 | True |
| capsule-4671827 | B2 | 1/1 | True | $0.10554 | 102.1 | True |
| capsule-4671827 | A2 | 1/1 | True | $0.06221 | 82.0 | True |
| capsule-3262218 | B2 | 1/1 | True | $0.03658 | 54.3 | True |
| capsule-3262218 | A2 | 1/1 | True | $0.03077 | 59.3 | True |

A missing submission or scientific execution/context/budget failure counts as unsolved, rather than
being excluded. Source integrity and answer correctness are separate properties.
Where inputs changed, the audit must be inspected before claiming faithful reproduction.

## Recovery and selection

The original eight unavailable selected images were revisited using the public
Registry authentication protocol, manifest digest verification, cached layers,
and serial pulls with bounded backoff. The original tag also worked in a control
recheck after the first recovery. The exact upstream rate-limit policy remains
unknown; do not attribute recovery conclusively to digest addressing alone.

The original size-ranked selection was extended to the proposal target of fifteen
held-out tasks before formal execution. The same five development tasks and three
lessons were retained. See selection-v2.json, recovery-v2.json, and the expanded
experiment protocol. No held-out score determined task replacement.

## Evidence and limitations

- Prepared original inputs unchanged: **58/60**; missing audits: 0.
- All referenced evidence artifact hashes match their recorded SHA-256 values.
- Formal image artifacts: **4**.
- Provisional diagnoses: `{'budget_exhausted': 6, 'solved': 46, 'output_error': 1, 'environment': 2, 'code_error': 5}`.
- Software checks, environment checks, report navigation, and release validation
  are recorded separately in reports/delivery-validation.json.
- Independent human diagnosis agreement and ten adversarial model-prompt trials
  remain unmeasured. Deterministic isolation checks are not substitutes for them.
- Two repetitions, a selected small-archive cohort, and amd64 emulation limit
  interpretation. No statistical-significance or general reproducibility claim is made.

The v0.1.0 release preserves the earlier two-task experiment. The expanded release
contains fresh runs and frozen lessons, with real failures retained. See the
portable evidence reports and exported trajectories for the underlying observations.
