"""Exercise the actual Inspect counting adapter and auditable retry recovery."""

import argparse
import asyncio
import json
import socket
import time
from pathlib import Path

from inspect_ai.model import ChatMessageUser, GenerateConfig, get_model

from reproscout.cli import load_key
from reproscout.network import transport_retry
from reproscout.request_count import count_request
from reproscout.tasks import write_json


async def probe(samples, destination, inject=False, interval=2):
    destination.mkdir(parents=True, exist_ok=True)
    model = get_model("openai/gpt-5.4-mini-2026-03-17")
    messages = [ChatMessageUser(content="ReproScout network stability probe.")]
    config = GenerateConfig(reasoning_effort="low")
    rows = []
    for i in range(samples):
        started = time.monotonic()
        result = await count_request(
            model, messages, [], config, destination / "network-events.jsonl"
        )
        rows.append(
            {
                "sample": i + 1,
                "input_tokens": result["native_input_tokens"],
                "seconds": time.monotonic() - started,
            }
        )
        write_json(destination / "progress.json", rows)
        if i + 1 < samples:
            await asyncio.sleep(interval)
    if inject:
        attempts = 0

        async def fail_then_count():
            nonlocal attempts
            attempts += 1
            if attempts <= 2:
                raise socket.gaierror(8, "Injected pre-dispatch DNS failure")
            return await count_request(model, messages, [], config)

        await transport_retry(
            fail_then_count, kind="count", audit_path=destination / "injected-events.jsonl"
        )
        assert attempts == 3
    events = [
        json.loads(line) for line in (destination / "network-events.jsonl").read_text().splitlines()
    ]
    out = {
        "passed": True,
        "samples": samples,
        "injected_dns_failures": 2 if inject else 0,
        "live_failed_attempts": sum(e["status"] == "failed" for e in events),
        "rows": rows,
        "scope": "Bounded observation, not a guarantee of future connectivity.",
    }
    write_json(destination / "validation.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}), flush=True)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=30)
    parser.add_argument("--inject", action="store_true")
    args = parser.parse_args()
    load_key(args.key_file)
    asyncio.run(probe(args.samples, args.output, args.inject))
