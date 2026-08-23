"""Tenant base-URL construction."""

from enum import StrEnum
from urllib.parse import urlparse, urlunparse

from .errors import ConfigurationError

# Iru still serves the API from the kandji.io domain post-rebrand.
_HOST_TEMPLATES = {
    "us": "{subdomain}.api.kandji.io",
    "eu": "{subdomain}.api.eu.kandji.io",
}


class Region(StrEnum):
    """The Iru tenant region, which determines the API hostname."""

    US = "us"
    EU = "eu"


def resolve_base_url(subdomain: str, region: Region | str = Region.US) -> str:
    """
    Build the tenant API base URL.

    Accepts either a bare subdomain (``"mycompany"``) or the full API URL copied from
    Settings > Access (``"https://mycompany.api.kandji.io"``); the latter is passed through with
    its scheme forced to HTTPS, so ``region`` is ignored in that case.

    :param subdomain: The tenant subdomain, or a full API URL.
    :type subdomain: str
    :param region: The tenant region. Ignored when ``subdomain`` is a full URL.
    :type region: Region | str
    :return: The base URL, without a trailing slash.
    :rtype: str
    :raises ConfigurationError: If the subdomain is empty or the region is unknown.
    """
    if not subdomain or not subdomain.strip():
        raise ConfigurationError("A tenant subdomain or API URL is required")

    value = subdomain.strip().rstrip("/")

    if "." in value or "//" in value:
        parsed = urlparse(value if "//" in value else f"https://{value}")
        if not parsed.netloc:
            raise ConfigurationError("Could not parse the API URL", url=subdomain)
        return urlunparse(("https", parsed.netloc, "", "", "", ""))

    try:
        host = _HOST_TEMPLATES[Region(region).value]
    except ValueError:
        raise ConfigurationError(
            "Unknown region", region=region, supported=", ".join(_HOST_TEMPLATES)
        ) from None

    return f"https://{host.format(subdomain=value)}"
