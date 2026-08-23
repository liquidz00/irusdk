"""Pagination strategy logic, tested against synthetic envelopes with no HTTP involved."""

from irusdk._core.pagination import CursorPagination, OffsetPagination, PagePagination


def test_bare_array_reports_no_total() -> None:
    strategy = OffsetPagination()

    result = strategy.parse([{"device_id": "a"}, {"device_id": "b"}])

    assert len(result.items) == 2
    assert result.total is None


def test_bare_array_stops_on_a_short_page() -> None:
    strategy = OffsetPagination()
    short = strategy.parse([{"device_id": "a"}])

    assert strategy.next_params(short, page_size=2, fetched=1) is None


def test_bare_array_continues_on_a_full_page() -> None:
    strategy = OffsetPagination()
    full = strategy.parse([{"device_id": "a"}, {"device_id": "b"}])

    assert strategy.next_params(full, page_size=2, fetched=2) == {"limit": 2, "offset": 2}


def test_bare_array_cannot_be_planned() -> None:
    strategy = OffsetPagination()

    assert strategy.plan(strategy.parse([{"a": 1}]), page_size=1) is None


def test_count_envelope_plans_remaining_offsets() -> None:
    strategy = OffsetPagination(results_key="results", total_key="count")
    first = strategy.parse({"count": 7, "next": None, "results": [{"i": n} for n in range(3)]})

    assert first.total == 7
    assert strategy.plan(first, page_size=3) == [
        {"limit": 3, "offset": 3},
        {"limit": 3, "offset": 6},
    ]


def test_prism_envelope_reads_data_and_total() -> None:
    strategy = OffsetPagination(results_key="data", total_key="total")

    first = strategy.parse(
        {
            "offset": None,
            "limit": 25,
            "total": 60,
            "cursor": None,
            "data": [{"i": n} for n in range(25)],
        }
    )

    assert first.total == 60
    assert len(first.items) == 25
    assert strategy.plan(first, page_size=25) == [
        {"limit": 25, "offset": 25},
        {"limit": 25, "offset": 50},
    ]


def test_page_pagination_plans_remaining_pages() -> None:
    strategy = PagePagination(total_key="count")
    first = strategy.parse({"count": 5, "results": [{"i": 0}, {"i": 1}]})

    assert strategy.first_params(2) == {"page": 1}
    assert strategy.plan(first, page_size=2) == [{"page": 2}, {"page": 3}]


def test_page_size_pagination_includes_the_size_parameter() -> None:
    strategy = PagePagination(total_key="total", size_param="size")
    first = strategy.parse({"total": 3, "page": 1, "size": 2, "results": [{"i": 0}, {"i": 1}]})

    assert strategy.first_params(50) == {"page": 1, "size": 50}
    assert strategy.plan(first, page_size=2) == [{"page": 2, "size": 2}]


def test_cursor_pagination_follows_the_next_url() -> None:
    strategy = CursorPagination()
    first = strategy.parse(
        {
            "next": "https://accuhive.api.kandji.io/api/v1/users?cursor=cD0yOTE0Mw%3D%3D",
            "previous": None,
            "results": [{"id": "1"}],
        }
    )

    assert strategy.next_params(first, page_size=100, fetched=1) == {"cursor": "cD0yOTE0Mw=="}


def test_cursor_pagination_stops_when_next_is_null() -> None:
    strategy = CursorPagination()
    last = strategy.parse({"next": None, "previous": None, "results": [{"id": "1"}]})

    assert strategy.next_params(last, page_size=100, fetched=1) is None


def test_cursor_pagination_is_never_planned() -> None:
    strategy = CursorPagination()
    first = strategy.parse({"next": "https://x/api?cursor=a", "results": [{"id": "1"}]})

    assert strategy.plan(first, page_size=100) is None


def test_cursor_pagination_uses_a_configurable_size_parameter() -> None:
    # /users pages by sizePerPage rather than limit.
    assert CursorPagination(size_param="sizePerPage").first_params(50) == {"sizePerPage": 50}


def test_cursor_pagination_can_send_no_size_parameter() -> None:
    # /tags returns a next URL but documents no page parameter to send.
    assert CursorPagination(size_param=None).first_params(50) == {}
