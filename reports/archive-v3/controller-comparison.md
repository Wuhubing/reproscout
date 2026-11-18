# Controller, reliability, integrity, time and cost comparison

**Experiment status: complete attempt matrix; lesson-effect comparison inconclusive because of host-side DNS failures.**

| Metric | prepared-v2 | prepared-v3 |
|---|---:|---:|
| Formal attempts / unique tasks | 60 / 15 | 60 / 15 |
| A answer-solved, both repetitions | 11/30 (36.7%) | 0/30 (0.0%) |
| B answer-solved, both repetitions | 9/30 (30.0%) | 1/30 (3.3%) |
| All answer-solved attempts | 20/60 (33.3%) | 1/60 (1.7%) |
| Answer-solved with unchanged prepared inputs | 20/60 | 1/60 |
| Context-admission stops | 39 byte-proxy stops | 0 measured-token stops |
| Count-request DNS failures | Not applicable: no native counter | 59 |
| Other pre-model startup failures | 1 | 0 |
| Zero-model-call attempts | 1 | 55 |
| Source audits unchanged / changed / absent | 59 / 0 / 1 | 60 / 0 / 0 |
| Model generations | 423 | 39 |
| Sum of recorded sample runtime | 4540.40 s (75.67 min) | 1421.20 s (23.69 min) |
| Calendar interval, first start to last completion | 76.93 min | 57.03 min |
| Estimated returned model-usage cost | $0.75550 | $0.05651 |

## Per-repetition outcomes

| Condition / repetition | prepared-v2 solved | prepared-v3 solved | v3 solved with unchanged inputs |
|---|---:|---:|---:|
| A1 | 6/15 | 0/15 | 0/15 |
| B1 | 4/15 | 1/15 | 1/15 |
| A2 | 5/15 | 0/15 | 0/15 |
| B2 | 5/15 | 0/15 | 0/15 |

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
