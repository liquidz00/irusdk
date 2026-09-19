"""Self Service service, exercised against both clients.

The categories endpoint returns a bare JSON array with no envelope, which is the one response
shape none of the paginated services cover.
"""

import httpx
import respx

from conftest import BASE_URL, ClientAdapter

CATEGORIES = f"{BASE_URL}/api/v1/self-service/categories"

PAYLOAD = [
    {"id": "e9010a08-a546-470b-a633-04ee27dadfb3", "name": "Apps"},
    {"id": "1087f69d-37a3-44f6-a0d8-2b33f5a336bb", "name": "Productivity"},
]


@respx.mock
def test_categories_parses_a_bare_array(any_client: ClientAdapter) -> None:
    respx.get(CATEGORIES).mock(return_value=httpx.Response(200, json=PAYLOAD))

    categories = any_client.call(any_client.client.self_service.categories)

    assert [c.name for c in categories] == ["Apps", "Productivity"]
    assert categories[0].id == "e9010a08-a546-470b-a633-04ee27dadfb3"


@respx.mock
def test_categories_handles_an_empty_tenant(any_client: ClientAdapter) -> None:
    respx.get(CATEGORIES).mock(return_value=httpx.Response(200, json=[]))

    assert list(any_client.call(any_client.client.self_service.categories)) == []
