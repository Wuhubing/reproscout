# Environment validation

Validation performed on November 17, 2026.

- Host: ARM64 macOS; Python 3.12.2.
- Docker Engine: 29.5.2 in Colima; Docker Compose: 2.30.3-desktop.1.
- Inspect AI: 0.3.290; dependency resolution pinned in uv.lock.
- Colima was initially stopped. It was started with 4 CPUs and 8 GiB memory.
- The active Docker context changed from an unavailable OrbStack context to Colima.
- A broken Compose plugin symlink was redirected to the installed Docker Desktop binary.
- The CULP author image runs linux/amd64 via emulation. Its runtime reports Python
  3.6.3, scikit-learn 0.19.2, networkx 2.1, and numpy 1.13.3.

The deterministic `validate` run checked network failure, absent credentials,
absent host Docker socket, absent supplied results, runtime versions, timeout
raising, and termination of a timed-out process. The author entry script completed.
See the exported environment-checks.json for machine-readable observations.

## Integration findings

- A mock model has no default pricing metadata; deterministic validation must not
  configure a monetary limit on that mock model.
- The pinned real model also needed explicit pricing registration in Inspect.
- Inspect's input_tokens excludes cache-read tokens. An initial accounting formula
  double-subtracted cached tokens; it was corrected using the untouched raw usage
  and covered by a regression test before formal evaluation.
- Inspect can finish a task log successfully while a sample has an error. Run
  status therefore checks the sample error independently.
- Some author code requires runtime external data. Such tasks fail under the
  offline policy; this is retained as a meaningful environment constraint.
- The registry rate-limited bulk image pulls with HTTP 429. Preparation attempts
  and final cohort membership are retained separately from evaluation outcomes.

## Expanded recovery on November 17, 2026

The local Colima VM was restarted with an 80 GiB virtual data disk after the
previous disk remained at 40 GiB. CPU allocation stayed at four and memory at
8 GiB; individual task containers still receive two CPUs and 2 GiB memory.
Recovery checks host free space before downloading additional uncached images.
The old HTTP 429 failure records remain available. Successful authenticated
manifest requests and verified digest pulls are recorded in recovery-v2.json.

## Controller-repair validation and network findings

V3 restarted the same Colima configuration: four CPUs, 8 GiB memory, 80 GiB disk,
and QEMU amd64 emulation. A deterministic check initially reported failure because
standalone test itself crashed with exit 139. Using bash's builtin test made the
probe observable and yielded thirteen passed checks in run
20261117T223433045169Z-capsule-6460826-validate-A1. Earlier failed checks and startup
attempts are retained in reports/development-v3-validation.json.

The subsequent frozen formal experiment encountered 59 host-side DNS resolution
failures during native token counting. No HTTP response was observed for these
failures. This is separate from the deliberately offline scientific containers.
A later post-run counting-only connectivity probe succeeded; it changed no outcome.
See reports/transport-failures-v3.json and reports/post-run-connectivity-v3.json.

## v0.4.0 network recovery delivery

The frozen prepared-v4 study completed sixty scientific cells, with 1
additional infrastructure attempts retained separately. A solved 25/30 and B
21/30. The project now records bounded request retries, checks counting connectivity
before each cell, and keeps scientific failures final. Thirty real counting probes,
injected DNS recovery, ten development A/B outcomes, 31 software tests, and thirteen
environment checks passed before formal evaluation. Historical v3 DNS failures
remain evidence of an invalid infrastructure-limited comparison.

See [the network protocol](network-recovery-protocol.md),
[updated comparison](controller-comparison.md), and
[development evidence](../reports/development-v4-validation.json).

## v0.5.0 completed lesson-revision study

The revised lesson candidate passed the amended development
gate after a rejected first candidate; twenty training outcomes are retained. All sixty formal scientific outcomes completed under an unchanged freeze:
A 20/30, B 26/30, with 0 separately retained infrastructure
attempts. This is test-informed method revision on an exposed cohort. Original-file
hashes do not audit scientific changes to new copies; supplemental trajectory review
and the original scorer remain separate. The v0.4.0 release and all failures persist.

See [the four-pair diagnosis](lesson-pair-analysis-v4.md),
[revision protocol](lesson-revision-protocol.md), and [comparison](controller-comparison.md).
