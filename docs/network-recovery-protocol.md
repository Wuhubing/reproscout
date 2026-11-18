# Network recovery and prepared-v4 protocol

## Diagnosis and scope

Prepared-v3 retained sixty attempts but only one completed successfully. Fifty-nine
attempts stopped at native counting with host DNS resolution errors before an HTTP
response; fifty-five made no model generation. This is an infrastructure-invalid
lesson comparison, not a completed scientific evaluation. The precise historical
resolver, network, or process-policy cause is not established. A successful later
probe does not explain or erase those failures.

The current host resolves the API hostname and reaches the native counting endpoint.
We retain the pinned Inspect client and native counter. We do not hardcode API IPs,
disable TLS, change DNS settings, replace scientific inputs, or infer an API outage.
Recovery is assessed in the actual execution environment, with sustained counting,
fault injection, and all five training tasks under A and B before freezing.

## Request retry policy

SDK generation retries remain disabled. A project-owned wrapper logs each attempt,
UTC timestamp, operation, request digest, duration, exception class chain, DNS flag,
HTTP status, retry decision, and backoff. It never records credentials or opaque
request contents. Counting is read-only: transient transport errors, HTTP 408/409,
500/502/503/504, and rate-limit 429 may retry; exhausted quota and authentication do
not. At most five attempts use delays of 1, 2, 4, and 8 seconds. The count timeout
remains sixty seconds, and all retry time counts against the task time limit.

Generation retries require a DNS-resolution exception and no HTTP response, proving
that the request did not reach the provider. Ambiguous read timeouts and other
possible post-dispatch errors are not retried. The reservation remains on ambiguous
failures. A DNS-only retry reuses the same request and reservation because no tokens
were generated. Native request counting still preserves tools, images, and encrypted
reasoning; there is no approximate fallback. Existing usage/reservation checks remain.

## Scientific completion and whole-cell retries

A terminal network failure or sandbox initialization failure is an infrastructure
attempt, not a completed scientific cell. Every such run remains in `all_attempts`
and the evidence export. A clean execution that submits null, reaches a scientific
execution/budget limit, or produces incorrect answers remains an unsolved scientific
outcome; it is never retried to improve a score.

The scheduler requires two successful native counting probes before each cell.
If the probe exhausts its retry policy, execution stops with the matrix incomplete;
it does not consume the remaining task matrix with predictable network failures.
A cell permits at most three total attempts with a thirty-second cooldown after an
infrastructure failure. Attempts share the original one-dollar uncached cost bound,
twenty model-call cap, and 1,800-second task runtime allowance. All incurred costs,
unknown-cost reservations, calls, and runtime from previous attempts are charged to
the remaining allowance. Preflight and cooldown time is reported separately from
scientific sample timers through the calendar interval.

The first non-infrastructure outcome is final. Aggregation exposes selected outcomes
and all attempts separately, rejects duplicate scientific outcomes, and leaves a cell
missing when no scientific outcome exists. If a retry or budget cap is exhausted,
the study stays incomplete. There are no silent replacements or success-driven reruns.

## Development gate, freeze, and inference

Before freezing, require passing unit tests (including persistent DNS failure,
transient recovery, generation retry safety, and aggregation), thirty sequential
real adapter counts, an injected two-failure sequence followed by a live count,
ten A/B training outcomes with model calls and no terminal infrastructure errors,
correct accounting bounds, and thirteen deterministic environment checks. Preserve
all development failures. Source integrity and answer correctness are reported
separately; their values are not used to tune the lesson intervention.

Freeze source, scripts, dependencies, configuration, manifests, lessons, this protocol,
and development evidence as prepared-v4. Then run the same fifteen previously
evaluated capsules, both A/B conditions, and two repetitions: sixty scientific cells.
Reverse A/B order in repetition two. Scientific inputs, original three lessons,
model snapshot, token/output limits, CPU/memory/offline policy, and scoring remain
unchanged. Prevent host idle sleep while the serial runner is active.

Compare v2, v3, and v4 success, controller errors, infrastructure errors, source audits,
sample timers, calendar duration, and estimated model cost. Include all retained
attempts when reporting operational costs and failures; also show all-attempt success
rates if a cell required retries. The within-v4 lesson comparison is descriptive on a
small, previously evaluated cohort. Cross-version results are not a randomized causal
estimate. A completed matrix does not imply every scientific task is reproducible or
that lessons helped. Never call an infrastructure-invalid matrix a completed experiment.
