# irusdk

A Python SDK and thin CLI for **querying and acting on an Iru fleet** — devices, their state, the
actions you take against them, and the blueprints, users, and tags that organise them.

:::{note}
Kandji is now Iru. The API still serves from `*.api.kandji.io`, and this SDK follows suit.
:::

:::{important}
Library authoring arrived in 0.2.0 and is landing one resource at a time — Custom Scripts,
Custom Profiles and Self Service categories today, Custom Apps next. Until then
[`iructl`](https://github.com/kandji-inc/iructl) still covers what this SDK does not, and the two
compose. See {doc}`guide/scope` for where the line now falls and what it costs.
:::

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} {iconify}`lucide:zap` Quickstart
:link: guide/quickstart
:link-type: doc

Install the SDK, authenticate against your tenant, and list your first devices.
:::

:::{grid-item-card} {iconify}`lucide:layers` Pagination
:link: guide/pagination
:link-type: doc

How list methods page for you, and how to take control when you need to.
:::

:::{grid-item-card} {iconify}`lucide:refresh-cw` Sync and async
:link: guide/sync-and-async
:link-type: doc

The same surface in both flavours, and how to choose between them.
:::

:::{grid-item-card} {iconify}`lucide:terminal` CLI
:link: guide/cli
:link-type: doc

Query your tenant from the terminal with `irusdk`.
:::

:::{grid-item-card} {iconify}`lucide:git-compare` Scope
:link: guide/scope
:link-type: doc

What this SDK covers, what it does not yet, and why the line moved in 0.2.0.
:::

::::

## Why this SDK

Nothing currently covers the Iru API from Python as a general client. The `kandji` package on PyPI
is a thin wrapper that has not been updated in four years, and `iructl` reaches only the
library-content endpoints it needs, behind a CLI built around its own repository layout. Devices,
device actions, Prism, users, and tags have had no client at all.

`irusdk` fills that gap:

- **Pydantic models** for API responses, so you get real attributes and IDE autocomplete.
- **Transparent pagination** across all of the API's differing page styles, with concurrent
  prefetch wherever the API reports a total.
- **Sync and async clients** with identical surfaces, guaranteed by a parity test.
- **Rate-limit awareness** for Iru's 50 requests/second and 10,000 requests/hour tenant quotas.

```{toctree}
:hidden:
:caption: Guide

guide/quickstart
guide/scope
guide/authentication
guide/pagination
guide/sync-and-async
guide/errors
guide/cli
```

```{toctree}
:hidden:
:caption: Reference

reference/index
reference/clients
reference/services
reference/models
reference/exceptions
```

```{toctree}
:hidden:
:caption: Contributing

contributing/adding-an-endpoint
contributing/api-spec
```
