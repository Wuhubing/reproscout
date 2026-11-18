"""Bounded, audited retries; generation retries require pre-dispatch DNS evidence."""

import asyncio
import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

DELAYS = (1, 2, 4, 8)


def failure_details(exc):
    chain = []
    seen = set()
    current = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or current.__context__
    dns = any(isinstance(e, socket.gaierror) for e in chain) or any(
        "nodename nor servname" in str(e)
        or "Name or service not known" in str(e)
        or "Temporary failure in name resolution" in str(e)
        for e in chain
    )
    status = getattr(exc, "status_code", None)
    code = getattr(exc, "code", None)
    transport = any(
        type(e).__name__
        in {
            "APIConnectionError",
            "APITimeoutError",
            "ConnectError",
            "ConnectTimeout",
            "ReadTimeout",
            "WriteTimeout",
            "RemoteProtocolError",
        }
        for e in chain
    )
    transient = (
        dns
        or transport
        or status in {408, 409, 500, 502, 503, 504}
        or (status == 429 and code != "insufficient_quota")
    )
    return {
        "error_types": [type(e).__name__ for e in chain],
        "dns_resolution": dns,
        "http_status": status,
        "retryable_count": transient,
    }


def append_event(path: Path | None, event):
    if path is not None:
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event) + "\n")


async def transport_retry(
    operation, *, kind, audit_path=None, request_sha256=None, delays=DELAYS, sleep=asyncio.sleep
):
    """Do not retry ambiguous generation dispatches, auth, or exhausted quota."""
    for attempt in range(len(delays) + 1):
        started = time.monotonic()
        event = {
            "operation": kind,
            "attempt": attempt + 1,
            "at": datetime.now(timezone.utc).isoformat(),
            "request_sha256": request_sha256,
        }
        try:
            result = await operation()
        except Exception as exc:
            details = failure_details(exc)
            retryable = (
                details["retryable_count"]
                if kind == "count"
                else (details["dns_resolution"] and details["http_status"] is None)
            )
            retry = retryable and attempt < len(delays)
            append_event(
                audit_path,
                {
                    **event,
                    **details,
                    "status": "failed",
                    "seconds": time.monotonic() - started,
                    "will_retry": retry,
                    "delay_seconds": delays[attempt] if retry else 0,
                },
            )
            if not retry:
                raise
            await sleep(delays[attempt])
        else:
            append_event(
                audit_path, {**event, "status": "succeeded", "seconds": time.monotonic() - started}
            )
            return result
