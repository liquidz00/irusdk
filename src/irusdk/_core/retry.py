"""Transport-agnostic retry policy.

The policy decides *how long* to wait; the transports own the sleeping, so the sync and async
paths share one set of rules.
"""

import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Mapping

# Statuses worth retrying: the tenant quota, and the transient server-side failures.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


def parse_retry_after(value: str | None, *, now: float | None = None) -> float | None:
    """
    Parse a ``Retry-After`` header, which may be a delay in seconds or an HTTP date.

    :param value: The raw header value.
    :type value: str | None
    :param now: Unix timestamp to measure an HTTP-date form against. Defaults to the current time.
    :type now: float | None
    :return: Seconds to wait, or ``None`` if the header was absent or unparseable.
    :rtype: float | None
    """
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    reference = now if now is not None else datetime.now(timezone.utc).timestamp()
    return max(0.0, when.timestamp() - reference)


class RetryPolicy:
    """
    Decides whether and how long to wait before replaying a failed request.

    :param max_retries: Attempts after the initial request.
    :type max_retries: int
    :param backoff_factor: Base for the exponential backoff, in seconds.
    :type backoff_factor: float
    :param max_backoff: Ceiling on any single wait, in seconds.
    :type max_backoff: float
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        max_backoff: float = 60.0,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff

    def delay_for(
        self,
        *,
        attempt: int,
        idempotent: bool,
        status: int | None = None,
        headers: Mapping[str, str] | None = None,
        exc: Exception | None = None,
    ) -> float | None:
        """
        Compute the wait before the next attempt.

        :param attempt: How many attempts have already been made, starting at 1.
        :type attempt: int
        :param idempotent: Whether the request is safe to replay.
        :type idempotent: bool
        :param status: The response status code, if a response was received.
        :type status: int | None
        :param headers: The response headers, consulted for ``Retry-After``.
        :param exc: The transport exception raised, if the request never completed.
        :type exc: Exception | None
        :return: Seconds to wait, or ``None`` to give up and raise.
        :rtype: float | None
        """
        if not idempotent or attempt > self.max_retries:
            return None
        if status is not None and status not in RETRYABLE_STATUS:
            return None
        if status is None and exc is None:
            return None

        retry_after = parse_retry_after((headers or {}).get("Retry-After"))
        if retry_after is not None:
            return min(retry_after, self.max_backoff)

        # Full jitter: spreads a thundering herd of concurrent workers across the window.
        ceiling = min(self.backoff_factor * (2 ** (attempt - 1)), self.max_backoff)
        return random.uniform(0.0, ceiling)
