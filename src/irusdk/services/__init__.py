"""Service classes: the public, typed surface of the SDK.

Each module here holds a sync class and its async twin adjacent to one another. The twins are
hand-written rather than generated so that signatures, docstrings, and return types stay explicit
for IDEs and Sphinx; ``tests/test_parity.py`` is what guarantees they stay in step.
"""

from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def copy_doc(source: Any) -> Callable[[F], F]:
    """
    Copy a docstring from one method onto another.

    Used on async twins so the prose is written once, on the sync method, without making the
    signatures implicit.

    :param source: The method to copy ``__doc__`` from.
    :rtype: Callable
    """

    def decorate(target: F) -> F:
        target.__doc__ = source.__doc__
        return target

    return decorate
