"""Retry safety and terminal infrastructure failures must remain observable."""

import asyncio
import json
import socket
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from reproscout.network import failure_details, transport_retry


def dns_failure():
    error = RuntimeError("transport failed")
    error.__cause__ = socket.gaierror(8, "nodename nor servname provided, or not known")
    return error


def test_dns_recovers_with_identical_operation_and_records_every_attempt(tmp_path):
    operation = AsyncMock(side_effect=[dns_failure(), dns_failure(), "ok"])
    sleep = AsyncMock()
    path = tmp_path / "events.jsonl"
    result = asyncio.run(transport_retry(operation, kind="count", audit_path=path, sleep=sleep))
    assert result == "ok" and operation.await_count == 3
    assert [c.args[0] for c in sleep.await_args_list] == [1, 2]
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert [e["status"] for e in events] == ["failed", "failed", "succeeded"]
    assert all(e["dns_resolution"] for e in events[:2])


def test_persistent_dns_exhaustion_is_recorded_and_raised(tmp_path):
    operation = AsyncMock(side_effect=dns_failure())
    path = tmp_path / "events.jsonl"
    with pytest.raises(RuntimeError):
        asyncio.run(transport_retry(operation, kind="count", audit_path=path, sleep=AsyncMock()))
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(events) == 5 and events[-1]["will_retry"] is False


def test_ambiguous_generation_failure_never_retried():
    class APIConnectionError(Exception):
        pass

    operation = AsyncMock(side_effect=APIConnectionError("read failed"))
    with pytest.raises(APIConnectionError):
        asyncio.run(transport_retry(operation, kind="generation", sleep=AsyncMock()))
    assert operation.await_count == 1


def test_predispatch_dns_generation_retry_is_safe():
    operation = AsyncMock(side_effect=[dns_failure(), SimpleNamespace(usage="retained")])
    result = asyncio.run(transport_retry(operation, kind="generation", sleep=AsyncMock()))
    assert result.usage == "retained" and operation.await_count == 2


@pytest.mark.parametrize("status,code", [(401, None), (403, None), (429, "insufficient_quota")])
def test_nontransient_http_errors_do_not_retry(status, code):
    error = RuntimeError("no retry")
    error.status_code = status
    error.code = code
    assert not failure_details(error)["retryable_count"]
    operation = AsyncMock(side_effect=error)
    with pytest.raises(RuntimeError):
        asyncio.run(transport_retry(operation, kind="count", sleep=AsyncMock()))
    assert operation.await_count == 1
