"""Describe all A outcome transitions, never infer causality from exposed samples."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = {
    ("capsule-2804717", 1): (
        "wrong_figure_and_unsupported_evidence",
        "V4 submits Time / TS#1; v5 submits Time / leader. V5 step 015 reconstructs Figure 2a, whose red legend is leader, rather than the requested Figure 4 network-density label. Step 016 prints the asserted answers as literal text and is the submitted evidence; this is not computed evidence. Step 018 writes an empty HTML summary. The original-input hash audit misses these new-file and in-memory behaviors.",
    ),
    ("capsule-2708693", 1): (
        "wrong_denominator",
        "V5 spends calls on rendering/pandoc searches and double-quoted R variables (015/016). Step 017 finally obtains protected-variable output but submits 21 nonmissing studies rather than the requested total denominator 620. V4 submits 81 / 620. The failure is scientific-output selection after execution detours, not API transport.",
    ),
    ("capsule-7716865", 2): (
        "reimplemented_subset",
        "V4 submits 1.31. After a render failure, v5 repeatedly rewrites inline functions and temporary calculation scripts, narrows to nonpilot ANOVA rows, and submits rounded 1.435194 -> 1.44 from step 017. That is a different calculation from the requested recalculated table mean. Shell expansion and factor conversions consume calls; the final report is still submitted at twenty calls. Correct old scoring is not by itself proof of faithful old execution.",
    ),
    ("capsule-0504157", 2): (
        "call_cap_and_copy_edit",
        "V5 attempts to change cacheGitData in a /tmp manuscript copy (009/010), searches data and uses double-quoted R variables, then reaches the twenty-call cap without a report. V4 submitted 1000 but also edited a manuscript copy. This is loss of a scored success, not necessarily loss of a fully faithful reproduction.",
    ),
    ("capsule-1724988", 2): (
        "contradicts_own_output",
        "V5 step 005 prints walk/search straightness medians 1.38 / 2.87, yet the report chooses Walk. V4 step 008 prints consistent medians (LSS1 1.3819 / 2.8693; LSS2 1.36875 / 2.8504) and selects Search. V5 has only eight calls, so this is answer/evidence interpretation, not a call cap or missing computation.",
    ),
    ("capsule-2708693", 2): (
        "correct_output_but_no_submission",
        "V5 steps 014 and 017 already print both correct values, 81 and 620. Additional searches/queries consume the twenty-call allowance and the run ends without submission. V4 submitted those values. Available correct output is not equivalent to a completed report.",
    ),
    ("capsule-3262218", 1): (
        "gain_by_timely_submission_with_fidelity_caveat",
        "V4 attempts readRDS, gzfile and then load on the stored object, encounters shell-variable expansion, and never submits. V5 reaches load sooner, computes a targeted count in step 013, and submits 45 after seventeen calls. It still uses a newly assembled calculation rather than the full author manuscript execution; this reverse transition must be retained to avoid selecting only regressions.",
    ),
}


def main():
    groups = []
    for v in ["v4", "v5"]:
        j = json.loads((ROOT / f"experiments/prepared-{v}/results.json").read_text())
        groups.append({(x["task_id"], x["repeat"]): x for x in j["runs"] if x["condition"] == "A"})
    old, new = groups
    records = []
    counts = {"both_solved": 0, "neither_solved": 0, "regressions": 0, "gains": 0}
    text = "# Why the A baseline declined from v4 to v5\n\nA fell from 25/30 to 20/30: six regressions and one reverse transition, over fifteen reused tasks. This is not evidence that B caused A to decline: A receives no B lessons. Different model samples, time, and execution trajectories remain confounders. No significance or independent-task claim applies.\n\n"
    evidence = {}
    for path in ["src/reproscout/agent.py", "src/reproscout/scoring.py", "configs/pilot.json"]:
        a = subprocess.check_output(["git", "show", "v0.4.0:" + path], cwd=ROOT)
        b = subprocess.check_output(["git", "show", "v0.5.0:" + path], cwd=ROOT)
        assert a == b
        evidence[path] = {"identical": True, "sha256": hashlib.sha256(a).hexdigest()}
    text += "The agent prompt/tools implementation, scorer and model/resource configuration are byte-identical between the two releases; their hashes are recorded in the companion JSON. Infrastructure-invalid v3 outcomes do not inform this analysis.\n\n"
    for k, a in old.items():
        b = new[k]
        sa = bool(a["evaluation"].get("solved"))
        sb = bool(b["evaluation"].get("solved"))
        category = (
            "both_solved"
            if sa and sb
            else "neither_solved"
            if not sa and not sb
            else "regressions"
            if sa
            else "gains"
        )
        counts[category] += 1
        if sa == sb:
            continue
        mechanism, note = NOTES[k]
        entry = {
            "task_id": k[0],
            "repeat": k[1],
            "transition": category,
            "mechanism": mechanism,
            "observation": note,
            "runs": {},
        }
        text += f"## {k[0]}, repeat {k[1]} — {category}\n\n{note}\n\n| Version | Solved | Calls | Submitted values | Evidence |\n|---|---|---:|---|---|\n"
        for v, x in [("v4", a), ("v5", b)]:
            folder = ROOT / "reports/runs" / x["run_id"]
            p = folder / "submission.json"
            submission = json.loads(p.read_text()) if p.exists() else None
            entry["runs"][v] = {"summary": x, "submission": submission}
            vals = {q: y["value"] for q, y in submission.items()} if submission else None
            text += f"| {v} | {bool(x['evaluation'].get('solved'))} | {x['model_calls']} | `{json.dumps(vals)}` | [Run](../reports/runs/{x['run_id']}/report.html) |\n"
        records.append(entry)
    text += "\n## Implication for v6\n\nThe baseline remains unchanged. B now tests explicit execution/type capabilities rather than prose alone. Separate scoring, original-execution verification, evidence provenance and semantic review are required: several apparently successful old runs also rewrote scientific calculations. A is marked unverified by the automatic execution-boundary audit unless separate trajectory review supports a narrower claim. Such asymmetric observability must not be called a measured zero fidelity rate for A.\n"
    (ROOT / "docs/baseline-decline-v5.md").write_text(text)
    (ROOT / "reports/baseline-decline-v5.json").write_text(
        json.dumps(
            {
                "counts": counts,
                "unchanged_runtime_evidence": evidence,
                "transitions": records,
                "scope": "Descriptive visible-tool analysis; no hidden reasoning or causal attribution.",
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
