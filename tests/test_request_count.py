"""Regression coverage for native counts, opaque data, and budget boundaries."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from inspect_ai.model import ChatMessageUser, GenerateConfig
from inspect_ai.tool import tool

from reproscout.budget import Budget
from reproscout.request_count import count_request, request_sizes


def test_large_serialized_payload_does_not_replace_native_token_count():
    payload = [{"content": [{"type": "reasoning", "redacted": True, "reasoning": "x" * 90000}]}]
    sizes = request_sizes(payload, [])
    assert sizes["legacy_input_bound"] > 60000
    budget = Budget()
    budget.reserve(5000, {"native_input_tokens": 5000, **sizes})
    assert budget.request_checks[-1]["input_token_bound"] == 7048
    assert payload[0]["content"][0]["reasoning"] == "x" * 90000


def test_measured_context_and_money_limits_fail_before_dispatch():
    budget = Budget()
    budget.reserve(57952)
    with pytest.raises(ValueError, match="Measured request token"):
        budget.reserve(57953)
    assert budget.request_checks[-1]["status"] == "context_denied"
    poor = Budget(limit=0.001)
    with pytest.raises(ValueError, match="Insufficient model budget"):
        poor.reserve(1)
    assert poor.spent_upper == 0
    assert poor.request_checks[-1]["status"] == "cost_denied"


def test_native_count_includes_tools_and_refuses_fallback():
    @tool
    def inspect_file():
        async def execute(path: str) -> str:
            """Read a file.

            Args:
                path: File path.
            """
            return path

        return execute

    counter = AsyncMock(return_value=SimpleNamespace(input_tokens=1234))
    client = SimpleNamespace(responses=SimpleNamespace(input_tokens=SimpleNamespace(count=counter)))
    api = SimpleNamespace(
        responses_api=True,
        responses_phase=False,
        api_model_name=lambda: "gpt-5.4-mini-2026-03-17",
        is_latest=lambda: False,
        client=Mock(),
    )
    api.client.with_options.return_value = client
    model = SimpleNamespace(api=api)
    messages = [ChatMessageUser(content="Read the provided file.")]
    config = GenerateConfig(reasoning_effort="low")
    result = asyncio.run(count_request(model, messages, [inspect_file()], config))
    assert result["native_input_tokens"] == 1234
    sent = counter.call_args.kwargs
    assert sent["tools"][0]["name"] == "inspect_file"
    assert sent["input"] and sent["reasoning"] == {"effort": "low"}
    api.client.with_options.assert_called_once_with(max_retries=0, timeout=60)
    counter.side_effect = RuntimeError("count unavailable")
    with pytest.raises(RuntimeError, match="count unavailable"):
        asyncio.run(count_request(model, messages, [inspect_file()], config))
    api.responses_api = False
    with pytest.raises(ValueError, match="no fallback"):
        asyncio.run(count_request(model, messages, [inspect_file()], config))


def test_counter_underestimate_stops_even_when_money_reservation_covers_usage():
    budget = Budget()
    budget.reserve(1)
    with pytest.raises(ValueError, match="input usage exceeded counted token bound"):
        budget.settle({"input_tokens": 3000, "output_tokens": 1}, "test-model")
    assert len(budget.calls) == 1  # Actual incurred usage remains in the ledger.
    assert budget.estimated_billed > 0
