<!-- markdownlint-capture -->
<!-- markdownlint-disable -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **`custom_apps.create` and `.update` now wait out the 503 Iru returns while it finalizes a
  freshly uploaded installer** ("The upload is still being processed"). Without this, every
  create straight after an `upload` failed: the transport does not retry a POST, because a
  POST is not idempotent. Only that one status is waited on, and only for these two calls --
  retrying a create on a dropped connection could make two apps. Exponential backoff capped
  at 30s within a 5-minute budget, matching what the endpoint needs. Found against a live
  tenant; mocks had not covered it.

## [v0.4.0] - 2026-09-25

### Added

- **`custom_apps` writes** — `upload`, `create` and `update`, sync and async. An app is
  written in three steps: reserve a presigned POST, stream the installer to object storage,
  then send Iru the `file_key` that comes back.
- `CustomAppsAPI.upload` streams from disk on a **bare client that carries no Iru
  credentials**. The presigned policy authenticates the upload by itself, and the store is
  not the tenant, so sending the token there would hand a third party fleet-wide write
  access for nothing. Its own timeout has no write limit, because the client default governs
  an API call rather than a multi-hundred-megabyte body.
- **Model** `CustomAppUpload`, re-exported from `irusdk.models`.
- **Error** `PayloadTransferError`, raised when object storage refuses the installer. It is
  not an `APIResponseError`: the failing request went to the store, so its status and body
  are the store's rather than the tenant's.
- `create` and `update` reject the field combinations Iru answers with an unhelpful 400 --
  an audit script without `continuously_enforce`, a `zip` app with no `unzip_location`,
  `no_enforcement` outside Self Service, and Self Service with no category. On an update
  each check is skipped when the field governing it was not supplied, since Iru still holds
  the old value and guessing it would reject valid calls.

## [v0.3.0] - 2026-09-25

### Added

- **`custom_apps`** — read-only: `list` and `get`, sync and async. Model verified field by
  field against a live tenant; all six apps parse with `unknown_fields` empty.
- **Model** `CustomApp`, plus the `InstallType` and `InstallEnforcement` enums, re-exported
  from `irusdk.models`. `audit_script`, `preinstall_script`, `postinstall_script` and
  `unzip_location` are blank-string fields collapsed to `None`; an app with no audit script
  is ordinary. `self_service_category_id` and `self_service_recommended` are absent keys
  rather than nulls unless the app is offered in Self Service.
- `CustomApp.file_basename` strips the storage prefix from `file_key`. The basename still
  carries the token Iru appends on upload, so it changes when the same binary is uploaded
  again; `sha256` is what identifies the content.

### Notes

- Creating and updating apps stays with `iructl`. The installer goes to object storage
  through a presigned POST, which is a larger piece of surface than the rest of this package
  and has no caller here yet.

## [v0.2.0] - 2026-09-19

### Added

- **Library-content authoring**, the scope this SDK previously left to `iructl`. Three new
  services, each with a sync class and an async twin: `custom_scripts`, `custom_profiles`, and
  `self_service`.
- **`custom_scripts`** — full CRUD. The Self Service combinations Iru rejects (`no_enforcement`
  without Self Service, Self Service without a category) raise `ValueError` at spec construction
  rather than arriving as a 400.
- **`custom_profiles`** — full CRUD. `create` and `update` take the `.mobileconfig` as `bytes`;
  reading the file is the caller's business, since `_endpoints` performs no I/O. Omitting the
  payload on `update` leaves the deployed profile alone, which is how a rename or a platform
  change is made without reuploading it.
- **`self_service.categories()`** — read-only; Iru exposes no write. Resolves the category id a
  Self Service script has to name.
- **Multipart request support** — `RequestSpec` gains `data` and `files`, threaded through both
  transports. `json` and `data`/`files` are mutually exclusive, enforced at construction so the
  two transports cannot disagree.
