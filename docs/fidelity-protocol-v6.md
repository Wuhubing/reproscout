# V6: constrained execution and separate fidelity evaluation

## Scope and exposure

This is a test-informed revision on the same fifteen previously exposed tasks,
not a fresh held-out benchmark. All historical scores and failures remain intact.
A retains the v5 baseline prompt, unrestricted scientific shell, model, scoring,
inputs and resource limits. B replaces arbitrary shell access with controller-owned
operations: list/read files, execute inventoried original author files, inspect
this execution's images and submit typed answers. This is a workflow intervention,
not a lesson-only causal estimate. The historical scorer is unchanged in both arms.

B cannot supply code, shell fragments, environment overrides, alternate loaders,
selected scientific chunks, or arbitrary execution arguments. Every execution
verifies all original input hashes. R Markdown can be rendered or have all R chunks
extracted by knitr and executed without edits; notebooks execute original cells.
Failures are retained. Missing data is a scientific blocker and may produce nulls.
Controller-generated wrappers serialize original outputs; they contain no scientific
formulas or task-specific fixes. Files created by author programs are not assumed
correct merely because they exist. Citation provenance is tracked separately.

## Outcomes, declared before development

1. **Answer correctness:** the unchanged external scorer, including its legacy parsing.
2. **Type compliance:** public-question contracts in answer-types-v6.json; numeric
   values must be finite JSON numbers (not bool/string), numeric lists must contain
   finite numbers, categorical answers must be strings. Null is a blocker, not success.
3. **Execution fidelity:** B's controlled execution ledger, all original hashes,
   successful original execution and output provenance. This verifies an execution
   boundary, not that every author computation is scientifically correct. A's
   unrestricted execution is unverified unless manually supported; observed edits
   are violations. Unknown is never counted as verified.
4. **Evidence support:** non-null B answers must cite stdout or new/changed outputs
   from a successful original execution, not source text, old data, or failed runs.
   Provenance is mechanical; semantic question-to-evidence agreement is separately
   reviewed and can remain unknown. Correctness does not imply semantic support.
5. **Joint outcome:** answer solved AND verified execution/output provenance;
   report as a conservative verified-execution intersection, not universal fidelity.

No post-hoc rescoring of earlier versions. Retain rejected submissions and blocked
operations as events, even if the agent later succeeds. Report nulls and missing
submissions explicitly. No benefit claim from abstention alone.

## Development gate

Run fresh A and B on all five official training tasks (ten scientific cells).
Before formal evaluation require all five B reports, zero accepted type violations,
zero unverified non-null citations, unchanged original input hashes on all B runs,
at least two B answer-solved tasks with verified original execution, and passing
adversarial tests for path/code injection, modified inputs, stale evidence,
boolean/string/nonfinite numbers, and original notebook/R extraction behavior.
Two is a minimum operational gate, not an improvement-over-v5 claim: abstention is
expected where an unchanged author pipeline cannot execute. Do not lower this gate
after observing development. If it fails, retain that candidate and validate a
separately identified revision on all five B tasks before freezing.

## Formal freeze and analysis

Freeze code, tests, configs, type contracts, lessons, development evidence and this
protocol before the sixty cells: fifteen tasks x two conditions x two repetitions.
Reverse A/B order in repetition two. Reuse the existing audited network preflight,
shared-budget infrastructure retry policy and scientific-outcome finality rule.
No mid-run changes or selective scientific reruns. Infrastructure failures do not
fill cells. Compare v4/v5/v6 success, stops, integrity, fidelity, time and cost.
Analyze every v4-A-success/v5-A-failure transition and all reverse transitions,
retaining sampling/time/order caveats. A decline is not evidence of B causation:
A receives no B lessons. Publish full evidence and the complete delivery archive.
