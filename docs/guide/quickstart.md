# Quickstart

## Install

```console
$ pip install irusdk          # library only
$ pip install "irusdk[cli]"   # library plus the irusdk command
```

## Get a token

Generate an API token in the Iru console, then find your API URL under **Settings → Access**. It
looks like `https://mycompany.api.kandji.io` (US) or `https://mycompany.api.eu.kandji.io` (EU).

Pass either the subdomain or the whole URL — the client accepts both.

## List some devices

```python
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="...")

for device in client.devices.list(platform="Mac"):
    print(device.device_name, device.serial_number, device.os_version)
```

No `with` block is required — construct the client and use it, the way you would an
`httpx.Client`. Call {meth}`~irusdk.IruClient.close` when you are done to release the connection
pool promptly, or let a context manager do it:

```python
with IruClient(subdomain="mycompany", token="...") as client:
    device = client.devices.get("2cfeb3ac-3b5d-423e-bcff-e2676a3a32da")
```

## Tuning the client

```python
from irusdk import IruClient, IruConfig

config = IruConfig(max_concurrency=10, timeout=60.0, max_retries=5)
client = IruClient(subdomain="mycompany", token="...", region="eu", config=config)
```

See {class}`~irusdk.IruConfig` for every knob.
