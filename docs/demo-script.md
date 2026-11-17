# English final demo script

Target length: approximately 3.5 minutes. This is a narrated walkthrough of saved
real execution evidence, not a staged live model run. Narration is generated with
the macOS system voice. All numerical claims must match docs/results.md.

## 1. The question

ReproScout is an individual MIT 1.125 project by Weibing Wang. It asks a practical
question: can lessons from failed reproduction attempts help an agent reproduce
scientific results? Our users are researchers reusing a baseline, artifact
reviewers, and students running published code. We start with the author's code
and data. The useful output is both an answer and a clear path to the evidence.
A failed attempt should also tell the reader what happened.

## 2. The system

This is an independently implemented application, not a fork of an existing
benchmark harness. Inspect AI provides general agent orchestration, Docker
transport, and logs. ReproScout owns task preparation, evidence tools, budgets,
external scoring, experiment freezing, and reporting. Each attempt starts in a
fresh, offline container using the author's archived environment. The answer key
and API credential stay outside the container. Four tools let the agent run a
command, read a file, view an image or PDF, and submit an evidence-linked report.

## 3. A real reproduction

The development pilot ran the original CULP classification code. The agent
submitted six answers, and all six passed the independent scorer. The report
connects each answer to a captured command output and line range. Opening those
links shows the actual recorded evidence, rather than an unsupported explanation.
The source audit confirms that the prepared input files remained unchanged in the
validated repeat. Other development attempts failed, and those traces remain in
the report. They include an unavailable external dataset and a notebook workflow
that exhausted the context bound.

## 4. The experiment

We used five official training tasks to develop three workflow lessons. The rules
cover missing offline data, efficient notebook execution, and discovering the
provided documentation. Before evaluation, we froze the lessons, code,
configuration, input manifests, and held-out membership. Baseline A receives no
lessons; B receives the frozen rules. Two held-out tasks run in both conditions,
twice, for eight formal attempts. The order reverses in the second repetition.
No held-out trace creates new lessons during this comparison.

## 5. Results

Both conditions solved one of two tasks in each repetition. The average solved
count improvement is zero. The Python task failed under the fixed execution and
context bounds; the R task succeeded in every formal attempt. Time differences
reversed between repetitions, so the rules did not show a stable time advantage.
All eight formal attempts together cost about nine cents in model usage, excluding
preparation and host compute. All original prepared inputs remained unchanged.
These are observations from two unique tasks, not a statistically strong estimate.

## 6. Delivery and limits

The deliverable includes the runnable repository, pinned dependencies, selection
ledger, lessons, evidence reports, and actual model and tool trajectories. Fourteen
software tests and thirteen deterministic environment checks passed. These are
not a substitute for an independent human diagnosis study or an adversarial prompt
evaluation. Registry rate limits reduced the available cohort. The experiment uses
prepared author environments, so it is not an unchanged CORE-Bench Medium result.
This small comparison demonstrates an inspectable workflow; it does not establish
general scientific reproducibility. Code and documentation received Codex assistance,
and this video uses synthetic narration.
