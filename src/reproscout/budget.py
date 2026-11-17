"""Conservative text-only request reservation around Inspect's model interface."""

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

    def reserve(self, serialized_input_bytes: int) -> float:
        # UTF-8 bytes conservatively bound text tokenization; padding accounts for
        # chat framing and provider schema conversion. Text-only pilot, one call at a time.
        input_bound = serialized_input_bytes + 8192
        if input_bound > 60000:
            raise ValueError("Pilot context limit reached")
        amount = (input_bound * self.input_rate + self.max_output * self.output_rate) / 1e6
        if self.spent_upper + amount > self.limit:
            raise ValueError("Insufficient model budget for the next bounded request")
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
                "model": model,
                "usage": usage,
                "reserved_usd": self.reserved,
                "uncached_upper_usd": upper,
                "estimated_usd": billed,
            }
        )
        if upper > self.reserved:
            raise ValueError("Provider usage exceeded reservation; stop and audit pricing")
        self.reserved = 0.0
