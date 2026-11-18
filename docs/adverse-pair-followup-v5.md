# Follow-up of the four adverse v4 pairs

These are four previously selected task/repetition pairs on three exposed capsules.
Their follow-up is descriptive and does not replace the sixty-cell primary analysis.
Different model samples and time, as well as the revised lesson bundle, can change
trajectories. Scores and old failures are never overwritten. Original-file hashes
cannot certify copied-code or semantic fidelity.

See the [original diagnosis](lesson-pair-analysis-v4.md) and
[complete comparison](controller-comparison.md).

## capsule-0504157, repetition 2

| Version / condition | Answer solved | Calls | Seconds | Estimated cost | Submitted values |
|---|---|---:|---:|---:|---|
| [v4 A](../reports/runs/20261118T063706044862Z-capsule-0504157-run-A2/report.html) | True | 19 | 125.7 | $0.04928 | `{"q1": 1000}` |
| [v4 B](../reports/runs/20261118T063546423955Z-capsule-0504157-run-B2/report.html) | False | 20 | 75.0 | $0.04646 | `{"q1": "1000 ms"}` |
| [v5 A](../reports/runs/20261118T093218449941Z-capsule-0504157-run-A2/report.html) | False | 20 | 99.9 | $0.04483 | `No submission` |
| [v5 B](../reports/runs/20261118T093113458234Z-capsule-0504157-run-B2/report.html) | True | 13 | 61.0 | $0.02928 | `{"q1": "1000"}` |

New B submits the numeric string `"1000"`, which the unchanged scorer accepts, instead of the old `"1000 ms"`. **It still violates the lesson requiring a JSON number.** Step 006 reads the author display mapping: internal time `250` corresponds to `1000 ms`; this is not a label contradiction. Step 012 calculates EC means from a newly assembled aggregation after the render fails. It omits the author visibility filtering and merge shown in step 011 (author lines 584–594), rather than executing unchanged analytical blocks. Thus the score-format deficit disappears in this sample, but scientific-fidelity and strict output-type compliance remain unresolved. The old A success already involved an edited manuscript copy, so neither the old A score nor the new B score should be treated as an unqualified faithful reproduction. New A has no submission: it reaches the twenty-call limit after rendering/data searches, attempts to switch cacheGitData in a /tmp manuscript copy (009/010), and double-quoted R-variable queries (016–018). The new A/B reversal is therefore partly a change in A, not simply a repaired B formatting deficit.

[New B trajectory](../reports/runs/20261118T093113458234Z-capsule-0504157-run-B2/trajectory.json) · [New A trajectory](../reports/runs/20261118T093218449941Z-capsule-0504157-run-A2/trajectory.json)

## capsule-2708693, repetition 1

| Version / condition | Answer solved | Calls | Seconds | Estimated cost | Submitted values |
|---|---|---:|---:|---:|---|
| [v4 A](../reports/runs/20261118T055452132871Z-capsule-2708693-run-A1/report.html) | True | 19 | 60.3 | $0.03007 | `{"q1": 81, "q2": 620}` |
| [v4 B](../reports/runs/20261118T055556608693Z-capsule-2708693-run-B1/report.html) | False | 20 | 59.0 | $0.05188 | `No submission` |
| [v5 A](../reports/runs/20261118T085034431301Z-capsule-2708693-run-A1/report.html) | False | 20 | 71.8 | $0.05191 | `{"q1": 81, "q2": 21}` |
| [v5 B](../reports/runs/20261118T085150930191Z-capsule-2708693-run-B1/report.html) | True | 14 | 49.9 | $0.03251 | `{"q1": 81, "q2": 620}` |

New B submits `(81, 620)` after a failed render, instead of exhausting twenty calls without a report. It reads the author Table 3 construction (010), checks the denominator conversion (011), and calculates `sum(as.numeric(df$disclosedDenom), na.rm=TRUE)` with protected R variables (012). New A instead submits `(81, 21)`: its repeated double-quoted R commands suffer shell-variable expansion (015/016), and its eventual quoted command (017) counts nonmissing studies rather than the requested denominator total. New B still uses direct targeted arithmetic instead of running the complete manuscript blocks; its PDF-copy attempt (013) fails before copying. This is a correct numeric answer and timely submission, not proof that rendering or full manuscript reproduction succeeded. The A/B reversal is an observed sample, not identification of the causal contribution of one reminder.

