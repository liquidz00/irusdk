"""Client-wide tuning knobs."""

import platform
import sys

from pydantic import BaseModel, ConfigDict, Field

from ..__about__ import __version__

# Iru's published tenant limits. The defaults below sit under these deliberately:
# retries and redirects count against the vendor's tally but not always against ours.
API_LIMIT_PER_SECOND = 50
API_LIMIT_PER_HOUR = 10_000

DEFAULT_USER_AGENT = (
    f"irusdk/{__version__} "
    f"{platform.system()}/{platform.release()} "
    f"Python/{sys.version_info.major}.{sys.version_info.minor}"
)


class IruConfig(BaseModel):
    """
    Tuning for transport, concurrency, rate limiting, and retries.

    :ivar timeout: Per-request timeout in seconds.
    :ivar max_concurrency: Ceiling on in-flight requests, used for page prefetch and the httpx
        connection pool.
    :ivar requests_per_second: Client-side throttle. Defaults below Iru's published 50/sec.
    :ivar requests_per_hour: Client-side hourly budget. Defaults below Iru's published 10,000/hr.
    :ivar max_retries: Retry attempts after the initial request, for 429 and 5xx responses.
    :ivar backoff_factor: Base for the exponential backoff between retries, in seconds.
    :ivar max_backoff: Ceiling on any single backoff sleep, in seconds.
    :ivar max_pages: Safety valve for endpoints that return no total, guarding against an
        endpoint that ignores its offset parameter and paginates forever.
    :ivar user_agent: The ``User-Agent`` header sent on every request.
    :ivar verify: TLS verification. ``True`` uses the OS trust store via truststore; a string is
        treated as a path to a CA bundle.
    """

    model_config = ConfigDict(extra="forbid")

    timeout: float = Field(default=30.0, gt=0)
    max_concurrency: int = Field(default=5, ge=1, le=50)
    requests_per_second: float = Field(default=45.0, gt=0)
    requests_per_hour: int = Field(default=9_500, gt=0)
    max_retries: int = Field(default=3, ge=0)
    backoff_factor: float = Field(default=0.5, gt=0)
    max_backoff: float = Field(default=60.0, gt=0)
    max_pages: int = Field(default=10_000, ge=1)
    user_agent: str = DEFAULT_USER_AGENT
    verify: bool | str = True
