"""Roll up request metrics from shard snapshots."""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ShardMetrics:
    requests: int
    failed_requests: int
    total_latency_ms: int

    def __post_init__(self) -> None:
        if self.requests < 0 or not 0 <= self.failed_requests <= self.requests:
            raise ValueError("invalid request counts")
        if self.total_latency_ms < 0:
            raise ValueError("invalid total latency")
        if self.requests == 0 and self.total_latency_ms != 0:
            raise ValueError("latency requires at least one request")


@dataclass(frozen=True)
class Rollup:
    requests: int
    failed_requests: int
    total_latency_ms: int

    @property
    def success_rate(self) -> Fraction | None:
        if not self.requests:
            return None
        return Fraction(self.requests - self.failed_requests, self.requests)

    @property
    def mean_latency_ms(self) -> Fraction | None:
        if not self.requests:
            return None
        return Fraction(self.total_latency_ms, self.requests)


def roll_up(shards: Iterable[ShardMetrics]) -> Rollup:
    """Combine disjoint request counts and latency, including failed requests."""
    requests = failed_requests = total_latency_ms = 0
    for shard in shards:
        requests += shard.requests
        failed_requests += shard.failed_requests
        total_latency_ms += shard.total_latency_ms
    return Rollup(requests, failed_requests, total_latency_ms)
