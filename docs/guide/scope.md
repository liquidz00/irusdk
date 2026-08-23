# Scope: fleet, not content

`irusdk` is a client for **querying and acting on an Iru fleet**: devices, their state, the actions
you take against them, and the blueprints, users, and tags that organise them.

It deliberately does **not** author library content — Custom Apps, Custom Scripts, Custom Profiles,
or In-House Apps. For that, use [`iructl`](https://github.com/kandji-inc/iructl), Iru's own tool.

## Why the split

The two problems are genuinely different, and the vendor already solves one of them well.

Authoring library content is a **content lifecycle** problem: you want the payloads in version
control, reviewed in pull requests, and synced to your tenant. `iructl` is built for exactly that —
a local repository of profiles, scripts, and apps, YAML and plist round-tripping, package uploads
through presigned S3 URLs, and declarative blueprint assignment.

Managing a fleet is a **query and act** problem: which Macs are on an old OS, which are missing,
which are out of compliance, what is installed where, and lock or wipe the one that just walked out
of the building. That is read-heavy, pagination-heavy, and spans most of the API surface — and it is
what this SDK is for.

There is also a durability argument. `iructl` is maintained by Iru, so when the API changes for
Custom Apps, the people who changed it ship the fix. A third-party SDK cannot match that in the
vendor's own domain, and pretending otherwise would serve nobody. Anywhere the vendor ships a
supported tool, that tool should win.

## Using both

They compose cleanly, and there is no reason to pick one:

```console
# iructl authors and syncs your library content
$ iructl profile pull --all
$ iructl script push --all
```

```python
# irusdk queries and drives the fleet
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="...")

stale = [d for d in client.devices.list(platform="Mac") if d.os_version.startswith("13.")]
for device in stale:
    print(device.serial_number, device.device_name, device.blueprint_name)
```

## What that means in practice

| Task | Tool |
| --- | --- |
| Version-control your Custom Profiles | `iructl` |
| Upload a new Custom App package | `iructl` |
| Declaratively assign library items to blueprints | `iructl` |
| Find every Mac on an outdated OS | `irusdk` |
| Report FileVault or compliance state across the fleet | `irusdk` |
| Lock, erase, or restart a device | `irusdk` |
| Audit which users have how many devices | `irusdk` |
| Build a dashboard, a Slack bot, or a scheduled report | `irusdk` |

## Blueprints sit in both

Blueprints are the one thing both tools touch, for different reasons.

`iructl` assigns library items *to* blueprints as part of the content lifecycle. `irusdk` reads
blueprints as **fleet context** — every device carries a `blueprint_id` and `blueprint_name`, and
blueprint is a primary device filter:

```python
for device in client.devices.list(blueprint_id="ab102b9d-..."):
    ...
```

So blueprint listing, reading, and membership live here. Authoring the content that goes *into* a
blueprint does not.
