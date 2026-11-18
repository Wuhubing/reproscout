# Lesson revision protocol: prepared-v5

## Question and disclosure

Does a conditional, evidence-focused lesson revision reduce observed output-format,
metric-selection, and call-budget failures without encouraging scientific changes?
A receives the same base prompt and no lessons. B receives revision 2. The fifteen
official test capsules, two repetitions, model, tools, inputs, images, scorer, prices,
and limits remain the same as v4. Repeat one runs A then B; repeat two B then A.

The revision is motivated by four adverse v4 pairs on three test capsules. This is
explicit **test-informed method development on an exposed cohort**, not development
based exclusively on training data, a new held-out test, or proof of generalization.
No task-specific answers, identifiers, table names, thresholds, or scientific fixes
are placed in the lessons. Encrypted model reasoning is not interpreted; diagnosis
uses observable tool calls and artifacts. Observed differences do not prove that a
particular old lesson caused the behavior.

## Development comparison, declared before execution

Run all five official training tasks under three arms: fresh A baseline; B with the
unchanged v1 lessons (`development-legacy-v5`); and B with candidate revision 2
(`development-v5`). Baseline A belongs to `development-v5`. Use one repetition per
arm (fifteen scientific outcomes), alternating arm order across tasks. Preserve all
attempts. These small, single-repeat development results are a mechanism check,
not a significance test. Existing training traces may support the revision; no new
formal runs may be inspected to tune it.

Record the candidate, source, configuration, dependency, and manifest hashes before
this comparison. Network preflights and the v4 bounded retry policy apply. A maximum
of three infrastructure attempts share each original cell budget; scientific
failures are final. Failed infrastructure never fills a scientific cell.

Acceptance requires complete development outcomes, successful native-count accounting,
no unresolved infrastructure failure, all candidate runs submitting a report, numeric
non-null values using JSON numbers, candidate answer success at least the legacy B
count and at least three of five, and no changed prepared-input hashes in candidate
runs. Manually inspect candidate tool calls for altered scientific copies or invented
analyses: unchanged original hashes alone are insufficient. Rendering or missing-data
blockers may legitimately remain unsolved. If a candidate fails, retain it and state
the failed criterion before making at most one additional development revision; never
relabel a failed run or silently rerun a scientific outcome. If validation does not
support superiority, state that explicitly even if the operational gate passes.

## Formal freeze and execution

After development acceptance and software checks, commit the implementation and
freeze all execution code, scripts, tests, configurations, manifests, dependency lock,
lessons, development evidence, this protocol, and historical experiment records.
Record source commit, time, prior test exposure, development run IDs, and the unchanged
infrastructure retry policy. Verify the freeze before every formal cell. No model,
lesson, code, or budget amendment is allowed during the sixty scientific outcomes.

The only controller change needed from v4 enables the same shared-budget guard for
v5 experiment IDs. Base prompt, scientific tools, source-hash audit and scoring stay
unchanged. Any reporting changes are prepared before freezing. The original-hash
audit's copied-file blind spot is disclosed; supplemental trajectory review is not
silently substituted for the historical metric.

## Analysis and delivery

Report A/B answer success, paired discordance, original-input integrity, source-copy
concerns, formatting defects, submission absence, controller/network failures, runtime,
and all-attempt estimated cost. Compare v2/v3/v4/v5 without treating v3's DNS aborts as
a valid scientific comparison. Track the four previously adverse pairs separately,
without changing the sixty-cell primary denominator. Descriptive before/after changes
also include model sampling and time effects; thirty pairs reuse only fifteen tasks.

Preserve old releases, experiment files, all failed attempts, and portable trajectories.
Publish English analysis, results app, narration/video, source ZIP, and checksums.
Keep private answers, credentials, author archives, and original binary logs local.
