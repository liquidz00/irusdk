"""Guards the sync and async service surfaces against drift.

The two twins are hand-written so their signatures and return types stay explicit. This is what
stops one from quietly gaining a method, a parameter, or a default the other lacks.
"""

import importlib
import inspect
import pkgutil
from typing import Any

import pytest

import irusdk.services


def _service_pairs() -> list[tuple[str, type, type]]:
    """Every ``(name, sync_class, async_class)`` triple across the services package."""
    pairs = []
    for module_info in pkgutil.iter_modules(irusdk.services.__path__):
        module = importlib.import_module(f"irusdk.services.{module_info.name}")
        for name, obj in vars(module).items():
            if not inspect.isclass(obj) or name.startswith("Async"):
                continue
            if obj.__module__ != module.__name__ or not name.endswith("API"):
                continue
            twin = getattr(module, f"Async{name}", None)
            if twin is not None:
                pairs.append((name, obj, twin))
    return pairs


def _public_methods(cls: type) -> dict[str, Any]:
    return {
        name: member
        for name, member in vars(cls).items()
        if callable(member) and not name.startswith("_")
    }


PAIRS = _service_pairs()


def test_at_least_one_service_pair_exists() -> None:
    assert PAIRS, "no sync/async service pairs were discovered"


@pytest.mark.parametrize(
    ("name", "sync_cls", "async_cls"), PAIRS, ids=lambda v: getattr(v, "__name__", v)
)
def test_method_names_match(name: str, sync_cls: type, async_cls: type) -> None:
    assert set(_public_methods(sync_cls)) == set(_public_methods(async_cls)), (
        f"{name} and Async{name} expose different methods"
    )


@pytest.mark.parametrize(
    ("name", "sync_cls", "async_cls"), PAIRS, ids=lambda v: getattr(v, "__name__", v)
)
def test_signatures_match(name: str, sync_cls: type, async_cls: type) -> None:
    for method_name, sync_method in _public_methods(sync_cls).items():
        async_method = getattr(async_cls, method_name)
        sync_params = list(inspect.signature(sync_method).parameters.values())
        async_params = list(inspect.signature(async_method).parameters.values())

        assert [(p.name, p.kind, p.default) for p in sync_params] == [
            (p.name, p.kind, p.default) for p in async_params
        ], f"{name}.{method_name} and Async{name}.{method_name} have different signatures"


@pytest.mark.parametrize(
    ("name", "sync_cls", "async_cls"), PAIRS, ids=lambda v: getattr(v, "__name__", v)
)
def test_docstrings_are_shared(name: str, sync_cls: type, async_cls: type) -> None:
    for method_name, sync_method in _public_methods(sync_cls).items():
        async_method = getattr(async_cls, method_name)
        assert sync_method.__doc__, f"{name}.{method_name} has no docstring"
        assert async_method.__doc__ == sync_method.__doc__, (
            f"Async{name}.{method_name} is missing @copy_doc"
        )
