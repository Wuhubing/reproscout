"""Token-aware request reservations with separate context and monetary limits."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Budget:
    limit: float = 1.0
    input_rate: float = 0.75
    output_rate: float = 4.50
    cached_rate: float = 0.075
    max_output: int = 4096
    spent_upper: float = 0.0
    estimated_billed: float = 0.0
    reserved: float = 0.0
    calls: list = field(default_factory=list)
    request_checks: list = field(default_factory=list)
    max_input_tokens: int = 60000
    framing_allowance: int = 2048
    pending: dict = field(default_factory=dict)

    def reserve(self, input_tokens: int, metadata: dict | None = None) -> float:
        if input_tokens < 0:
            raise ValueError("Input token count cannot be negative")
        # Native full-request counting plus a fixed margin; output is reserved separately.
        input_bound = input_tokens + self.framing_allowance
        check = {
            **(metadata or {}),
            "input_token_bound": input_bound,
            "input_limit": self.max_input_tokens,
            "status": "pending",
        }
        self.request_checks.append(check)
        if input_bound > self.max_input_tokens:
            check["status"] = "context_denied"
            raise ValueError("Measured request token limit reached")
        amount = (input_bound * self.input_rate + self.max_output * self.output_rate) / 1e6
        if self.spent_upper + amount > self.limit:
            check["status"] = "cost_denied"
            raise ValueError("Insufficient model budget for the next bounded request")
        check.update(status="reserved", reserved_usd=amount)
        self.pending = dict(check)
        self.reserved = amount
        self.spent_upper += amount  # retain reservation on ambiguous API failures
        return amount

    def settle(self, usage: dict, model: str) -> None:
        input_tokens = usage["input_tokens"]
        cache_write = usage.get("input_tokens_cache_write") or 0
        output_tokens = usage["output_tokens"]
        cached = usage.get("input_tokens_cache_read") or 0
        upper = (
            (input_tokens + cached + cache_write) * self.input_rate
            + output_tokens * self.output_rate
        ) / 1e6
        billed = (
            (input_tokens + cache_write) * self.input_rate
            + cached * self.cached_rate
            + output_tokens * self.output_rate
        ) / 1e6
        self.spent_upper += upper - self.reserved
        self.estimated_billed += billed
        self.calls.append(
            {
                **self.pending,
                "status": "settled",
                "model": model,
                "usage": usage,
                "reserved_usd": self.reserved,
                "uncached_upper_usd": upper,
                "estimated_usd": billed,
            }
        )
        actual_input = input_tokens + cached + cache_write
        if actual_input > self.pending["input_token_bound"]:
            raise ValueError("Provider input usage exceeded counted token bound; stop and audit")
        self.request_checks[-1]["status"] = "settled"
        if upper > self.reserved:
            raise ValueError("Provider usage exceeded reservation; stop and audit pricing")
        self.reserved = 0.0
