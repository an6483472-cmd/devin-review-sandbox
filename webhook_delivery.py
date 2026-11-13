"""Process a delivery job and record how the queue should handle it."""

from collections.abc import Callable
from dataclasses import dataclass


class TemporaryDeliveryError(Exception):
    """The provider is unavailable and the request may be retried."""


class PermanentDeliveryError(Exception):
    """The provider rejected a request that should not be retried."""


@dataclass(frozen=True)
class DeliveryJob:
    destination: str
    payload: bytes
    attempts: int = 0


@dataclass(frozen=True)
class DeliveryResult:
    status: str
    attempts: int
    retry_in_seconds: int | None = None


def deliver(
    job: DeliveryJob,
    send: Callable[[str, bytes], None],
    max_attempts: int = 3,
) -> DeliveryResult:
    """Send once and return delivered, retry, or failed for the job."""
    if max_attempts < 1 or job.attempts < 0:
        raise ValueError("invalid attempt limit or attempt count")
    if job.attempts >= max_attempts:
        return DeliveryResult("failed", job.attempts)

    attempts = job.attempts + 1
    try:
        send(job.destination, job.payload)
    except PermanentDeliveryError:
        return DeliveryResult("delivered", attempts)
    except TemporaryDeliveryError:
        if attempts > max_attempts:
            return DeliveryResult("failed", attempts)
        return DeliveryResult("retry", attempts, retry_in_seconds=30 * attempts)
    return DeliveryResult("delivered", attempts)
