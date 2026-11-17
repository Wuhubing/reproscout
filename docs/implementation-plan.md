# Implementation and delivery plan

## Objective

Deliver an independently authored reproduction application with real, auditable
runs. Use Inspect AI as general-purpose infrastructure; do not fork or invoke an
existing benchmark task. All project-authored content is in English.

## Delivery sequence

1. Establish the independent repository and pinned dependencies.
2. Validate Docker, model access, sandbox boundaries, and termination behavior.
3. Execute one official training capsule with original author code and evidence.
4. Extend the same application to a fixed small Python/R cohort, if archived
   images and local resources permit. Preserve all selection exclusions.
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
