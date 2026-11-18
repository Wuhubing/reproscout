# Why the first lessons comparison did not improve

## What prepared-v2 actually established

A solved 6/15 and 5/15 tasks; B solved 4/15 and 5/15. The average solved-count
change was -1. Across thirty task/repetition pairs, nine were solved by both
conditions, two only by A, none only by B, and nineteen by neither. Both discordant
pairs occurred in repetition one: capsule-3849634 and capsule-4671827. The second
repetition had equal solved counts. This is too small and variable to establish
that lessons generally help or harm.

Most unsuccessful attempts never submitted a final scored report: 39 stopped at
the controller's request-size guard, and one failed before a model call. There
were 18 controller stops in A and 21 in B. These outcomes evaluate the bounded
application, not an unconstrained model or the scientific feasibility of each task.
The startup failure also prevents a clean attribution of every outcome to lessons.

## Measured controller failure

[The complete token audit](../reports/controller-v2-analysis.json) reconstructs
all 39 stopped conversations, including the unchanged tool schemas, and calls
OpenAI's native input-token counting endpoint. It does not generate answers or
rerun the tasks.

- Historical byte bounds ranged from 60,509 to 77,068; median 63,999.
- Actual native input counts ranged from 6,452 to 17,838; median 9,090.
- Median encrypted reasoning payload size was 16,344 bytes.
- Subtracting only opaque payload bytes would put 37 of 39 reconstructed requests
  below the old numerical threshold, but that is not the chosen implementation.
- All 39 requests fit the repaired policy: actual input tokens plus a 2,048-token
  margin, under an input cap of 60,000. Maximum output is reserved separately.

The old byte proxy counted encrypted reasoning as ordinary text and mixed context
admission with a deliberately loose cost bound. This prematurely censored the
agent loop. The repair preserves encrypted reasoning for the model and measures
the full request instead of deleting context or merely increasing a byte limit.
That all requests now fit does **not** establish that all 39 tasks would be solved;
only a fresh frozen rerun can measure continuation outcomes.

## Why lessons may still fail after that repair

The following are mechanism hypotheses, distinguished from measured outcomes:

1. **L1 changes efficiency, not data availability.** Stopping an offline data search
   earlier can save calls and cost, but it cannot create missing scientific inputs.
   The development validation illustrates this: capsule-4098236 submitted unsolved
   results in both conditions, using ten calls in A and seven in B.
2. **L2 applies to a particular workflow.** Structured notebook-output inspection
   can help with excessive source dumps. Rendering or executing an entire notebook
   can also add work when a narrower computation suffices. The correct balance
   depends on the task, and a broad rule is not a universally beneficial policy.
3. **L3 is a narrow robustness rule.** Discovering instruction filenames can avoid
   a failed shell chain; this does not necessarily change final numerical answers.
4. **Extra prompt content consumes some budget and changes actions.** B's lesson
   text adds request content, but differing subsequent actions also affect growth.
   The two discordant pairs do not isolate prompt length as their cause. Do not
   claim that simply appending lessons caused every extra controller stop.
5. **Five development tasks provide limited coverage.** The three manually curated
   rules cover selected failures, not every language, plotting task, dependency,
   or algorithmic obstacle. They are not an autonomous learned reproduction policy.

## Development result after repairing the controller

The ten-run development matrix completed before the formal freeze. A and B each
answered 4/5 training tasks correctly. A had 4/5 answer-solved attempts with
unchanged prepared inputs; B had 3/5. All ten native-counting paths worked, and
nine source audits were unchanged. The extra startup attempt remains recorded
separately and is not presented as a successful validation run.

On capsule-0940461, A completed in ten model calls without changing prepared
inputs. B used fifteen calls and replaced the original seaborn network data
loader with sklearn data in `/code/my_datasets.py`. Its correct answers therefore
do not establish faithful reproduction under the unchanged-input policy. This
is a concrete limit of relying on a textual instruction alone. It does not show
that L2 caused the edit, because the two trajectories also differ stochastically.
The original prompts and tool permissions are kept for the formal comparison;
source-integrity flags and the secondary metric expose such behavior explicitly.

[Development validation evidence](../reports/development-v3-validation.json)
contains every run ID, accounting check, source-audit flag, and retained
initialization/validation failure. The gate establishes correct request admission
and usage accounting, not universal scientific correctness or source fidelity.

## Repair evaluation design

The [prepared-v3 protocol](controller-repair-protocol.md) keeps the original model,
scientific inputs, task selection, tools, scoring, lessons, and primary execution
budgets. It repairs native request accounting and a deterministic validation probe.
All five existing training tasks receive A and B before the new freeze; failed
preflight attempts remain recorded. The formal matrix is fifteen tasks times two
conditions times two repetitions, with no score-based replacements.

All fifteen official test tasks are now previously evaluated. The new controller
was motivated by their aggregate infrastructure failures; this is an iterative
repair study on a reused test cohort, not fresh unseen generalization evidence.
The lessons themselves remain byte-identical and receive no test-derived updates.

Within prepared-v3, B minus A is the lesson comparison under the repaired
controller. Across versions, reduced controller stops and changed solved counts
are descriptive before/after observations. Report both, together with replacement
failure modes such as call limits, command timeouts, incorrect submissions, or
missing data. A larger success count alone does not establish semantic fidelity;
source audits and evidence provenance remain separate.

## Completed repaired comparison

**Experiment status: complete attempt matrix; lesson-effect comparison inconclusive because of host-side DNS failures.**

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
