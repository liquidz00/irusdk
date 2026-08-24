<!-- markdownlint-capture -->
<!-- markdownlint-disable -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
