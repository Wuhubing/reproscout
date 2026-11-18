# Lessons after controller and network recovery

V4 shows no observed lesson benefit: A scored 25/30 (83.3%) and B scored 21/30 (70.0%), a B-minus-A difference of -13.3 percentage points. Across matched task/repetition pairs, four favored A and none favored B; twenty-one passed in both conditions and five passed in neither. These observations do not establish a statistically significant causal effect.

The original lesson file is unchanged. A receives no lessons; B receives three
workflow rules derived from five official training tasks. No formal outcome was
used to rewrite the rules, change scientific inputs, or select replacement tasks.

## What the successive studies establish

- V2: A 11/30, B 9/30, with 39 premature byte-proxy controller stops.
- V3: A 0/30, B 1/30, with 59 DNS failures. This is an invalid infrastructure-limited
  comparison and does not show either lesson benefit or harm.
- V4: A 25/30, B 21/30; all sixty scientific cells completed. Mean B-minus-A
  solved count per repetition is -2.0. There were 1
  separately retained infrastructure attempts and 0 native-token stops.

A completed evaluation does not mean all tasks succeeded. Offline author data
dependencies, scientific code behavior, execution time, model-call limits, and
agent choices still constrain performance. These failures remain final outcomes.
A small selected cohort with two repetitions cannot establish statistical significance.
All fifteen capsules were previously evaluated; no unseen-generalization claim applies.

## Answer correctness versus faithful reproduction

46 formal outcomes passed answer scoring. 46
also had an unchanged prepared-input audit. Source audits across all attempts:
`{'unchanged': 58, 'missing': 1, 'changed': 2}`. A changed original scientific input prevents claiming a
faithful unchanged-input reproduction, even if the answers happen to match.
An unchanged audit does not independently prove semantic evidence support.

The historical v3 development notebook B source edit remains recorded. V4 development
source-integrity violations: 1. Training
network validation is not a guarantee of scientifically faithful model behavior.

## Why the comparison is more interpretable now

Native counting preserves the full request. Every request attempt and retry is
recorded; ambiguous generation dispatches are not retried at request level.
The scheduler checks network health, separates infrastructure attempts from final
scientific outcomes, and shares original budgets across any cell retries. It does
not keep rerunning a scientific failure until it passes. All-attempt cost and time
remain visible, preventing retries from disappearing from operational metrics.

See [three-version metrics](controller-comparison.md), [all sixty outcomes](results.md),
[the frozen recovery protocol](network-recovery-protocol.md), and
[the retained evidence browser](../reports/index.html).

## Observed remaining failure mechanisms

| Condition | Answer solved | 20-call cap | Completed without passing score | Other sample error | Source not unchanged | Generations | Estimated cost | Sample minutes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 25/30 | 5 | 0 | 0 | 1 | 366 | $0.83703 | 65.38 |
| B | 21/30 | 3 | 6 | 0 | 1 | 355 | $1.00391 | 77.64 |

These group costs and timers describe the sixty selected scientific outcomes;
the comparison report additionally includes infrastructure attempts. Source
exceptions overlap outcome categories. A completed submission without a passing
score is not itself evidence of a network or controller failure.

The old byte guard and DNS aborts are no longer explanations for the v4 group
difference. The unchanged twenty-call budget can still stop long workflows, and
successful transport does not guarantee correct scientific execution or faithful
input handling. Three general workflow rules cannot by themselves supply missing
author dependencies or guarantee a correct interpretation of each capsule.
These are limits of the approach, not proven causes for any particular failed run.

The observed A/B totals do not isolate a causal mechanism for the lessons: model
sampling and task-specific trajectories also vary. No post-hoc rule edits or
selective retries were used. Per-pair outcomes and full retained trajectories are
provided so that a later, separately preregistered lesson study can investigate
specific failure mechanisms on a genuinely fresh cohort.

[Group breakdown data](../reports/lessons-breakdown-v4.json) ·
[Paired outcomes](../reports/paired-outcomes-v4.json) ·
[Source exceptions](../reports/source-integrity-v4.json)

B used fewer generations (355 versus 366), but had higher estimated usage cost ($1.00391 versus $0.83703) and longer selected sample time (77.64 versus 65.38 minutes). More expensive or longer trajectories did not translate into more solved tasks in this run. Generation count alone does not measure token volume or execution effort.