- **Models** `CustomScript`, `CustomProfile`, `SelfServiceCategory`, and the `ExecutionFrequency`
  enum, all re-exported from `irusdk.models`. `CustomScript.remediation_script` is blank-string
  normalized; the API sends `""` rather than `null`.

### Fixed

- `CustomProfile` now declares `runs_on_android` and `runs_on_windows`. A live tenant returns
  both on every profile, always `False`, from a serializer Iru shares across library items.
  They were landing in `unknown_fields`. There is no matching argument on `create` or `update`:
  a `.mobileconfig` cannot target either platform.
- `Content-Type: application/json` is no longer set as a client-wide default header. It overrode
  the per-request `multipart/form-data` boundary httpx generates, which would have sent every
  custom profile upload out mislabelled. httpx now sets the header from the body type, so JSON
  requests are unaffected and bodyless requests no longer carry a spurious one.

### Changed

- **Scope.** Earlier releases left library authoring to `iructl` on the reasoning that content
  authoring and fleet querying are different problems. The querying half still holds; the
  authoring half rested on the assumption that the hard part of authoring is talking to the API,
  and it is not — it is the repository side, which is a decision a repository has to make for
  itself. `irusdk` now owns the API and has no opinion about your filesystem. The durability cost
  of that (Iru maintains `iructl`, so when the API changes they ship the fix) is real and is
  documented rather than dropped. See the scope guide.
- Custom Apps and In-House Apps remain unauthored here; `iructl` still covers them.
- Documented what Iru rewrites on store, verified against a live tenant: three top-level profile
  keys (`PayloadIdentifier`, `PayloadDisplayName`, and `PayloadUUID`, the last regenerated on
  every update so macOS reinstalls), and the trailing newline on script bodies. Everything inside
  `PayloadContent` is stored verbatim.


## [v0.1.0] - 2026-08-24

### Added

- **Sync and async clients** — `IruClient` and `AsyncIruClient`, usable directly or as context
  managers, sharing models, endpoint definitions, and pagination logic.
- **Transparent pagination** with three strategies covering the API's envelope shapes
  (`limit`/`offset` over bare arrays and envelopes, one-based `page`, and opaque cursors), with
  concurrent page prefetch wherever the API reports a total.
- **Rate limiting** against Iru's 50 requests/second and 10,000 requests/hour tenant quotas, with
  `Retry-After` handling and exponential backoff with full jitter on 429 and 5xx responses.
- **Four services**, each with a sync class and an async twin: `devices`, `blueprints`, `users`,
  and `tags`.
- **Pydantic models** for every response shape above, permitting unknown fields so a new API field
  does not break the SDK. Every model is re-exported from `irusdk.models`, and `Model.unknown_fields`
  reports anything the API returned that the model does not declare.
- **Derived model fields** — `Device.os_major`, `Device.os_version_info`,
  `Device.days_since_check_in`, `Blueprint.present_count`, and `Blueprint.present_percent`.
- **Blank-string normalization** on fields where the API sends `""` rather than `null`
  (`Device.asset_tag`, `Device.lost_mode_status`, `User.department`, `User.job_title`, and
  `Blueprint.description`/`icon`/`color`), so a falsiness check means what it looks like.
- **CLI** (`irusdk`, via the `cli` extra) with `devices`, `blueprints`, `users`, and `tags` command
  groups, rendering Rich tables or JSON.
- Typed exception hierarchy under `IruError`, TLS via the OS trust store, and a `py.typed` marker.
- **Documentation** built with Sphinx and the Shibuya theme, covering quickstart, authentication,
  pagination, sync vs async, errors, the CLI, a full API reference, and contributor guides for
  adding an endpoint, scope, and working with the API spec.

### Scope

- `irusdk` covers the **fleet** surface of the Iru API — devices, blueprints, users, and tags. It
  deliberately does not author library content: Iru's own
  [`iructl`](https://github.com/kandji-inc/iructl) handles Custom Apps, Scripts, and Profiles, with
  local repository sync, YAML round-tripping, and presigned package upload. The two compose rather
  than compete.
