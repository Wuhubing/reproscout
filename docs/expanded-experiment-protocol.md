# Expanded experiment: prepared-v2

## Purpose and scope

Recover the original unavailable author images and reach the proposal's target
of 15 official held-out capsules. The five development tasks and their existing
three lessons remain unchanged. This is a new complete A/B experiment, not a
merge of selected earlier successes into a larger denominator.

## Selection before execution

Keep the original pinned official test split and archive-size ordering. Extend
the first selection quota from ten to fifteen eligible test capsules: archive at
most 50 MB, published author image, and no explicit GPU execution requirement.
Do not use model outcomes to select or replace capsules. Preserve the original
selection and failure ledgers; publish selection-v2.json and recovery-v2.json.
Image availability is checked before freezing. A prepared task that later fails
execution remains in the formal denominator.

## Recovery and environment

Use standard Registry bearer authentication for public images, verify manifest
SHA-256, pin the returned digest, and pull serially. Retain a bounded retry record
and honor a supplied Retry-After delay. Do not use account rotation, alternate
identities, or unrelated mirrors. Reuse downloaded layers and inspect local image
digests before execution. Reserve host disk space and expand only the local
Docker VM's virtual disk; task CPU, memory, network, and timing limits stay fixed.

Initial recovery succeeded for a previously unavailable image by digest. A follow-up
pull of the original tag also succeeded, so the observations support a transient
access/rate-limit recovery, not a proven tag-specific bug or permanent quota fix.
The server's exact quota and reset window are unknown.

The implementation follows the official [Registry token authentication protocol](https://distribution.github.io/distribution/spec/auth/token/)
and [Registry HTTP API](https://distribution.github.io/distribution/spec/api/).
Neither reference establishes CodeOcean's private quota policy.

## Invariants

- Same agent implementation, model, tool interfaces, system instructions, scoring,
  source audit, request limits, command timeout, offline policy, and resource limits.
- Same frozen development-v1 lessons, with an identical SHA-256.
- No additional lesson extraction from the previous or expanded held-out traces.
- Every one of the fifteen tasks receives A and B twice: sixty fresh formal cells.
- A/B order in repetition one and B/A in repetition two; serial execution and
  fresh containers avoid concurrent-task resource interference.
- Each attempt retains failures, evidence, usage, and a source-integrity audit.

## Previously evaluated tasks

Two of the fifteen official test capsules were already observed in prepared-v1.
This is disclosed as prior evaluation exposure. No agent or lesson changes were
made in response to their outcomes. Report the full fifteen-task comparison and
an additional breakdown for the thirteen newly evaluated capsules versus the two
previously evaluated capsules. Do not describe all fifteen as never previously seen.
The original v0.1.0 release and its eight formal records remain available separately.

## Reporting

Report each repetition, per-task question verdicts, all-question solved counts,
language/modality and prior-exposure breakdowns, model usage cost, wall time, and
provisional failure diagnoses. Separately audit source changes and artifact hashes.
A vision-labelled question does not imply the image tool was used. No significance
or independent human diagnosis agreement is inferred from these repetitions.

The primary completion criterion is all sixty planned cells recorded without
post-outcome task replacement. An infrastructure startup failure must be preserved
and explicitly resolved before a missing cell is resumed; it must not be silently
counted as an unrelated successful rerun.
