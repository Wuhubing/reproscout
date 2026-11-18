# Lesson revision: findings and limits

B scored higher than A in this rerun: A 20/30 versus B 26/30. The preceding v4 run scored A 25/30
and old B 21/30. Within v5, 1 pairs favored A, 7 favored
B, 19 passed in both, and 3 passed in neither.
These are thirty repeated observations on fifteen previously exposed tasks.

## Diagnosed problems and intervention

The [four adverse-pair study](lesson-pair-analysis-v4.md) distinguishes serialization
failure from scientific error, wrong output selection, and failure to submit within
budget. The original lessons did not address those checks and were not consistently
followed. Tool traces cannot prove which individual old lesson caused a behavior.
Revision 2 adds a final numeric-type check, targeted question-to-output matching,
submission budgeting, and conditional handling of rendering and data blockers.
It prohibits editing scientific copies as well as original files. No task answers
or capsule-specific repairs appear in the revised prompt.

## Development evidence

A fresh three-arm study on five official training tasks produced fifteen scientific
outcomes and rejected candidate 1 for editing a scientific copy. Candidate 2 was
then checked on all five tasks, giving twenty development outcomes. Candidate B: 3/5; legacy B: 4/5;
A: 3/5. The declared gate checks completion, report submission,
numeric value types, native counts, original hashes, and manual code-copy fidelity.
The initial raw-success floor passed: False.
The acceptance comparator was amended before candidate-2 execution to exclude
legacy successes involving scientific modifications; the legacy qualified count
was 3/5. This is an explicit development-stage
amendment, not the original preregistered raw-score floor. See the
[confirmation protocol](lesson-confirmation-protocol.md).
A passing amended gate establishes bounded observed operation, not statistical improvement.
All attempts and any adverse training results remain available.

## Formal resource and failure breakdown

| Condition | Solved | Generations | Estimated cost | Sample minutes | Outcome categories |
|---|---:|---:|---:|---:|---|
| A | 20/30 | 370 | $0.77698 | 64.16 | {'model_call_cap': 4, 'answer_solved': 20, 'completed_without_passing_score': 6} |
| B | 26/30 | 294 | $0.72383 | 66.23 | {'completed_without_passing_score': 4, 'answer_solved': 26} |

These group metrics cover selected scientific outcomes; the cross-version report
also counts infrastructure attempts. All scientific failures are final. No selective
rerun, scorer relaxation, or mid-experiment lesson adjustment was used.

## What can be claimed

The exact score gap and trajectories are observations under the frozen settings.
Cross-version changes also reflect new model samples and time; a changed A baseline
is an especially useful warning against attributing all change to the lessons.
The revision used insights from exposed test traces, so it cannot be described as
pure training-only lesson discovery. No fresh held-out or significance claim applies.

Original-file hashes do not detect modified new copies or prove that the evidence
semantically supports an answer. The v4 A manuscript-copy edit is a concrete
counterexample. Read [source exceptions](../reports/source-integrity-v5.json) and
[supplemental trajectory review](../reports/trajectory-review-v5.json) alongside
answer scores, never as a replacement for the historical scoring rule.

Targeted review already found that new B on capsule-9054015 repetition 1
scored correctly but reimplemented the q1 formula instead of querying the author
function. New B on capsule-2708693 repetition 1 used direct arithmetic after a
rendering failure and did not reproduce the full manuscript. These observations
show that the prompt does not guarantee compliance; see the four-pair follow-up.
New B on capsule-0504157 repetition 2 likewise passes with the string `"1000"`,
while rebuilding an aggregation that omits author preprocessing. It violates both
the JSON-number reminder and the unchanged-computation requirement despite passing
the scorer. New A on capsule-9054015 repetition 2 uses a modified inline function
copy. These limitations apply to both conditions and cannot be reduced to hashes.

A subsequent, separately frozen study could test a typed submission schema and
execution paths that extract unchanged author blocks with recorded source spans.
Those controls would change the intervention and require new development validation
and a genuinely unexposed test cohort. They were not added during this experiment.

[Four-version comparison](controller-comparison.md) ·
[All sixty outcomes](results.md) · [Four-pair follow-up](adverse-pair-followup-v5.md) · [Development gate](../reports/development-v5-validation.json) ·
[Revision protocol](lesson-revision-protocol.md)

## Remaining adverse pair in v5

Only capsule-4671827 repetition 1 favors A: A submits `Semantic-based`, while
B submits `Combination`. The question asks about **44 elements**. B's cited
image (step 009) instead compares Greedy and Combination over **2–12 elements**.
This is a remaining wrong-figure selection, not a numeric serialization issue.
It shows that a question-to-output reminder did not guarantee correct matching.
The image was visually reviewed; scores remain unchanged.

[New B evidence](../reports/runs/20261118T085405675915Z-capsule-4671827-run-B1/report.html) ·
[New A evidence](../reports/runs/20261118T085245071914Z-capsule-4671827-run-A1/report.html)
