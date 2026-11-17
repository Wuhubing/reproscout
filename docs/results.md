# Measured results: prepared-v2

This is a prepared-author-environment experiment on 15 official test
capsules. Author images are pre-provisioned and execution is offline. This is not
an unchanged CORE-Bench Medium score. Model and limits are recorded in the freeze.

## Complete paired comparison

| Cell | Solved capsules | Estimated model cost | Total seconds |
|---|---:|---:|---:|
| A1 | 6/15 | $0.19392 | 966.8 |
| B1 | 4/15 | $0.18476 | 1254.7 |
| A2 | 5/15 | $0.18996 | 1295.3 |
| B2 | 5/15 | $0.18686 | 1023.6 |

Average B-minus-A solved count: **-1.0**.
All **60** planned records are present; no missing cells. Total formal model
cost: **$0.75550**. A receives no lessons; B receives the original frozen rules.
No earlier prepared-v1 run is counted in these totals. Costs exclude image
preparation, host compute, and development assistance.

## Group breakdown

| Group | A solved / attempts | B solved / attempts |
|---|---:|---:|
| Python | 7/10 | 6/10 |
| R | 4/20 | 3/20 |
| Text-labelled | 2/4 | 2/4 |
| Vision-labelled | 9/26 | 7/26 |
| Newly evaluated | 10/26 | 8/26 |
| Previously evaluated | 1/4 | 1/4 |

Counts combine two repetitions; repeats are not independent scientific tasks.
The two previously evaluated capsules are explicitly separated from the thirteen
newly evaluated capsules. No lessons or agent policy were changed after their
previous outcomes were observed. Task modality labels do not establish image-tool use.

## Per-task records

| Capsule | Cell | Correct questions | Solved | Model cost | Seconds | Inputs unchanged |
|---|---|---:|---|---:|---:|---|
| capsule-4180912 | A1 | 0/2 | False | $0.01463 | 244.7 | True |
| capsule-4180912 | B1 | 0/2 | False | $0.01671 | 565.6 | True |
| capsule-1175539 | A1 | 0/1 | False | $0.00000 | 2.7 | not recorded |
| capsule-1175539 | B1 | 0/1 | False | $0.01528 | 35.1 | True |
| capsule-0921079 | A1 | 1/1 | True | $0.00684 | 53.9 | True |
| capsule-0921079 | B1 | 1/1 | True | $0.00805 | 54.8 | True |
| capsule-1624349 | A1 | 2/2 | True | $0.01146 | 58.2 | True |
| capsule-1624349 | B1 | 2/2 | True | $0.01371 | 65.9 | True |
| capsule-9054015 | A1 | 0/2 | False | $0.00952 | 58.7 | True |
| capsule-9054015 | B1 | 0/2 | False | $0.01056 | 63.3 | True |
| capsule-7716865 | A1 | 0/1 | False | $0.02784 | 45.6 | True |
| capsule-7716865 | B1 | 0/1 | False | $0.01269 | 23.8 | True |
| capsule-0504157 | A1 | 0/1 | False | $0.01287 | 28.9 | True |
| capsule-0504157 | B1 | 0/1 | False | $0.00963 | 31.1 | True |
| capsule-8807709 | A1 | 2/2 | True | $0.01384 | 25.0 | True |
| capsule-8807709 | B1 | 2/2 | True | $0.01416 | 24.7 | True |
| capsule-2804717 | A1 | 0/2 | False | $0.01602 | 212.3 | True |
| capsule-2804717 | B1 | 0/2 | False | $0.01390 | 209.2 | True |
| capsule-3849634 | A1 | 1/1 | True | $0.01601 | 30.2 | True |
| capsule-3849634 | B1 | 0/1 | False | $0.01118 | 31.8 | True |
| capsule-1724988 | A1 | 0/2 | False | $0.01732 | 74.9 | True |
| capsule-1724988 | B1 | 0/2 | False | $0.01651 | 68.1 | True |
| capsule-9052293 | A1 | 1/1 | True | $0.00439 | 13.3 | True |
| capsule-9052293 | B1 | 1/1 | True | $0.00570 | 11.3 | True |
| capsule-2708693 | A1 | 0/2 | False | $0.01428 | 26.2 | True |
| capsule-2708693 | B1 | 0/2 | False | $0.01276 | 30.0 | True |
| capsule-4671827 | A1 | 1/1 | True | $0.01797 | 64.7 | True |
| capsule-4671827 | B1 | 0/1 | False | $0.01460 | 15.5 | True |
| capsule-3262218 | A1 | 0/1 | False | $0.01091 | 27.6 | True |
| capsule-3262218 | B1 | 0/1 | False | $0.00932 | 24.5 | True |
| capsule-4180912 | B2 | 0/2 | False | $0.01331 | 284.5 | True |
| capsule-4180912 | A2 | 0/2 | False | $0.01236 | 505.9 | True |
| capsule-1175539 | B2 | 1/1 | True | $0.00814 | 27.2 | True |
| capsule-1175539 | A2 | 1/1 | True | $0.01150 | 32.7 | True |
| capsule-0921079 | B2 | 1/1 | True | $0.00987 | 59.3 | True |
| capsule-0921079 | A2 | 1/1 | True | $0.01772 | 140.2 | True |
| capsule-1624349 | B2 | 2/2 | True | $0.01536 | 62.3 | True |
| capsule-1624349 | A2 | 2/2 | True | $0.01187 | 76.5 | True |
| capsule-9054015 | B2 | 0/2 | False | $0.01050 | 61.5 | True |
| capsule-9054015 | A2 | 0/2 | False | $0.01527 | 67.6 | True |
| capsule-7716865 | B2 | 0/1 | False | $0.01272 | 24.1 | True |
| capsule-7716865 | A2 | 0/1 | False | $0.01346 | 29.6 | True |
| capsule-0504157 | B2 | 0/1 | False | $0.01608 | 37.5 | True |
| capsule-0504157 | A2 | 0/1 | False | $0.01237 | 29.9 | True |
| capsule-8807709 | B2 | 2/2 | True | $0.01897 | 26.8 | True |
| capsule-8807709 | A2 | 2/2 | True | $0.01499 | 30.9 | True |
| capsule-2804717 | B2 | 0/2 | False | $0.01285 | 209.9 | True |
| capsule-2804717 | A2 | 0/2 | False | $0.01516 | 213.4 | True |
| capsule-3849634 | B2 | 0/1 | False | $0.01174 | 27.7 | True |
| capsule-3849634 | A2 | 0/1 | False | $0.01657 | 30.9 | True |
| capsule-1724988 | B2 | 0/2 | False | $0.01303 | 67.8 | True |
| capsule-1724988 | A2 | 0/2 | False | $0.01294 | 64.5 | True |
| capsule-9052293 | B2 | 1/1 | True | $0.00636 | 16.2 | True |
| capsule-9052293 | A2 | 1/1 | True | $0.00539 | 15.2 | True |
| capsule-2708693 | B2 | 0/2 | False | $0.01298 | 29.9 | True |
| capsule-2708693 | A2 | 0/2 | False | $0.00961 | 23.9 | True |
| capsule-4671827 | B2 | 0/1 | False | $0.01476 | 70.8 | True |
| capsule-4671827 | A2 | 0/1 | False | $0.01025 | 12.0 | True |
| capsule-3262218 | B2 | 0/1 | False | $0.01019 | 18.2 | True |
| capsule-3262218 | A2 | 0/1 | False | $0.01048 | 22.3 | True |

