"""Shared CLI plumbing: credential resolution and error handling."""

import functools
import os
import sys
from typing import Any, Callable

from .._core.errors import IruError
from ..client import IruClient
from ._console import print_error

ENV_SUBDOMAIN = "IRU_SUBDOMAIN"
ENV_TOKEN = "IRU_API_TOKEN"
ENV_REGION = "IRU_REGION"


def build_client(subdomain: str | None, token: str | None, region: str | None) -> IruClient:
    """
    Construct a client from explicit options, falling back to the environment.

    :param subdomain: The tenant subdomain or full API URL, or ``None`` to read the environment.
    :type subdomain: str | None
    :param token: The API token, or ``None`` to read the environment.
    :type token: str | None
    :param region: The tenant region, or ``None`` to read the environment.
    :type region: str | None
    :rtype: IruClient
    :raises SystemExit: If no subdomain or token can be resolved.
    """
    subdomain = subdomain or os.environ.get(ENV_SUBDOMAIN)
    token = token or os.environ.get(ENV_TOKEN)
    region = region or os.environ.get(ENV_REGION) or "us"

    if not subdomain:
        print_error(f"No tenant given. Pass --subdomain or set {ENV_SUBDOMAIN}.")
        raise SystemExit(2)
    if not token:
        print_error(f"No API token given. Pass --token or set {ENV_TOKEN}.")
        raise SystemExit(2)

    return IruClient(subdomain, token, region=region)


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Turn SDK exceptions into a clean stderr message and a non-zero exit.

    Keeps tracebacks out of the terminal for expected failures such as a bad token or a missing
    device, while leaving genuine bugs to surface normally.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except IruError as exc:
            print_error(str(exc))
            sys.exit(1)

    return wrapper
