# Scope: fleet, and the content that configures it

`irusdk` is a client for **querying and acting on an Iru fleet** — devices, their state, the
actions you take against them, and the blueprints, users, and tags that organise them — and, as of
0.2.0, for **authoring the library content** that configures it.

Authoring support is landing one resource at a time:

| Library item | Authoring support |
| --- | --- |
| Custom Scripts | available |
| Custom Profiles | available |
| Self Service categories | in progress |
| Custom Apps | planned |
| In-House Apps | not planned |

## The line moved in 0.2.0

Earlier releases deliberately left library authoring to
[`iructl`](https://github.com/kandji-inc/iructl), Iru's own tool, on the reasoning that content
authoring and fleet querying are different problems and the vendor already solved the first one.

The querying half of that argument still holds. The authoring half turned out to rest on an
assumption that does not survive contact with a GitOps repository: that the hard part of authoring
is talking to the API.

It is not. The hard part is the **repository side** — deciding what a component looks like on disk,
which fields a human owns and which the vendor assigns, how a pull reconciles with a working tree,
and what a reviewer sees in a diff. Those are decisions a repository has to make for itself, and
they are not decisions a general-purpose vendor tool can make on any particular repository's
behalf. A tool that is right for every layout is not especially right for yours.

So the split changed shape. It is no longer *fleet here, content there*. It is:

- **`irusdk` owns the API.** Typed calls, one shape for sync and async, pagination, retries,
  errors. It has no opinion about your filesystem and never touches it.
- **Your tooling owns the repository.** Layout, identity, formatting, validation, reconciliation.

That seam is the useful one, because it puts each decision where the information to make it is.

## The cost, stated plainly

The durability argument against this has not gone away, and it is worth keeping visible rather than
quietly dropping now that it is inconvenient:

> `iructl` is maintained by Iru. When the API changes for Custom Apps, the people who changed it
> ship the fix. A third-party SDK cannot match that in the vendor's own domain.

That remains true. Adopting library authoring here means accepting on-call for Iru's API drift in a
surface the vendor also ships a tool for. It is a real cost, taken deliberately, in exchange for
owning the repository-side decisions outright.

If you do not need repository-side control, `iructl` is still the shorter path, and this page is
not an argument that you should switch.

## Blueprints sit in both

Blueprints are fleet context and content target at once. Every device carries a `blueprint_id` and
`blueprint_name`, and blueprint is a primary device filter:

```python
for device in client.devices.list(blueprint_id="ab102b9d-..."):
    ...
```

Blueprint listing, reading, and membership live here. Declarative assignment of library items to
blueprints — the part that belongs to a repository's sync step — does not, and is left to whatever
tooling owns your repository.

## Using both

They still compose, and while authoring support is incomplete there is good reason to:

```console
# iructl for what irusdk does not author yet
$ iructl app pull --all
```

```python
# irusdk for the API, fleet or content
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="...")

for script in client.custom_scripts.list():
    print(script.id, script.name, script.execution_frequency)
```
