"""The blocking transport: httpx.Client, a thread pool, and threading locks."""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Iterable, Iterator

import httpx

from .._core.config import IruConfig
from .._core.errors import RATE_LIMIT_STATUS, raise_for_response
from .._core.pagination import Page, PageResult
from .._core.ratelimit import RateLimitPolicy
from .._core.retry import RetryPolicy, parse_retry_after
from .._core.spec import PagedSpec, RequestSpec
from ._common import (
    SerialGuard,
    build_client_kwargs,
    build_result,
    chunked,
    decode_json,
    to_page,
)

logger = logging.getLogger("irusdk")


class SyncTransport:
    """
    Executes :class:`~irusdk._core.spec.RequestSpec` objects against the Iru API.

    :param base_url: The tenant base URL.
    :type base_url: str
    :param token: The tenant API token.
    :type token: str
    :param config: Transport tuning.
    :type config: IruConfig
    """

    def __init__(self, base_url: str, token: str, config: IruConfig) -> None:
        self.base_url = base_url
        self.config = config
        self._client = httpx.Client(**build_client_kwargs(base_url, token, config))
        self._retry = RetryPolicy(config.max_retries, config.backoff_factor, config.max_backoff)
        self._limiter = RateLimitPolicy(
            config.requests_per_second, config.requests_per_hour, now=time.monotonic()
        )
        self._limiter_lock = threading.Lock()

    def close(self) -> None:
        """Release the underlying connection pool. Idempotent."""
        self._client.close()

    def __enter__(self) -> "SyncTransport":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def send(self, spec: RequestSpec[Any]) -> Any:
        """
        Perform a single request and return its validated result.

        :param spec: The call to perform.
        :return: A model instance, a list of them, or the raw body when the spec names no model.
        """
        response = self._request(spec)
        return build_result(spec, decode_json(response))

    def send_raw(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """
        Perform a request outside the spec model, returning the raw response.

        The escape hatch for uploads, multipart bodies, and streaming downloads that do not fit a
        declarative description. Rate limiting and retries still apply.

        :rtype: httpx.Response
        """
        spec = RequestSpec[Any](method=method, path=path)
        return self._request(spec, **kwargs)

    def concurrent(self, handler: Callable[..., Any], arguments: Iterable[Any]) -> Iterator[Any]:
        """
        Run ``handler`` over ``arguments`` in a bounded thread pool, yielding results in order.

        :param handler: The callable to invoke. A dict argument is expanded into keywords.
        :param arguments: One entry per invocation.
        """
        with ThreadPoolExecutor(max_workers=self.config.max_concurrency) as pool:
            futures = [
                pool.submit(handler, **a) if isinstance(a, dict) else pool.submit(handler, a)
                for a in arguments
            ]
            for future in futures:
                yield future.result()

    def iterate(self, spec: PagedSpec[Any]) -> Iterator[Any]:
        """
        Iterate every record of a list endpoint, fetching pages as needed.

        :param spec: The list endpoint to walk.
        :return: The validated records, in page order.
        """
        for page in self.pages(spec):
            yield from page.items

    def pages(self, spec: PagedSpec[Any], *, prefetch: int | None = None) -> Iterator[Page[Any]]:
        """
        Iterate a list endpoint one page at a time.

        The first page is fetched serially. If the strategy can compute the remaining pages up
        front, they are fetched concurrently in bounded batches; otherwise the endpoint is walked
        serially.

        :param spec: The list endpoint to walk.
        :param prefetch: Pages in flight at once. Defaults to the client's ``max_concurrency``.
        :type prefetch: int | None
        """
        strategy = spec.strategy
        window = prefetch or self.config.max_concurrency
        guard = SerialGuard(self.config.max_pages)

        first_raw = self._fetch_page(spec, strategy.first_params(spec.page_size))
        guard.check(first_raw, spec.base.path)
        yield to_page(spec, 0, first_raw)

        if not first_raw.items:
            return

        index = 1
        fetched = len(first_raw.items)

        if (plan := strategy.plan(first_raw, spec.page_size)) is not None:
            # Bounded batches keep this streaming rather than materializing every page at once.
            for batch in chunked(plan, window):
                jobs = [{"params": params} for params in batch]
                for raw in self.concurrent(lambda params: self._fetch_page(spec, params), jobs):
                    yield to_page(spec, index, raw)
                    index += 1
            return

        previous = first_raw
        while (params := strategy.next_params(previous, spec.page_size, fetched)) is not None:
            previous = self._fetch_page(spec, params)
            guard.check(previous, spec.base.path)
            if not previous.items:
                return
            fetched += len(previous.items)
            yield to_page(spec, index, previous)
            index += 1

    def _fetch_page(self, spec: PagedSpec[Any], params: dict[str, Any]) -> PageResult:
        response = self._request(spec.base.with_params(params))
        return spec.strategy.parse(decode_json(response))

    def _request(self, spec: RequestSpec[Any], **kwargs: Any) -> httpx.Response:
        """Send one request, applying the rate limiter and the retry policy."""
        attempt = 1
        while True:
            self._throttle()
            try:
                response = self._client.request(
                    spec.method,
                    spec.path,
                    params=spec.params or None,
                    json=spec.json,
                    data=spec.data,
                    files=spec.files,
                    **kwargs,
                )
            except httpx.RequestError as exc:
                delay = self._retry.delay_for(
                    attempt=attempt, idempotent=spec.is_idempotent, exc=exc
                )
                if delay is None:
                    raise
                logger.debug("Retrying %s %s after %.2fs: %s", spec.method, spec.path, delay, exc)
                time.sleep(delay)
                attempt += 1
                continue

            if response.status_code == RATE_LIMIT_STATUS:
                self._penalize(response)

            if response.is_success:
                return response

            delay = self._retry.delay_for(
                attempt=attempt,
                idempotent=spec.is_idempotent,
                status=response.status_code,
                headers=response.headers,
            )
            if delay is None:
                self._raise(response)
            logger.debug(
                "Retrying %s %s after %.2fs (HTTP %s)",
                spec.method,
                spec.path,
                delay,
                response.status_code,
            )
            time.sleep(delay)
            attempt += 1

    def _raise(self, response: httpx.Response) -> None:
        raise_for_response(
            response.status_code,
            url=str(response.request.url),
            body=decode_json(response),
            retry_after=parse_retry_after(response.headers.get("Retry-After")),
        )

    def _penalize(self, response: httpx.Response) -> None:
        # `or` would swallow an explicit `Retry-After: 0`, so test for None.
        retry_after = parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is None:
            retry_after = 1.0
        with self._limiter_lock:
            self._limiter.penalize(retry_after, time.monotonic())

    def _throttle(self) -> None:
        with self._limiter_lock:
            send_at = self._limiter.acquire_at(time.monotonic())
        if (wait := send_at - time.monotonic()) > 0:
            time.sleep(wait)
