"""Evidence-backed operational hypotheses, independent of answer scores."""

from .review import read
from .tasks import write_json


def diagnose(run):
    summary = read(run, "summary.json", {})
    facts = []
    contributors = []
    signatures = [
        (
            "environment",
            "dependency_or_network",
            [
                "Temporary failure in name resolution",
                "Network is unreachable",
                "ModuleNotFoundError",
                "ImportError",
                "there is no package called",
                "command not found",
                "cannot open shared object",
                "Could not resolve",
                "URLError",
            ],
        ),
        (
            "code_error",
            "execution",
            ["Traceback (most recent call last)", "Error in ", "Execution halted"],
        ),
    ]
    for label, stage, markers in signatures:
        evidence = []
        for path in sorted((run / "artifacts").glob("*.txt")):
            for line, text in enumerate(path.read_text(errors="replace").splitlines(), 1):
                if any(marker in text for marker in markers):
                    evidence.append(
                        {
                            "artifact": str(path.relative_to(run)),
                            "line_start": line,
                            "line_end": line,
                        }
                    )
        if evidence:
            contributors.append({"label": label, "stage": stage, "evidence": evidence})
    timed_out = [
        p.name for p in run.glob("step-*.json") if read(run, p.name, {}).get("status") == "timeout"
    ]
    if (
        summary.get("limit")
        or timed_out
        or any(
            marker in str(summary.get("sample_error", "")).lower()
            for marker in ("limit", "maximum model calls", "budget exhausted")
        )
    ):
        contributors.append(
            {
                "label": "budget_exhausted",
                "stage": "controller",
                "evidence": timed_out or ["summary.json"],
            }
        )
    ledger = read(run, "execution-ledger.json", [])
    for item in ledger:
        if item.get("status") in ("succeeded", "failed", "failed_or_timeout", "refused"):
            facts.append(item)
    result = {
        "schema_version": "1.0",
        "label": contributors[0]["label"] if contributors else None,
        "stage": contributors[0]["stage"] if contributors else "unknown",
        "status": "provisional",
        "primary_cause": "Unconfirmed; inspect the cited trace and execution order.",
        "contributors": contributors,
        "known_facts": facts,
        "evidence": ["summary.json", *(["execution-ledger.json"] if ledger else [])],
        "human_confirmed": False,
        "note": "A matching reference answer does not establish faithful or complete execution. Trace signatures are hypotheses, not confirmed root causes.",
        "next_actions": [
            "Inspect the first failing author step and cited output.",
            "Separate computation output from rendering failure.",
            "Review file changes and the requested metric, object, and units before accepting a candidate.",
        ],
    }
    write_json(run / "diagnosis.json", result)
    return result
