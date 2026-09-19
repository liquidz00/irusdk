"""Unit tests for the pure policies in ``irusdk._core``."""

import pytest

from irusdk import ConfigurationError, Region
from irusdk._core.ratelimit import RateLimitPolicy
from irusdk._core.retry import RetryPolicy, parse_retry_after
from irusdk._core.spec import RequestSpec, drop_none
from irusdk._core.urls import resolve_base_url


@pytest.mark.parametrize(
    ("subdomain", "region", "expected"),
    [
        ("accuhive", Region.US, "https://accuhive.api.kandji.io"),
        ("accuhive", "us", "https://accuhive.api.kandji.io"),
        ("accuhive", Region.EU, "https://accuhive.api.eu.kandji.io"),
        ("https://accuhive.api.kandji.io", Region.US, "https://accuhive.api.kandji.io"),
        ("https://accuhive.api.kandji.io/", Region.EU, "https://accuhive.api.kandji.io"),
        ("accuhive.api.eu.kandji.io", Region.US, "https://accuhive.api.eu.kandji.io"),
        ("http://accuhive.api.kandji.io", Region.US, "https://accuhive.api.kandji.io"),
    ],
)
def test_resolves_base_urls(subdomain: str, region: Region | str, expected: str) -> None:
    assert resolve_base_url(subdomain, region) == expected


def test_rejects_an_unknown_region() -> None:
    with pytest.raises(ConfigurationError, match="Unknown region"):
        resolve_base_url("accuhive", "apac")


def test_drops_none_parameters() -> None:
    assert drop_none(a=1, b=None, c=False) == {"a": 1, "c": False}


@pytest.mark.parametrize(
    ("method", "expected"),
    [("GET", True), ("PUT", True), ("DELETE", True), ("POST", False), ("PATCH", False)],
)
def test_idempotency_defaults_from_the_method(method: str, expected: bool) -> None:
    assert RequestSpec(method=method, path="/x").is_idempotent is expected


def test_idempotency_can_be_overridden() -> None:
    assert RequestSpec(method="POST", path="/x", idempotent=True).is_idempotent is True


def test_json_and_files_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="either json or data/files"):
        RequestSpec(method="POST", path="/x", json={"a": 1}, files={"f": ("n", b"")})


def test_with_params_carries_the_body_through() -> None:
    spec = RequestSpec(method="POST", path="/x", data={"name": "n"}, files={"f": ("n", b"")})

    assert spec.with_params({"page": 2}).data == {"name": "n"}
    assert spec.with_params({"page": 2}).files == {"f": ("n", b"")}


def test_with_params_merges_over_existing_ones() -> None:
    spec = RequestSpec(method="GET", path="/x", params={"platform": "Mac", "limit": 10})

    merged = spec.with_params({"limit": 300, "offset": 300})

    assert merged.params == {"platform": "Mac", "limit": 300, "offset": 300}
    assert spec.params == {"platform": "Mac", "limit": 10}, "the original must not be mutated"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("5", 5.0), ("0", 0.0), (None, None), ("", None), ("not-a-date", None)],
)
def test_parses_retry_after_seconds(value: str | None, expected: float | None) -> None:
    assert parse_retry_after(value) == expected


def test_parses_retry_after_http_date() -> None:
    # 10 seconds past the epoch, measured from the epoch.
    assert parse_retry_after("Thu, 01 Jan 1970 00:00:10 GMT", now=0.0) == 10.0


def test_retry_gives_up_after_max_retries() -> None:
    policy = RetryPolicy(max_retries=2)

    assert policy.delay_for(attempt=2, idempotent=True, status=500) is not None
    assert policy.delay_for(attempt=3, idempotent=True, status=500) is None


def test_retry_skips_non_idempotent_requests() -> None:
    assert RetryPolicy().delay_for(attempt=1, idempotent=False, status=500) is None


def test_retry_skips_non_retryable_statuses() -> None:
    assert RetryPolicy().delay_for(attempt=1, idempotent=True, status=404) is None


def test_retry_prefers_the_retry_after_header() -> None:
    policy = RetryPolicy(max_backoff=60.0)

    delay = policy.delay_for(attempt=1, idempotent=True, status=429, headers={"Retry-After": "7"})

    assert delay == 7.0


def test_retry_caps_the_retry_after_header() -> None:
    policy = RetryPolicy(max_backoff=5.0)

    delay = policy.delay_for(attempt=1, idempotent=True, status=429, headers={"Retry-After": "600"})

    assert delay == 5.0


def test_retry_backoff_stays_within_its_ceiling() -> None:
    policy = RetryPolicy(max_retries=10, backoff_factor=1.0, max_backoff=8.0)

    for attempt in range(1, 6):
        delay = policy.delay_for(attempt=attempt, idempotent=True, status=503)
        assert 0.0 <= delay <= 8.0


def test_rate_limiter_paces_the_per_second_window() -> None:
    limiter = RateLimitPolicy(per_second=10, per_hour=1_000_000, now=0.0)

    slots = [limiter.acquire_at(0.0) for _ in range(3)]

    assert slots == pytest.approx([0.0, 0.1, 0.2])


def test_rate_limiter_enforces_the_hourly_budget() -> None:
    limiter = RateLimitPolicy(per_second=1_000_000, per_hour=2, now=0.0)

    limiter.acquire_at(0.0)
    limiter.acquire_at(0.0)
    third = limiter.acquire_at(0.0)

    # The bucket refills at 2/hour, so the third request waits half an hour.
    assert third == pytest.approx(1800.0, rel=1e-3)


def test_rate_limiter_penalty_stalls_the_whole_bucket() -> None:
    limiter = RateLimitPolicy(per_second=1000, per_hour=1_000_000, now=0.0)

    limiter.penalize(retry_after=30.0, now=10.0)

    assert limiter.acquire_at(10.0) == pytest.approx(40.0)


def test_rate_limiter_rejects_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        RateLimitPolicy(per_second=0, per_hour=100)
