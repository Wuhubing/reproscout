# Experiment protocol: prepared-author-environment pilot

## Research question

Does a frozen development-derived lessons file improve reproduction accuracy or
reduce wasted execution under the same model, tool, and budget constraints?

## Task selection

Use the official train/test split from CORE-Bench commit
`e32a2980e72fe6eb04ee04eb749458f570625663`. Rank available archives by size,
exclude archives above 50 MB and explicit GPU requirements, and require an archived
author image. Target five development tasks (including a vision example) and ten
held-out tasks. Image preparation failures are recorded before evaluation. If the
registry prevents completion of the target cohort, freeze the smaller available
cohort and report that selection limitation prominently. Do not use held-out model
scores to select, replace, or tune tasks.

The cohort is deliberately small and biased toward small downloadable artifacts.
It is not representative of all scientific code. Archive size is not a guarantee
of CPU feasibility; resource failures remain in the evaluation denominator.

## Intervention

A: no lessons. B: one frozen lessons file, curated from development traces with
Codex assistance. This is a human-in-the-loop rule intervention, not an autonomous
implementation of all ExpeL mechanisms. Both use the same instructions, tools,
model, per-request limits, per-task budget, and prepared input archive.

## Execution

Two repeats per condition on every held-out task. Order within each task is A/B
for repeat 1 and B/A for repeat 2. Execute serially, in fresh containers, with no
shared writable task state. Model-side prompt caching may occur and is accounted
for; no agent answer cache or shared memory is used. Formal runs do not generate
new lessons. Verify frozen code/configuration/manifest hashes before each cell.

Image pulls and data acquisition are trusted preparation. Execution is offline,
with author images pinned by digest, no privileged mode, no Docker socket, and
no host bind mounts. This changes the original Medium environment-construction
burden. Report results only as the prepared-environment variant.

## Outcomes

A capsule is solved only if every original question passes the independent
implementation of the original scorer. Report per-question verdicts as well.
No submission, model limit, execution limit, or runtime failure counts as unsolved.
Do not silently exclude failed samples from accuracy. Framework-level successful
log completion does not imply a sample succeeded.

Report each repeat separately and the average B-minus-A solved count. The original
project's +2 solved goal is a target, not a post hoc decision rule. Small cohorts
and two repeats do not establish statistical significance.

Report per-condition costs, wall time, language/modality groups, failure labels,
and per-task outcomes. Evidence references are mechanically checked separately;
semantic support requires audit. No independent human agreement percentage is
claimed without a separately conducted annotation study.

## Changes and retries

Before freezing, retain all development failures and document implementation
changes. After freezing, do not tune the system on held-out outcomes. A runner
infrastructure bug requires a new experiment ID and an explicit rerun policy;
never splice selective improved reruns into an older experiment. Resume only
missing cells. Duplicate formal cells cause aggregation to fail for review.
