# Measured results: prepared-v3

This is a prepared-author-environment experiment on 15 official test
capsules. Author images are pre-provisioned and execution is offline. This is not
an unchanged CORE-Bench Medium score. Model and limits are recorded in the freeze.

**Experiment status: complete attempt matrix; lesson-effect comparison inconclusive because of host-side DNS failures.**

59/60 attempts failed during host-side DNS resolution for the native count request;
55 made no model generation. The +0.5 arithmetic B-minus-A difference is not an
interpretable lesson-effect result. See [full cross-version comparison](controller-comparison.md).

## Complete paired comparison

| Cell | Solved capsules | Estimated model cost | Total seconds |
|---|---:|---:|---:|
| A1 | 0/15 | $0.03318 | 936.0 |
| B1 | 1/15 | $0.02109 | 204.4 |
| A2 | 0/15 | $0.00224 | 213.3 |
| B2 | 0/15 | $0.00000 | 67.5 |

Average B-minus-A solved count: **+0.5**.
All **60** planned records are present; no missing cells. Total formal model
cost: **$0.05651**. A receives no lessons; B receives the original frozen rules.
No earlier experiment run is counted in these totals. Costs exclude image
preparation, host compute, and development assistance.

## Group breakdown

| Group | A solved / attempts | B solved / attempts |
|---|---:|---:|
| Python | 0/10 | 0/10 |
| R | 0/20 | 1/20 |
| Text-labelled | 0/4 | 0/4 |
| Vision-labelled | 0/26 | 1/26 |
| Newly evaluated | 0/0 | 0/0 |
| Previously evaluated | 0/30 | 1/30 |

Counts combine two repetitions; repeats are not independent scientific tasks.
Previously evaluated capsules: 15; newly evaluated capsules: 0.
Prior exposure is disclosed rather than treating repeated evaluation as new data. No lessons or agent policy were changed after their
previous outcomes were observed. Task modality labels do not establish image-tool use.

## Per-task records

| Capsule | Cell | Correct questions | Solved | Model cost | Seconds | Inputs unchanged |
|---|---|---:|---|---:|---:|---|
| capsule-4180912 | A1 | 0/2 | False | $0.02851 | 803.7 | True |
| capsule-4180912 | B1 | 0/2 | False | $0.00000 | 3.1 | True |
| capsule-1175539 | A1 | 0/1 | False | $0.00000 | 4.7 | True |
| capsule-1175539 | B1 | 1/1 | True | $0.01547 | 58.7 | True |
| capsule-0921079 | A1 | 0/1 | False | $0.00468 | 73.5 | True |
| capsule-0921079 | B1 | 0/1 | False | $0.00562 | 83.4 | True |
| capsule-1624349 | A1 | 0/2 | False | $0.00000 | 3.6 | True |
| capsule-1624349 | B1 | 0/2 | False | $0.00000 | 5.5 | True |
| capsule-9054015 | A1 | 0/2 | False | $0.00000 | 4.5 | True |
| capsule-9054015 | B1 | 0/2 | False | $0.00000 | 5.3 | True |
| capsule-7716865 | A1 | 0/1 | False | $0.00000 | 4.4 | True |
| capsule-7716865 | B1 | 0/1 | False | $0.00000 | 5.7 | True |
| capsule-0504157 | A1 | 0/1 | False | $0.00000 | 3.8 | True |
| capsule-0504157 | B1 | 0/1 | False | $0.00000 | 3.6 | True |
| capsule-8807709 | A1 | 0/2 | False | $0.00000 | 5.2 | True |
| capsule-8807709 | B1 | 0/2 | False | $0.00000 | 4.9 | True |
| capsule-2804717 | A1 | 0/2 | False | $0.00000 | 4.4 | True |
| capsule-2804717 | B1 | 0/2 | False | $0.00000 | 5.6 | True |
| capsule-3849634 | A1 | 0/1 | False | $0.00000 | 4.2 | True |
| capsule-3849634 | B1 | 0/1 | False | $0.00000 | 2.9 | True |
| capsule-1724988 | A1 | 0/2 | False | $0.00000 | 4.6 | True |
| capsule-1724988 | B1 | 0/2 | False | $0.00000 | 4.7 | True |
| capsule-9052293 | A1 | 0/1 | False | $0.00000 | 5.1 | True |
| capsule-9052293 | B1 | 0/1 | False | $0.00000 | 5.0 | True |
| capsule-2708693 | A1 | 0/2 | False | $0.00000 | 4.7 | True |
| capsule-2708693 | B1 | 0/2 | False | $0.00000 | 4.5 | True |
| capsule-4671827 | A1 | 0/1 | False | $0.00000 | 3.8 | True |
| capsule-4671827 | B1 | 0/1 | False | $0.00000 | 5.7 | True |
| capsule-3262218 | A1 | 0/1 | False | $0.00000 | 5.9 | True |
| capsule-3262218 | B1 | 0/1 | False | $0.00000 | 5.6 | True |
| capsule-4180912 | B2 | 0/2 | False | $0.00000 | 4.9 | True |
| capsule-4180912 | A2 | 0/2 | False | $0.00000 | 5.5 | True |
| capsule-1175539 | B2 | 0/1 | False | $0.00000 | 5.1 | True |
| capsule-1175539 | A2 | 0/1 | False | $0.00224 | 88.8 | True |
| capsule-0921079 | B2 | 0/1 | False | $0.00000 | 3.3 | True |
| capsule-0921079 | A2 | 0/1 | False | $0.00000 | 4.3 | True |
| capsule-1624349 | B2 | 0/2 | False | $0.00000 | 4.9 | True |
| capsule-1624349 | A2 | 0/2 | False | $0.00000 | 4.9 | True |
| capsule-9054015 | B2 | 0/2 | False | $0.00000 | 4.4 | True |
| capsule-9054015 | A2 | 0/2 | False | $0.00000 | 3.3 | True |
| capsule-7716865 | B2 | 0/1 | False | $0.00000 | 5.8 | True |
| capsule-7716865 | A2 | 0/1 | False | $0.00000 | 4.7 | True |
| capsule-0504157 | B2 | 0/1 | False | $0.00000 | 5.0 | True |
| capsule-0504157 | A2 | 0/1 | False | $0.00000 | 4.9 | True |
| capsule-8807709 | B2 | 0/2 | False | $0.00000 | 5.9 | True |
| capsule-8807709 | A2 | 0/2 | False | $0.00000 | 3.5 | True |
| capsule-2804717 | B2 | 0/2 | False | $0.00000 | 3.5 | True |
| capsule-2804717 | A2 | 0/2 | False | $0.00000 | 66.4 | True |
| capsule-3849634 | B2 | 0/1 | False | $0.00000 | 3.4 | True |
| capsule-3849634 | A2 | 0/1 | False | $0.00000 | 3.7 | True |
| capsule-1724988 | B2 | 0/2 | False | $0.00000 | 2.8 | True |
| capsule-1724988 | A2 | 0/2 | False | $0.00000 | 3.3 | True |
| capsule-9052293 | B2 | 0/1 | False | $0.00000 | 3.8 | True |
| capsule-9052293 | A2 | 0/1 | False | $0.00000 | 5.8 | True |
| capsule-2708693 | B2 | 0/2 | False | $0.00000 | 5.1 | True |
| capsule-2708693 | A2 | 0/2 | False | $0.00000 | 4.9 | True |
| capsule-4671827 | B2 | 0/1 | False | $0.00000 | 6.3 | True |
| capsule-4671827 | A2 | 0/1 | False | $0.00000 | 5.1 | True |
| capsule-3262218 | B2 | 0/1 | False | $0.00000 | 3.3 | True |
| capsule-3262218 | A2 | 0/1 | False | $0.00000 | 4.2 | True |

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