A missing submission, execution error, context-bound stop, or budget failure
counts as unsolved rather than being excluded. Source integrity and answer correctness are separate properties.
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

- Prepared original inputs unchanged: **59/60**; missing audits: 1.
- All referenced evidence artifact hashes match their recorded SHA-256 values.
- Formal image artifacts: **9**.
- Provisional diagnoses: `{'budget_exhausted': 39, 'output_error': 1, 'solved': 20}`.
- Software checks, environment checks, report navigation, and release validation
  are recorded separately in reports/delivery-validation.json.
- Independent human diagnosis agreement and ten adversarial model-prompt trials
  remain unmeasured. Deterministic isolation checks are not substitutes for them.
- Two repetitions, a selected small-archive cohort, and amd64 emulation limit
  interpretation. No statistical-significance or general reproducibility claim is made.

The v0.1.0 release preserves the earlier two-task experiment. The expanded release
contains fresh runs and frozen lessons, with real failures retained. See the
portable evidence reports and exported trajectories for the underlying observations.

## Interpretation of the expanded comparison

A solved 6/15 and 5/15 across the two repetitions; B solved 4/15 and 5/15. Average B-minus-A solved-count change was -1.0; estimated model cost for all 60 formal attempts was $0.75550.
Across both repetitions, A solved 11/30 attempts and B solved
9/30 attempts. The original target of at least two additional solved
capsules on average was not met. These are descriptive results for the
selected cohort, not a significance test or a model-wide capability claim.

There were 39 stops at the application's conservative request-size bound.
This is a ReproScout controller limit; it is not an OpenAI context-window error.
Opaque provider reasoning fields were counted in that bound during execution.
The result therefore measures this bounded application and its frozen lessons,
including their interaction with that policy. No limit was increased after
observing held-out outcomes.

There was one zero-model-call initialization failure, preserved
as unsolved in the all-attempt primary analysis. This is an infrastructure event,
not evidence that a model could not answer the questions. In particular,
`capsule-1175539 A1` failed to create the container directory `/tmp`; it made no
model request and incurred zero returned model usage. The experiment did not
replace or rerun that cell. An A/B difference involving that cell must not be
attributed solely to the lesson intervention.

A future study should validate a revised request-bound policy on development
cases, improve startup-failure diagnostics, and freeze a separate experiment
before collecting new held-out outcomes. None of those changes is silently
included in this comparison. Independent human diagnosis agreement and adversarial
prompt robustness still require separate measurements.
