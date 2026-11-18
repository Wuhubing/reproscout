# English controlled-execution walkthrough

Saved real results, not a staged live run. Narration uses the macOS Samantha voice.

## 1. The research question

ReproScout is an individual MIT 1.125 project by Weibing Wang. It tests whether
scientific reproduction workflows improve reliable answers. Version five exposed
a gap: answers could score correctly even when the agent rewrote a computation.
Version six separates answer scoring from execution fidelity and evidence meaning.

## 2. What changed

Condition A keeps the same prompt, tools, model and budgets. Condition B can execute
only inventoried original author files. It cannot provide replacement formulas,
loaders or scripts. Numeric types and current-execution evidence are enforced at
submission. This changes tool capabilities as well as lessons, so it is not a pure
prompt comparison. Source hashes alone do not prove faithful science.

## 3. Development evidence

The original CULP pilot illustrates inspectable evidence. The new ten-cell training
study scored A four of five and B three of five. A's extra notebook success replaced
a loader in memory, while B preserved its missing-data blocker. All B submissions
passed type and provenance checks. The predeclared gate was unchanged. Forty-eight
software tests and two offline wrapper probes passed. A failed plotting fixture and
one failed container setup are preserved, with their subsequent resolutions.

## 4. Freeze and interpretation

We froze 506 file hashes before all sixty scientific outcomes. The same
fifteen tasks had been evaluated before, so this is an exposed-cohort regression
study. A's earlier decline consisted of six regressions and one gain: wrong output
selection, rewritten calculations, misreading computed medians and failure to submit.
A did not receive B lessons. These observations do not establish causation.

## 5. Measured results

All sixty scientific cells completed. A solved 24 of thirty and B solved 20.
B had 0 accepted type violations and
1 missing reports. Its solved-and-verified-execution
intersection was 20 of thirty. A is not automatically
certified by this execution audit, so unverified must not be interpreted as zero
faithfulness. There were 0 separately retained infrastructure
failures. Full reports compare correctness, execution checks, time and cost.

## 6. Delivery and limits

The release preserves all old results and every failure. The evidence app separates
correct answers, typed submissions and verified original execution. Semantic support
requires an additional artifact review and remains distinct from mechanical
provenance. No independent human agreement, fresh held-out generalization or
statistical significance is claimed. Source and pinned dependencies are included.
Implementation received Codex assistance and this video uses synthetic narration.
