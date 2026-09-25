"""Models for the custom app endpoints."""

from enum import StrEnum
from pathlib import PurePosixPath

from pydantic import Field

from .base import BlankAsNone, Model


class InstallType(StrEnum):
    """What kind of installer a custom app carries."""

    PACKAGE = "package"
    ZIP = "zip"
    IMAGE = "image"


class InstallEnforcement(StrEnum):
    """How Iru keeps a custom app installed."""

    INSTALL_ONCE = "install_once"
    CONTINUOUSLY_ENFORCE = "continuously_enforce"
    NO_ENFORCEMENT = "no_enforcement"


class CustomApp(Model):
    """
    A custom app as returned by ``/api/v1/library/custom-apps``.

    :ivar id: The library item's identifier. Iru assigns this on create and ignores any value
        sent with the request.
    :ivar name: The app's name.
    :ivar active: Whether the app is active.
    :ivar install_type: One of :class:`InstallType`. Typed as a string rather than the enum so a
        type Iru adds later is carried through instead of raising; compare against the values.
    :ivar install_enforcement: One of :class:`InstallEnforcement`, typed as a string for the same
        reason.
    :ivar unzip_location: Where a ``zip`` app is expanded. The API sends ``""`` for every other
        install type, which :data:`~irusdk.models.base.BlankAsNone` collapses to ``None``.
    :ivar restart: Whether the device restarts after the app installs.
    :ivar audit_script: The audit script's contents, or ``None`` when the app has none. Blank
        rather than null on the wire. Iru strips the trailing newline on store, so this rarely
        matches a file read from disk byte for byte; compare with ``.rstrip()``.
    :ivar preinstall_script: Runs before the installer. Blank-as-``None`` like the others.
    :ivar postinstall_script: Runs after the installer. Blank-as-``None`` like the others.
    :ivar sha256: The installer's checksum, as Iru recorded it at upload.
    :ivar file_key: The installer's full object path in Iru's storage, tenant prefix and all.
        :attr:`file_basename` is usually what you want.
    :ivar file_url: A download URL for the installer.
    :ivar file_size: The installer's size in bytes.
    :ivar file_updated: When the installer was last uploaded.
    :ivar created_at: When the app was created.
    :ivar updated_at: When the app was last modified.
    :ivar show_in_self_service: Whether the app is offered in Self Service.
    :ivar self_service_category_id: The Self Service category the app appears under. The API
        omits this key entirely unless ``show_in_self_service`` is true.
    :ivar self_service_recommended: Whether the app is featured in Self Service. Omitted
        alongside the category.
    """

    id: str | None = None
    name: str | None = None
    active: bool | None = None
    install_type: str | None = None
    install_enforcement: str | None = None
    unzip_location: BlankAsNone = None
    restart: bool | None = None
    audit_script: BlankAsNone = None
    preinstall_script: BlankAsNone = None
    postinstall_script: BlankAsNone = None
    sha256: str | None = None
    file_key: str | None = None
    file_url: str | None = None
    file_size: int | None = None
    file_updated: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    show_in_self_service: bool | None = None
    self_service_category_id: str | None = None
    self_service_recommended: bool | None = None

    @property
    def file_basename(self) -> str:
        """
        The installer's filename, without the storage prefix ``file_key`` carries.

        Still carries the upload token Iru appends before the extension
        (``AgentTelemetry-1.0.3_d6c50654.pkg``), because that token is part of the stored
        object's name and changes with every upload.

        :rtype: str
        """
        return PurePosixPath(self.file_key).name if self.file_key else ""


class CustomAppUpload(Model):
    """
    The presigned POST handed back by ``/library/custom-apps/upload``.

    The installer does not travel through the Iru API. This endpoint returns a short-lived
    policy for object storage; the bytes go there, and only :attr:`file_key` comes back to
    Iru on the create or update that follows.

    :ivar name: The filename registered with the endpoint.
    :ivar expires: When the policy stops being accepted.
    :ivar post_url: The object store's URL, on a host that is not the tenant's. It must be
        posted to without Iru credentials -- see :meth:`~irusdk.services.custom_apps.CustomAppsAPI.upload`.
    :ivar post_data: The policy fields, which must be sent as form parts ahead of the file.
    :ivar file_key: The object path to hand back to Iru once the bytes are stored.
    """

    name: str | None = None
    expires: str | None = None
    post_url: str | None = None
    post_data: dict[str, str] = Field(default_factory=dict)
    file_key: str | None = None
