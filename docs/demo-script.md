# English network-recovery demo script

This narrates saved real runs, not a staged live experiment. Narration uses the
macOS Samantha system voice. Target length: approximately three minutes.

## 1. The question

ReproScout is an individual MIT 1.125 project by Weibing Wang. It asks whether
lessons from failed scientific reproduction attempts help on subsequent tasks.
The output is an answer linked to execution evidence, with a clear record of
failure. We first repaired thirty-nine premature controller stops. The next study
then encountered fifty-nine DNS failures. Those failures made its lesson comparison
invalid. A scientific experiment is not complete merely because every attempt has
a log file.

## 2. The system

Inspect AI supplies orchestration and Docker transport. ReproScout independently
implements preparation, evidence tools, scoring, budgets, freezes and reports.
The controller counts the full native request, preserving tools, images and
encrypted reasoning. The new wrapper records every request attempt and applies
bounded backoff. Generation retries are limited to errors classified as DNS resolution failures without an HTTP response.
Ambiguous failed generations retain their cost reservation. The scientific container
stays offline while the host connects to the model API.

## 3. Development validation

The original CULP development pilot illustrates the evidence workflow: six correct
answers linked to captured execution output. Before the new freeze, thirty real
counting probes succeeded. Two injected DNS failures recovered on the third attempt.
We then obtained ten A and B training outcomes and eighty-two model generations,
with exact native input accounting and no network failures. One container startup
failure was retained and retried. Thirteen deterministic environment checks passed.
These checks validate observed operation, not universal scientific reproducibility.

## 4. The frozen comparison

We froze seventy-nine file hashes before running the same fifteen previously
evaluated test tasks under both conditions twice. A receives no lessons; B receives
the original three rules. Every cell begins with two live connectivity probes.
Infrastructure failures remain separate from scientific outcomes, and retries share
the original cost, call and time budgets. Incorrect answers and scientific budget
failures are final. No frozen code, input or lesson changed during evaluation.

## 5. Measured outcomes

All sixty scientific cells completed. A solved 12 and 13
of fifteen tasks across the two repetitions. B solved 10 and 11.
There were 1 separately retained infrastructure attempts
and 0 terminal counting failures. Native counts matched
returned usage on 721 of 721 generations.
Of 46 answer-solved outcomes, 46
also had unchanged prepared inputs. The report compares success, controller and
infrastructure errors, source integrity, runtime and estimated cost across all three
versions. These descriptive results do not establish statistical significance.

## 6. Delivery and limits

The release contains runnable source, pinned dependencies, freezes, failed attempts,
evidence reports, visible trajectories and request retry logs. Thirty-one software
tests passed. Older releases and their failures remain available. Prepared author
environments differ from original Medium conditions, and all test tasks have prior
exposure. Unchanged input hashes do not prove semantic evidence support. Independent
human diagnosis agreement and adversarial robustness remain unmeasured. Implementation
received Codex assistance, and this walkthrough uses synthetic narration.
