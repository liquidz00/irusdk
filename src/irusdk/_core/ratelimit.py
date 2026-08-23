"""Client-side rate limiting.

Pure arithmetic with an injectable clock: no locks, no sleeping. The transports wrap this in
their own lock and sleep with their own primitive, so one implementation serves both.
"""

SECONDS_PER_HOUR = 3600.0


class RateLimitPolicy:
    """
    A dual-window limiter covering Iru's per-second and per-hour tenant quotas.

    The per-second window paces requests evenly rather than allowing a burst followed by a stall.
    The per-hour window is a token bucket that refills continuously.

    :param per_second: Sustained requests per second.
    :type per_second: float
    :param per_hour: Requests permitted per rolling hour.
    :type per_hour: int
    :param now: The current timestamp, from a monotonic clock.
    :type now: float
    """

    def __init__(self, per_second: float, per_hour: int, *, now: float = 0.0) -> None:
        if per_second <= 0 or per_hour <= 0:
            raise ValueError("Rate limits must be positive")

        self.per_second = per_second
        self.per_hour = per_hour
        self._spacing = 1.0 / per_second
        self._refill_rate = per_hour / SECONDS_PER_HOUR
        self._next_slot = now
        self._hour_tokens = float(per_hour)
        self._hour_updated = now

    def acquire_at(self, now: float) -> float:
        """
        Reserve the next request slot and report when it may be sent.

        Mutates the internal counters, so every call must be followed by an actual request.

        :param now: The current timestamp, from a monotonic clock.
        :type now: float
        :return: The timestamp at which the caller may send. May be in the past.
        :rtype: float
        """
        send_at = max(now, self._next_slot, self._hour_available_at(now))
        self._next_slot = send_at + self._spacing
        self._spend_hour_token(send_at)
        return send_at

    def penalize(self, retry_after: float, now: float) -> None:
        """
        Stall the whole bucket after a ``429``.

        Applied to the shared limiter rather than the one worker that was rejected, so concurrent
        workers back off together instead of retrying into the same wall.

        :param retry_after: Seconds the server asked the client to wait.
        :type retry_after: float
        :param now: The current timestamp, from a monotonic clock.
        :type now: float
        """
        self._next_slot = max(self._next_slot, now + max(0.0, retry_after))

    def _hour_available_at(self, now: float) -> float:
        """Earliest timestamp at which the hourly bucket holds a whole token."""
        tokens = self._tokens_at(now)
        if tokens >= 1.0:
            return now
        return now + (1.0 - tokens) / self._refill_rate

    def _tokens_at(self, now: float) -> float:
        """Hourly tokens available at ``now``, without committing the refill."""
        elapsed = max(0.0, now - self._hour_updated)
        return min(float(self.per_hour), self._hour_tokens + elapsed * self._refill_rate)

    def _spend_hour_token(self, at: float) -> None:
        self._hour_tokens = max(0.0, self._tokens_at(at) - 1.0)
        self._hour_updated = at
