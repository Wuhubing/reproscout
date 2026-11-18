# Why the A baseline declined from v4 to v5

A fell from 25/30 to 20/30: six regressions and one reverse transition, over fifteen reused tasks. This is not evidence that B caused A to decline: A receives no B lessons. Different model samples, time, and execution trajectories remain confounders. No significance or independent-task claim applies.

The agent prompt/tools implementation, scorer and model/resource configuration are byte-identical between the two releases; their hashes are recorded in the companion JSON. Infrastructure-invalid v3 outcomes do not inform this analysis.

## capsule-2804717, repeat 1 — regressions

V4 submits Time / TS#1; v5 submits Time / leader. V5 step 015 reconstructs Figure 2a, whose red legend is leader, rather than the requested Figure 4 network-density label. Step 016 prints the asserted answers as literal text and is the submitted evidence; this is not computed evidence. Step 018 writes an empty HTML summary. The original-input hash audit misses these new-file and in-memory behaviors.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 20 | `{"q1": "Time", "q2": "TS#1"}` | [Run](../reports/runs/20261118T053442366620Z-capsule-2804717-run-A1/report.html) |
| v5 | False | 19 | `{"q1": "Time", "q2": "leader"}` | [Run](../reports/runs/20261118T083053205159Z-capsule-2804717-run-A1/report.html) |
## capsule-2708693, repeat 1 — regressions

V5 spends calls on rendering/pandoc searches and double-quoted R variables (015/016). Step 017 finally obtains protected-variable output but submits 21 nonmissing studies rather than the requested total denominator 620. V4 submits 81 / 620. The failure is scientific-output selection after execution detours, not API transport.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 19 | `{"q1": 81, "q2": 620}` | [Run](../reports/runs/20261118T055452132871Z-capsule-2708693-run-A1/report.html) |
| v5 | False | 20 | `{"q1": 81, "q2": 21}` | [Run](../reports/runs/20261118T085034431301Z-capsule-2708693-run-A1/report.html) |
## capsule-3262218, repeat 1 — gains

V4 attempts readRDS, gzfile and then load on the stored object, encounters shell-variable expansion, and never submits. V5 reaches load sooner, computes a targeted count in step 013, and submits 45 after seventeen calls. It still uses a newly assembled calculation rather than the full author manuscript execution; this reverse transition must be retained to avoid selecting only regressions.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | False | 20 | `null` | [Run](../reports/runs/20261118T060002145955Z-capsule-3262218-run-A1/report.html) |
| v5 | True | 17 | `{"q1": 45}` | [Run](../reports/runs/20261118T085612722688Z-capsule-3262218-run-A1/report.html) |
## capsule-7716865, repeat 2 — regressions

V4 submits 1.31. After a render failure, v5 repeatedly rewrites inline functions and temporary calculation scripts, narrows to nonpilot ANOVA rows, and submits rounded 1.435194 -> 1.44 from step 017. That is a different calculation from the requested recalculated table mean. Shell expansion and factor conversions consume calls; the final report is still submitted at twenty calls. Correct old scoring is not by itself proof of faithful old execution.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 10 | `{"q1": 1.31}` | [Run](../reports/runs/20261118T063444539031Z-capsule-7716865-run-A2/report.html) |
| v5 | False | 20 | `{"q1": 1.44}` | [Run](../reports/runs/20261118T092835302317Z-capsule-7716865-run-A2/report.html) |
## capsule-0504157, repeat 2 — regressions

V5 attempts to change cacheGitData in a /tmp manuscript copy (009/010), searches data and uses double-quoted R variables, then reaches the twenty-call cap without a report. V4 submitted 1000 but also edited a manuscript copy. This is loss of a scored success, not necessarily loss of a fully faithful reproduction.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 19 | `{"q1": 1000}` | [Run](../reports/runs/20261118T063706044862Z-capsule-0504157-run-A2/report.html) |
| v5 | False | 20 | `null` | [Run](../reports/runs/20261118T093218449941Z-capsule-0504157-run-A2/report.html) |
## capsule-1724988, repeat 2 — regressions

V5 step 005 prints walk/search straightness medians 1.38 / 2.87, yet the report chooses Walk. V4 step 008 prints consistent medians (LSS1 1.3819 / 2.8693; LSS2 1.36875 / 2.8504) and selects Search. V5 has only eight calls, so this is answer/evidence interpretation, not a call cap or missing computation.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 12 | `{"q1": "Walk", "q2": "Search"}` | [Run](../reports/runs/20261118T070149109987Z-capsule-1724988-run-A2/report.html) |
| v5 | False | 8 | `{"q1": "Walk", "q2": "Walk"}` | [Run](../reports/runs/20261118T095335368824Z-capsule-1724988-run-A2/report.html) |
## capsule-2708693, repeat 2 — regressions

V5 steps 014 and 017 already print both correct values, 81 and 620. Additional searches/queries consume the twenty-call allowance and the run ends without submission. V4 submitted those values. Available correct output is not equivalent to a completed report.

| Version | Solved | Calls | Submitted values | Evidence |
|---|---|---:|---|---|
| v4 | True | 16 | `{"q1": 81, "q2": 620}` | [Run](../reports/runs/20261118T070521261739Z-capsule-2708693-run-A2/report.html) |
| v5 | False | 20 | `null` | [Run](../reports/runs/20261118T095647497163Z-capsule-2708693-run-A2/report.html) |

## Implication for v6

The baseline remains unchanged. B now tests explicit execution/type capabilities rather than prose alone. Separate scoring, original-execution verification, evidence provenance and semantic review are required: several apparently successful old runs also rewrote scientific calculations. A is marked unverified by the automatic execution-boundary audit unless separate trajectory review supports a narrower claim. Such asymmetric observability must not be called a measured zero fidelity rate for A.
