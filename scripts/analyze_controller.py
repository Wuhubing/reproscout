"""Audit old controller stops; native counts are measurements, not new generations."""

import argparse
import asyncio
import json
from pathlib import Path
from statistics import median

from inspect_ai.log import read_eval_log
from inspect_ai.model import get_model
from inspect_ai.model._openai_responses import openai_responses_inputs

from reproscout.cli import load_key
from reproscout.request_count import request_sizes
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_key(args.key_file)
    results = json.loads((args.experiment / "results.json").read_text())
    api = get_model(results["runs"][0]["model"]).api
    rows = []
    for run in results["runs"]:
        if "Pilot context limit reached" not in (run.get("sample_error") or ""):
            continue
        sample = read_eval_log(
            str(next((ROOT / "runs" / run["run_id"] / "logs").glob("*.eval"))),
            resolve_attachments=True,
        ).samples[0]
        events = [
            e
            for e in sample.events
            if e.event == "model" and e.output and e.output.usage and e.call
        ]
        last = events[-1]
        schemas = [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters.model_dump(mode="json"),
            }
            for t in last.tools
        ]
        row = {
            "run_id": run["run_id"],
            "task_id": run["task_id"],
            "condition": run["condition"],
            "repeat": run["repeat"],
            "model_calls": run["model_calls"],
            "last_generated_input_tokens": last.output.usage.input_tokens
            + (last.output.usage.input_tokens_cache_read or 0),
            **request_sizes([m.model_dump(mode="json") for m in sample.messages], schemas),
        }
        wire = {
            "model": api.api_model_name(),
            "input": await openai_responses_inputs(
                sample.messages, api, synthesize_phase=api.responses_phase
            ),
            "tools": last.call.request["tools"],
            "reasoning": {"effort": "low"},
            "parallel_tool_calls": False,
        }
        try:
            count = await api.client.with_options(
                max_retries=0, timeout=60
            ).responses.input_tokens.count(**wire)
            row["blocked_native_input_tokens"] = count.input_tokens
            row["new_bound_would_allow"] = count.input_tokens + 2048 <= 60000
        except Exception as exc:
            row["count_error_type"] = type(exc).__name__
        rows.append(row)
        write_json(args.output, {"experiment_id": results["experiment_id"], "rows": rows})
        print(
            f"Measured {len(rows)}: {run['task_id']} {run['condition']}{run['repeat']}", flush=True
        )
    measured = [r for r in rows if "blocked_native_input_tokens" in r]
    output = {
        "experiment_id": results["experiment_id"],
        "stops": len(rows),
        "native_counts_completed": len(measured),
        "native_counts_below_new_bound": sum(r["new_bound_would_allow"] for r in measured),
        "median_legacy_bound": median(r["legacy_input_bound"] for r in rows),
        "median_opaque_bytes": median(r["opaque_reasoning_bytes"] for r in rows),
        "median_native_tokens": median(r["blocked_native_input_tokens"] for r in measured)
        if measured
        else None,
        "native_token_range": [
            min(r["blocked_native_input_tokens"] for r in measured),
            max(r["blocked_native_input_tokens"] for r in measured),
        ]
        if measured
        else None,
        "method": "Post-hoc token counting of the stopped conversation and unchanged tool schemas; no model generation, no replayed score, and no claim that continuation would solve a task.",
        "rows": rows,
    }
    write_json(args.output, output)
    print(json.dumps({k: v for k, v in output.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
