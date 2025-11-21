from __future__ import annotations

import sys
from typing import Protocol, TypeVar, overload, runtime_checkable

if sys.version_info >= (3, 9):
    from collections.abc import Callable, Iterable
else:
    from typing import Callable, Iterable

if sys.version_info >= (3, 12):
    from typing import override
else:
    try:
        from typing_extensions import override
    except ImportError:  # pragma: nocover

        def override(meth: Callable, /) -> Callable:
            """Fallback override decorator that does nothing."""
            return meth


_Self = TypeVar("_Self")
_K_contra = TypeVar("_K_contra", contravariant=True)
_V_co = TypeVar("_V_co", covariant=True)
_D = TypeVar("_D")


class MethodWithDefault(Protocol[_K_contra, _V_co]):
    @overload
    def __call__(self: _Self, key: _K_contra, /) -> _V_co: ...

    @overload
    def __call__(self: _Self, key: _K_contra, /, default: _D) -> _V_co | _D: ...


_K = TypeVar("_K")


@runtime_checkable
class SupportsKeysAndGetItem(Protocol[_K, _V_co]):
    def keys(self) -> Iterable[_K]: ...
    def __getitem__(self, key: _K, /) -> _V_co: ...


@runtime_checkable
class MappingLike(SupportsKeysAndGetItem[_K, _V_co], Protocol):
    def items(self) -> Iterable[tuple[_K, _V_co]]: ...


__all__ = ["MappingLike", "MethodWithDefault", "SupportsKeysAndGetItem", "override"]
