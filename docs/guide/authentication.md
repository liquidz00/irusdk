# Authentication

Iru uses a **static, long-lived bearer token**. There is no OAuth flow, no token exchange, and no
refresh endpoint, so authentication is simply a matter of getting the token to the client.

```python
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="your-api-token")
```

## Regions

Tenants live in one of two regions, which determines the hostname:

| Region | Base URL |
| --- | --- |
| US (default) | `https://{subdomain}.api.kandji.io` |
| EU | `https://{subdomain}.api.eu.kandji.io` |

```python
client = IruClient(subdomain="mycompany", token="...", region="eu")
```

If you paste the full URL from **Settings → Access**, the region argument is ignored and the URL is
used as given (with the scheme forced to HTTPS):

```python
client = IruClient(subdomain="https://mycompany.api.eu.kandji.io", token="...")
```

## Keeping the token out of your code

The CLI reads `IRU_SUBDOMAIN`, `IRU_API_TOKEN`, and `IRU_REGION` from the environment. For library
use, do the same:

```python
import os

from irusdk import IruClient

client = IruClient(
    subdomain=os.environ["IRU_SUBDOMAIN"],
    token=os.environ["IRU_API_TOKEN"],
)
```

On macOS, `keyring` is a good place to keep the token so it never lands in a dotfile:

```python
import keyring

token = keyring.get_password("irusdk", "mycompany")
```

## Permissions

API tokens carry scopes assigned in the Iru console. A token missing a scope produces a
{class}`~irusdk.AuthenticationError` on `403`, not an empty result — so an unexpected
`AuthenticationError` usually means a missing scope rather than a bad token.
