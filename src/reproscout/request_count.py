"""Count the complete Responses request using the pinned Inspect conversion adapter.

Private conversion helpers are isolated here and pinned to Inspect 0.3.290. No
fallback tokenizer is allowed: opaque reasoning must be counted by the provider.
"""

import hashlib
import json

from inspect_ai.model._openai_responses import openai_responses_inputs, openai_responses_tools
from inspect_ai.tool import ToolDef, ToolInfo

from .network import transport_retry


def request_sizes(messages, schemas):
    """Measure the historical byte bound without exposing opaque payload contents."""
    opaque_bytes = 0

    def transform(value):
        nonlocal opaque_bytes
        if isinstance(value, str) and value.startswith("data:image/"):
            return "X" * 8192
        if isinstance(value, list):
            return [transform(v) for v in value]
        if isinstance(value, dict):
            if value.get("type") == "reasoning" and value.get("redacted"):
                opaque_bytes += len(str(value.get("reasoning", "")).encode())
            return {k: transform(v) for k, v in value.items()}
        return value

    encoded = json.dumps(transform({"messages": messages, "tools": schemas}), ensure_ascii=False)
    return {
        "legacy_input_bound": len(encoded.encode()) + 8192,
        "opaque_reasoning_bytes": opaque_bytes,
    }


async def count_request(model, messages, tools, config, audit_path=None):
    """Count messages, images, encrypted reasoning and tool schemas together."""
    api = model.api
    if not getattr(api, "responses_api", False):
        raise ValueError("Native Responses token counting is required; no fallback is allowed")
    infos = []
    for item in tools:
        definition = ToolDef(item)
        infos.append(
            ToolInfo(
                name=definition.name,
                description=definition.description,
                parameters=definition.parameters,
            )
        )
    wire = {
        "model": api.api_model_name(),
        "input": await openai_responses_inputs(messages, api, synthesize_phase=api.responses_phase),
        "tools": openai_responses_tools(
            infos, api.api_model_name(), config, is_latest=api.is_latest()
        ),
        "reasoning": {"effort": config.reasoning_effort},
        "parallel_tool_calls": False,
    }
    request_digest = hashlib.sha256(json.dumps(wire, sort_keys=True).encode()).hexdigest()
    client = api.client.with_options(max_retries=0, timeout=60)
    response = await transport_retry(
        lambda: client.responses.input_tokens.count(**wire),
        kind="count",
        audit_path=audit_path,
        request_sha256=request_digest,
    )
    schemas = [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters.model_dump(mode="json"),
        }
        for t in infos
    ]
    return {
        "native_input_tokens": response.input_tokens,
        "count_method": "responses.input_tokens.count/full-request",
        "request_sha256": request_digest,
        **request_sizes([m.model_dump(mode="json") for m in messages], schemas),
    }