- Prepared original inputs unchanged: **60/60**; missing audits: 0.
- All referenced evidence artifact hashes match their recorded SHA-256 values.
- Formal image artifacts: **0**.
- Provisional diagnoses: `{'budget_exhausted': 1, 'output_error': 58, 'solved': 1}`.
- Software checks, environment checks, report navigation, and release validation
  are recorded separately in reports/delivery-validation.json.
- Independent human diagnosis agreement and ten adversarial model-prompt trials
  remain unmeasured. Deterministic isolation checks are not substitutes for them.
- Two repetitions, a selected small-archive cohort, and amd64 emulation limit
  interpretation. No statistical-significance or general reproducibility claim is made.

The v0.1.0 release preserves the earlier two-task experiment. The expanded release
contains fresh runs and frozen lessons, with real failures retained. See the
portable evidence reports and exported trajectories for the underlying observations.

## Interpretation

All sixty frozen attempts are present, with no mid-run change, outcome replacement,
or silent rerun. In prepared-v3, 59 attempts encountered `APIConnectionError` caused
by `[Errno 8] nodename nor servname provided, or not known` while counting input.
This is host-side name-resolution failure before any HTTP response. It is not
an observed 429, quota exhaustion, authentication rejection, or scientific-code failure.
Of those attempts, 55 made no model generation. The other four stopped after
some model/tool activity. The sole completed successful attempt was capsule-1175539 B1.

The frozen no-retry policy refused generation when counting failed. This was the
specified behavior, but it meant the completed run matrix did not produce a useful
lesson-effect comparison. The arithmetic average B-minus-A solved-count difference
is +0.5, compared with -1.0 before; **this is not evidence that lessons improved**.
Network failure dominates the new denominator. Do not report a conditional success
rate on the tiny reachable subset as a replacement primary result.

The repair's accounting mechanism did work on the requests that reached the API:
39/39 native input counts matched returned input usage exactly, eight generations
continued beyond the historical byte bound, and the largest observed input was
13,296 tokens. No measured-token cap or monetary admission limit was reached.
These observations validate those calls, not service reliability across the cohort.
Zero new context stops must be read together with 59 DNS failures; they are not a
standalone claim that the overall application became more reliable.

All sixty new input audits were unchanged, but 55 of those attempts had no model
call. This is not an improvement in scientific fidelity over the previous study.
Answer correctness, source integrity, and semantic evidence support remain distinct.
The development B notebook data-loader edit remains documented separately.

Lower model cost and recorded runtime mostly reflect early refusals and do not
establish a speedup or better cost-effectiveness. Costs are estimates from returned
usage, not billing receipts; they exclude development, host compute, and preparation.
Recorded sample timers and the calendar interval measure different quantities.
The latter includes gaps between attempts and must not be called CPU time.

A single post-run native-count connectivity probe succeeded on November 17, 2026
(New York time). It made no model generation and changed no experimental result.
This establishes connectivity at that later instant, not the cause or repair of
the earlier DNS failures. The record is linked below.

All fifteen official test tasks were previously evaluated. This is an iterative
repair study on a reused cohort. Any future network-resilience change needs its own
development validation, freeze, and complete experiment; it is not folded into v3.
The current delivery preserves the failed experiment rather than selecting replacements.

## Evidence

- [Machine-readable comparison](../reports/controller-comparison.json)
- [All 59 transport failure records](../reports/transport-failures-v3.json)
- [Post-run connectivity diagnostic](../reports/post-run-connectivity-v3.json)
- [Old controller token audit](../reports/controller-v2-analysis.json)
- [Development validation and source violation](../reports/development-v3-validation.json)
- [Execution freeze](../experiments/prepared-v3/freeze.json)
- [Complete per-run results](results.md)
