# Registry recovery and reproducible preparation

## Observed outcome

All fifteen selected held-out capsules now have verified original author images
in the local Docker cache. This includes all eight images that blocked the first
release and five additional eligible capsules from the same archive-size ordering.
No image was rebuilt, mirrored, or substituted on the basis of a model score.

This resolves preparation for this experiment. It does not establish that the
upstream registry has permanently removed its rate limit.

## What the evidence shows

The first diagnostic request without authorization returned HTTP 401. The public
bearer-token endpoint returned 200, and authenticated HEAD and GET manifest
requests returned 200. The downloaded manifest matched its SHA-256 digest, and a
pull by digest succeeded. A control pull of the original tag also succeeded.
Therefore, digest addressing is useful for reproducibility but is not proven to
be the cause of recovery.

Later, the public token endpoint still returned 200 while a manifest request
returned 429 with an empty body, an `awselb/2.0` server header, and no `Retry-After`.
This establishes that authentication success does not guarantee manifest access.
The exact quota, enforcement layer, and reset interval remain unknown.

See [diagnostic observations](../manifests/registry-diagnostics-v2.json),
[per-image recovery attempts](../manifests/recovery-v2.json), and
[selection decisions](../manifests/selection-v2.json). The original selection and
failed provisioning ledgers remain in the repository.

## Implemented approach

1. Select eligible capsules before running the agent, preserving the pinned
   official split, archive-size ordering, 50 MB ceiling, and CPU requirements.
2. Resolve public image manifests through standard bearer authentication. Keep
   the short-lived registry token in memory rather than in reports or manifests.
3. Verify manifest bytes, select linux/amd64, and pin the original image digest.
4. Pull serially, with at most four attempts per image per invocation. Backoff
   starts at 60 seconds and doubles between retries; a longer `Retry-After`
   value takes precedence. Both seconds and HTTP-date forms are supported.
5. Verify the local image digest and platform, then prepare inputs and record
   hashes. Preserve every failed attempt before continuing.
6. On resumption, reuse a ready image only when its local digest, platform, and
   prepared-input checksum match. This path makes no registry resolution call.

The final two newly selected images recovered after bounded retries; a transient
DNS failure is retained alongside the rate-limit observations. The local Colima
virtual disk was expanded from 40 to 80 GiB to hold the cohort. Per-task limits
remained unchanged: two CPUs, 2 GiB memory, and offline execution.

An isolated cache integration check replaced network resolution with an immediate
failure and verified all fifteen ready images successfully. Its machine-readable
result is [cache-recovery-check.json](../reports/cache-recovery-check.json).

## Reuse

```bash
uv run python scripts/recover_cohort.py --target 15
```

Run preparation before freezing a new experiment. The command can update cohort
and preparation manifests, so do not use it to mutate inputs during an active
frozen comparison. If the service is still throttling, retain the failure ledger
and resume after a cooldown. No account rotation or unrelated mirror is required.
The published evidence remains reviewable without registry access.
