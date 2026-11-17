# Controller repair and prepared-v3 protocol

## Question and identification

The v0.2.0 comparison produced A=6/15 and 5/15, B=4/15 and 5/15, with 39
application request-bound stops. This version tests the same lesson intervention
after repairing request accounting. It does not revise lessons using test answers.

Two comparisons must remain separate:

- Within prepared-v3, B versus A measures the frozen lesson intervention under
  the repaired controller, using the same fifteen tasks and two repetitions.
- Prepared-v2 versus prepared-v3 is a descriptive before/after controller comparison.
  It is not a randomized causal estimate: model sampling, temporal effects, and
  runtime variation can affect it. All fifteen test tasks have prior exposure.

## Root cause and repair

The old guard JSON-serialized Inspect messages and tool definitions, replaced
image data with an 8,192-character placeholder, added 8,192 for framing, and
compared UTF-8 bytes with 60,000. It counted opaque encrypted reasoning as text.
Bytes are a conservative text-token bound, but this combination was a poor
context admission policy and caused premature stops far below model capacity.

The new adapter calls the native Responses input-token endpoint with the complete
converted input, tool schemas, images, encrypted reasoning, and reasoning effort.
It uses the same Inspect conversion functions as generation, isolated behind a
small adapter pinned to Inspect 0.3.290. No fallback tokenizer silently discards
opaque reasoning. A count failure refuses generation and records the error type.
Actual reasoning payloads are preserved for generation and local logs.

The request input bound is the measured count plus a fixed 2,048-token margin.
The input limit remains 60,000; the 4,096-token output reservation is separate.
The $1 sample cap, 20 model-call cap, 30-minute wall clock, 180-second command
limit, model snapshot, low reasoning, two CPUs, 2 GiB memory, and offline policy
remain unchanged. Counter calls have a 60-second timeout and no automatic retries.
Their latency is included in sample wall time; they are not model generations.

Monetary admission reserves uncached input plus maximum output cost before dispatch.
Settlement records actual returned usage. Either an input-count underestimate or
a monetary reservation overrun stops execution for audit. Failed requests retain
their reserved unknown cost. The ledger records native tokens, historical byte
bound, opaque byte volume, request digest, admission result, and actual usage.

References checked November 17, 2026:
[OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting),
[API reference](https://developers.openai.com/api/reference/python/resources/responses/subresources/input_tokens/methods/count),
and [model specification](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
The model's documented 400,000-token window is not the application's chosen limit.

## Development gate before formal execution

Run both A and B on all five existing official training capsules. Retain the first
pilot initialization failure and every subsequent development record. The fixed
validation matrix uses repetition label 2 to distinguish it from that startup
attempt. No validation result is counted as a formal test result.

Require software checks, the deterministic environment check, successful real
native counting and generation, no counted-context or counting-service failure
in the completed development matrix, and at least one request admitted after its
historical byte bound exceeds 60,000. Audit returned input usage against the new
reservation. Record all outcomes, including tasks blocked by unavailable data or
other execution limits. Correctness on every development task is not required to
verify request accounting. Source audit failures are retained and reported separately;
they do not establish faithful reproduction even when answers pass the scorer.
One development notebook B run modified its data loader. The controller gate
is specifically about admission and usage accounting, not source-fidelity acceptance.
The formal report will retain the historical answer-only solved metric and add
answer-solved attempts whose original prepared-input audit is unchanged. No scoring
threshold, prompt, or lesson is changed in response to this development observation.

A deterministic timeout check was also corrected: an old image's standalone
`test` executable returned 139 under amd64 emulation. This was a probe crash, not
proof that the timed-out process survived. The new check uses the bash builtin
and records its exit code and output. This changes validation diagnostics, not
the agent's command timeout or scientific execution policy. Prior failed checks
and startup failures are preserved. Colima was restarted with the same four CPUs,
8 GiB memory, 80 GiB disk, and QEMU amd64 emulation; no image was rebuilt.

## Freeze and complete rerun

After the development gate passes, hash code, scripts, configuration, lessons,
cohort, input manifests, dependency lock, this protocol, and validation evidence.
Use a new experiment ID, prepared-v3. Keep original lesson bytes and all fifteen
prepared task/image digests identical to prepared-v2. Record all fifteen tasks as
previously evaluated; none is newly unseen test data.

Run sixty fresh attempts: fifteen tasks times A/B times two repetitions, using
A then B in repetition one and B then A in repetition two. Run serially in fresh
containers. Do not replace tasks or revise the agent, lesson, threshold, or budget
after observing new formal outcomes. Do not silently retry a failed formal cell.
If the orchestration process stops without a record, investigate and document it
before resuming missing cells. Existing records remain in the denominator.

## Reporting and preservation

Preserve prepared-v1 and prepared-v2 results, freezes, releases, and evidence.
Export every development and formal record with explicit experiment identifiers.
Report solved counts per repetition, paired outcomes, question scores, model cost,
wall time, native token maxima, old-bound crossings, count failures, context stops,
call/time/cost limits, initialization failures, source audits, and artifact hashes.
Explain lesson applicability without treating operational signatures as human
causal labels. No significance, independent diagnosis agreement, or adversarial
robustness claim is implied by completing the experiment.
