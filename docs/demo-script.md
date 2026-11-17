# English expanded-study demo script

Target length: approximately 3.5 minutes. This narrates saved real experiments,
not a staged live model run. Narration uses the macOS Samantha system voice.

## 1. The question

ReproScout is an individual MIT 1.125 project by Weibing Wang. It asks whether
lessons from failed reproduction attempts can help an agent reproduce scientific
results. Our users are researchers reusing a baseline, artifact reviewers, and
students running published code. We start with the author's code and data. The
useful output is an answer with an inspectable path to the evidence. A failed
attempt should also tell the reader what happened and where to investigate.

## 2. The system

This application is independently implemented, not a fork of an existing benchmark
harness. Inspect AI provides general orchestration, Docker transport, and logs.
ReproScout owns preparation, evidence tools, budgets, external scoring, freezing,
and reports. Each attempt uses a fresh offline container with the author's archived
environment. The answer key and API credential stay outside. Four tools let the
agent run commands, read files, view images or PDF pages, and submit evidence-linked
answers. Original input hashes are audited separately from answer correctness.

## 3. A real reproduction

The development pilot ran the original CULP classification code. The agent
submitted six answers, and all six passed the independent scorer. Each submitted
value links to a captured output and line range. Opening those links shows actual
execution evidence. The validated repeat also has an unchanged-input audit. We
retain failed development attempts, including missing offline data and an inefficient
notebook workflow. The report is meant to make both successful and unsuccessful
attempts inspectable, rather than present only a successful screenshot.

## 4. The expanded experiment

The first release was limited by registry rate limits. Standard authentication,
verified digests, cached layers, and serial pulls with backoff recovered all fifteen
selected held-out images. No difficult task was replaced based on model scores.
Five development tasks produced three frozen lessons. The same agent, model,
budgets, and lessons were retained for sixty fresh runs: A and B on fifteen tasks,
twice. A receives no lessons; B receives the frozen rules. Order reverses in the
second repetition. Two tasks were previously evaluated; thirteen are newly evaluated,
and the report separates these groups.

## 5. Measured results

In the first repetition, A solved 6 of fifteen tasks and B solved 4. In the second, A solved 5 and B solved 5. The average B minus A change was -1.0 solved tasks. All sixty planned records are present, at an estimated model cost of 0.76 dollars. 39 attempts stopped at our controller's request-size bound. One attempt failed during initialization before any model call; it remains unsolved in the primary analysis. 59 attempts have unchanged-input audits; one has no audit. All recorded artifact hashes verified. These results do not meet the proposed improvement target.

## 6. Delivery and limits

The release includes the runnable repository, pinned dependencies, selection and
recovery ledgers, frozen lessons, evidence reports, and visible model and tool
trajectories. Eighteen software tests and thirteen environment checks passed.
These checks do not establish independent diagnostic agreement or adversarial
robustness. The application uses prepared author environments, so it is not an
unchanged CORE-Bench Medium result. The controller's request bound is also separate
from the model's actual context window. This selected cohort and two repetitions
do not establish statistical significance. Implementation received Codex assistance,
and this video uses synthetic narration.
