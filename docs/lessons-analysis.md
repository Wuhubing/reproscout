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

The repaired formal comparison will be summarized here only after all sixty
planned records are complete. Historical results remain in prepared-v2 and the
v0.2.0 release, and are never overwritten or pooled with the new denominator.
