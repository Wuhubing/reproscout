# Implementation and delivery plan

## Objective

Deliver an independently authored reproduction application with real, auditable
runs. Use Inspect AI as general-purpose infrastructure; do not fork or invoke an
existing benchmark task. All project-authored content is in English.

## Delivery sequence

1. Establish the independent repository and pinned dependencies.
2. Validate Docker, model access, sandbox boundaries, and termination behavior.
3. Execute one official training capsule with original author code and evidence.
4. Extend the same application to fifteen size-ranked eligible held-out Python/R
   capsules. Recover rate-limited original images and preserve all selection exclusions.
5. Derive development lessons, freeze code/configuration/data membership, and
   run both conditions twice without updating lessons on held-out outcomes.
6. Export reports, failure records, cost accounting, and a reproducible release.

## Scope and honesty

The first execution uses a controller-provisioned author image instead of giving
the agent privileged Docker-in-Docker. This is a prepared-environment variant;
it must not be called an unchanged CORE-Bench Medium reproduction. Images are
pulled before the 30-minute sample clock; provisioning is recorded separately.
The tool surface includes text, image, and PDF inspection. Full Medium environment
construction remains outside this prepared-environment experiment. Task modality
labels and actual image-tool use are reported separately.

## Acceptance

A task is successful only when all questions pass the fixed scorer. Evidence
availability is evaluated separately from answer correctness. A complete release
must preserve failed runs and known limitations, not only successful screenshots.
No hypothesis improvement or diagnostic agreement is claimed without measurement.

## Expanded delivery acceptance

The v0.2.0 target is fifteen held-out tasks, both conditions, and two repetitions:
sixty fresh formal records. Five development tasks supply the original three frozen
lessons. Two held-out capsules have prior v0.1.0 results; thirteen are newly evaluated.
Report these groups separately and preserve v0.1.0 as historical evidence.

The registry recovery uses public bearer authentication, manifest digest checks,
serial pulls, bounded backoff, and verified local caches. No task is replaced based
on its score, and no image is rebuilt to make it pass. An unavailable service is
not evidence of an incorrect scientific answer. Retained initialization failures
are identified separately even though the primary all-attempt score counts them
as unsolved.

Delivery requires a complete frozen run matrix, portable evidence for every record,
artifact hash verification, an updated English results narrative and video, browser
navigation checks, and a source release with no credentials or private answer keys.
The success criterion is a complete and auditable experiment, not a positive A/B
effect. The original proposed improvement of two solved tasks is tested rather
than assumed.

## v0.3.0 completion record

Native request accounting was implemented and validated on five training tasks
under both conditions. Twenty-two software tests and thirteen environment checks
passed. A new immutable freeze preceded sixty formal attempts. All sixty records
were retained, but 59 DNS failures made the lesson-effect comparison inconclusive.
The delivery includes the failure diagnosis and full comparison rather than a
selective rerun. Network-resilience changes belong to a separately validated and
frozen future experiment, not an in-place alteration of this release.

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
