"""The ``irusdk`` command-line interface.

Requires the ``cli`` extra: ``pip install irusdk[cli]``.
"""

try:
    import click
    import rich.traceback
except ModuleNotFoundError as exc:  # pragma: no cover - depends on how the package was installed
    raise SystemExit(
        "The irusdk CLI requires the 'cli' extra. Install it with: pip install 'irusdk[cli]'"
    ) from exc

from ..__about__ import __version__
from ._helpers import ENV_REGION, ENV_SUBDOMAIN, ENV_TOKEN
from .blueprints import blueprints
from .devices import devices
from .tags import tags
from .users import users

# show_locals=False keeps pasted tracebacks token-safe; suppress collapses click's own frames.
rich.traceback.install(show_locals=False, suppress=[click])

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS, options_metavar="<options>", no_args_is_help=True)
@click.version_option(__version__, "-v", "--version", prog_name="irusdk")
@click.option("--subdomain", envvar=ENV_SUBDOMAIN, help="Tenant subdomain or full API URL.")
@click.option("--token", envvar=ENV_TOKEN, help="Tenant API token.")
@click.option("--region", envvar=ENV_REGION, type=click.Choice(["us", "eu"]), help="Tenant region.")
@click.pass_context
def cli(ctx: click.Context, subdomain: str | None, token: str | None, region: str | None) -> None:
    """A command-line client for the Iru (formerly Kandji) Endpoint Management API.

    Credentials are read from IRU_SUBDOMAIN, IRU_API_TOKEN, and IRU_REGION unless overridden.
    """
    ctx.obj = {"subdomain": subdomain, "token": token, "region": region}


for _command in (devices, blueprints, users, tags):
    cli.add_command(_command)

__all__ = ["cli"]
