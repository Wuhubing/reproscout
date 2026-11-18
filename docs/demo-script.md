# English repaired-controller demo script

Target length: approximately 3.5 minutes. This narrates saved real experiments,
not a staged live model run. Narration uses the macOS Samantha system voice.

## 1. The question

ReproScout is an individual MIT 1.125 project by Weibing Wang. It asks whether
lessons from failed scientific reproduction attempts help on subsequent tasks.
The useful output is an answer with inspectable execution evidence, together
with a clear account of failure. In the previous fifteen-task study, lessons did
not improve the average solved count. But thirty-nine attempts stopped at our
controller's request-size guard. Before interpreting that result as a lesson
failure, we needed to investigate and repair the measurement.

## 2. The repaired system

The old guard counted serialized bytes, including encrypted reasoning payloads,
as a conservative token bound. Native recounting of all thirty-nine stopped
requests found only about six to eighteen thousand input tokens. The new
controller counts the complete request through the native token endpoint, adds
a fixed margin, and reserves monetary cost before generation. It preserves the
original conversation and encrypted reasoning. Count failures stop safely.
Inspect AI supplies general orchestration and Docker transport; ReproScout owns
preparation, evidence tools, scoring, budgets, freezes, and reports.

## 3. Development validation

The original CULP development pilot demonstrates the evidence workflow: six
answers, six correct verdicts, and links to recorded output. Before the repaired
formal comparison, we ran both conditions on all five training tasks. Native
counts matched returned input usage, and requests that crossed the old byte bound
continued successfully. One notebook B attempt answered correctly but changed
its original data loader. We retain that violation and distinguish correct
answers from correct answers with unchanged inputs. The controller check does
not certify every reproduction as faithful.

## 4. The frozen comparison

We froze a new version before generating formal results. The same model, tools,
scientific inputs, original author images, three lessons, monetary cap, and
execution limits were retained. A receives no lessons, while B receives the
original frozen rules. Fifteen tasks receive both conditions twice, with order
reversed in the second repetition. All fifteen tasks have been evaluated before;
this is a repair study on a reused test cohort. Earlier results remain separate.
Within-version A versus B and across-version controller changes answer different
questions and must not be confused.

## 5. Measured outcomes

All sixty attempts are recorded, but this experiment cannot establish a lesson effect. A solved zero tasks in both repetitions. B solved one and zero. Fifty-nine attempts failed at host-side DNS resolution before the counting request received an HTTP response. Fifty-five made no model call. On the thirty-nine generations that occurred, native counts matched returned usage exactly, and eight requests crossed the old byte bound. Lower cost and runtime mostly reflect early refusal. All input audits were unchanged, mostly without agent activity. Every failure is retained, and no frozen outcome was replaced.

## 6. Delivery and limits

The release contains the runnable repository, dependency lock, original and new
freezes, recovery and controller audits, evidence reports, and visible model and
tool trajectories. Twenty-two software tests and thirteen environment checks
passed. These checks do not establish human diagnostic agreement or adversarial
robustness. Prepared author environments differ from original Medium conditions.
An unchanged-input audit is not proof of semantic fidelity. We report remaining
execution failures and avoid statistical-significance claims. Implementation
received Codex assistance, and this video uses synthetic narration.
