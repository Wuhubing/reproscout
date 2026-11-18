"""Compare the exact model-facing A prompt/tool schemas to the v5 release."""

import hashlib
import subprocess
import types
from pathlib import Path

from inspect_ai.tool import ToolDef

from reproscout import agent
from reproscout.budget import Budget
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    old = types.ModuleType("reproscout._baseline_v5")
    exec(
        subprocess.check_output(["git", "show", "v0.5.0:src/reproscout/agent.py"], cwd=ROOT),
        old.__dict__,
    )

    def capture(**kwargs):
        return kwargs

    old.react = capture
    agent.react = capture
    manifest = {"questions": {}, "input_inventory": []}
    config = {"max_model_calls": 20}
    before = old.build_agent(ROOT, manifest, config, Budget())
    after = agent.build_agent(ROOT, manifest, config, Budget())

    def schemas(built):
        result = []
        for t in built["tools"] + [built["submit"].tool]:
            d = ToolDef(t)
            result.append(
                {
                    "name": d.name,
                    "description": d.description,
                    "parameters": d.parameters.model_dump(mode="json"),
                }
            )
        return result

    a, b = schemas(before), schemas(after)
    assert old.INSTRUCTIONS == agent.INSTRUCTIONS and a == b
    hashes = {}
    for name in [
        "configs/pilot.json",
        "src/reproscout/scoring.py",
        "src/reproscout/budget.py",
        "src/reproscout/network.py",
        "src/reproscout/request_count.py",
        "src/reproscout/sandbox.py",
    ]:
        current = (ROOT / name).read_bytes()
        assert current == subprocess.check_output(["git", "show", "v0.5.0:" + name], cwd=ROOT)
        hashes[name] = hashlib.sha256(current).hexdigest()
    write_json(
        ROOT / "reports/baseline-parity-v6.json",
        {
            "passed": True,
            "compared_to": "v0.5.0",
            "prompt_sha256": hashlib.sha256(agent.INSTRUCTIONS.encode()).hexdigest(),
            "A_tool_schemas": b,
            "unchanged_runtime_files": hashes,
            "scope": "Exact A prompt and tool schemas, model/resource config, scorer, budget, transport and sandbox are unchanged. Bookkeeping and separate post-run assessments are new.",
        },
    )
    print("A prompt, all four tool schemas and six runtime/config files match v5.")


if __name__ == "__main__":
    main()
