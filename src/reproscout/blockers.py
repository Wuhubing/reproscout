"""Stop repeated author execution after a demonstrated offline dependency failure."""

import re
from pathlib import Path

from .review import read
from .tasks import write_json


def detect_offline_blocker(run: Path, artifacts: dict, execution_id: int) -> dict | None:
    evidence = []
    for name, meta in artifacts.items():
        if meta.get("execution_id") != execution_id or meta.get("kind") != "command_stderr":
            continue
        for number, line in enumerate((run / name).read_text(errors="replace").splitlines(), 1):
            text = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
            network = any(
                m in text.lower()
                for m in (
                    "temporary failure in name resolution",
                    "network is unreachable",
                    "could not resolve host",
                )
            )
            exception = re.match(
                r"^(?:urllib\.error\.)?(?:URLError|ConnectionError):|^(?:curl|wget):", text
            )
            if network and exception:
                evidence.append({"artifact": name, "line_start": number, "line_end": number})
    if not evidence:
        return None
    result = {
        "kind": "offline_dependency",
        "execution_id": execution_id,
        "evidence": evidence,
        "reason": "An original author execution failed while accessing a network dependency in the offline sandbox.",
        "next_action": "Provide the exact author-required data or dependency in a newly prepared input; retain this attempt.",
        "finalization_calls_remaining": 2,
        "automatic_answer": False,
    }
    write_json(run / "blocker.json", result)
    return result


def before_generation(run: Path):
    if (run / "cancel.requested").exists():
        raise ValueError("Run cancelled by user; partial evidence retained")
    blocker = read(run, "blocker.json")
    if blocker:
        if blocker["finalization_calls_remaining"] <= 0:
            raise ValueError("Known offline blocker; finalization allowance exhausted")
        blocker["finalization_calls_remaining"] -= 1
        write_json(run / "blocker.json", blocker)