[New B trajectory](../reports/runs/20261118T085150930191Z-capsule-2708693-run-B1/trajectory.json) · [New A trajectory](../reports/runs/20261118T085034431301Z-capsule-2708693-run-A1/trajectory.json)

## capsule-9054015, repetition 1

| Version / condition | Answer solved | Calls | Seconds | Estimated cost | Submitted values |
|---|---|---:|---:|---:|---|
| [v4 A](../reports/runs/20261118T052421157449Z-capsule-9054015-run-A1/report.html) | True | 13 | 127.1 | $0.02505 | `{"q1": 90, "q2": 1.24}` |
| [v4 B](../reports/runs/20261118T052632424013Z-capsule-9054015-run-B1/report.html) | False | 7 | 70.8 | $0.01696 | `{"q1": "80%", "q2": 1.24}` |
| [v5 A](../reports/runs/20261118T082023636217Z-capsule-9054015-run-A1/report.html) | True | 11 | 128.6 | $0.02844 | `{"q1": 90, "q2": 1.24}` |
| [v5 B](../reports/runs/20261118T082236563632Z-capsule-9054015-run-B1/report.html) | True | 12 | 146.4 | $0.04212 | `{"q1": 90, "q2": 1.24}` |

New B submits numeric `90` and `1.24`, and passes both unchanged scoring checks; the old B selected `80%` from a different supplemental-table grid. New B executes the full author R script (step 005) and sources it again (007), then reads Table 1 for q2 (009). **Fidelity limitation:** q1 evidence is a newly implemented `1000*(0.005+0.01)*sensitivity*0.8` calculation (010), not a query of the author-generated hypothetical object. The constants/formula match the displayed author calculation for these conditions, but this violates the new instruction against reimplementing scientific computations. Thus the old wrong-table score deficit disappears in this sample, while strict lesson compliance is not established. New A queries the author `hypothetical_test(0.99)` object (009) and also passes. The primary scores are not adjusted by this manual review.

[New B trajectory](../reports/runs/20261118T082236563632Z-capsule-9054015-run-B1/trajectory.json) · [New A trajectory](../reports/runs/20261118T082023636217Z-capsule-9054015-run-A1/trajectory.json)

## capsule-9054015, repetition 2

| Version / condition | Answer solved | Calls | Seconds | Estimated cost | Submitted values |
|---|---|---:|---:|---:|---|
| [v4 A](../reports/runs/20261118T063058891718Z-capsule-9054015-run-A2/report.html) | True | 13 | 133.7 | $0.04269 | `{"q1": "90%", "q2": 1.24}` |
| [v4 B](../reports/runs/20261118T062744402986Z-capsule-9054015-run-B2/report.html) | False | 14 | 190.3 | $0.03378 | `{"q1": "90% sensitivity for both cancers A and B", "q2": 1.24}` |
| [v5 A](../reports/runs/20261118T092553115314Z-capsule-9054015-run-A2/report.html) | True | 14 | 104.4 | $0.03264 | `{"q1": "90%", "q2": "1.24%"}` |
| [v5 B](../reports/runs/20261118T092341047794Z-capsule-9054015-run-B2/report.html) | True | 9 | 128.0 | $0.03469 | `{"q1": 90, "q2": 1.24}` |

New B submits JSON numbers `90` and `1.24`, so the old prose-wrapped `90% sensitivity for both cancers A and B` failure is absent. It executes the original full R script (005), reads the generated Table 1 (006), and attempts a focused query of the author hypothetical function (007). That displayed query output is truncated by its own first-120-lines command and is mostly library messages, so it is not the cited numeric evidence. The actual q1 citation is the captured author-generated figure (008): the 90% curve is visibly highest at prevalence 1%. The preserved image was visually checked for this follow-up. Unlike repetition 1, no replacement scientific formula appears in this B trajectory. This supports the observed formatting/evidence improvement for this sample, without proving general compliance or a causal effect of one lesson. New A also scores correctly, but its cited step 010 uses an inline copy of the author function with the lives-saved computation and LS return column removed; step 012 reconstructs the Table 1 formatting pipeline. Running the original script later (013) does not change the provenance of its submitted evidence. Original hashes therefore must not be read as proof that both conditions performed unchanged science.

[New B trajectory](../reports/runs/20261118T092341047794Z-capsule-9054015-run-B2/trajectory.json) · [New A trajectory](../reports/runs/20261118T092553115314Z-capsule-9054015-run-A2/trajectory.json)

The final observations do not identify the causal contribution of any one lesson. Numeric-format compliance, answer correctness, execution evidence and scientific fidelity remain separate checks.
