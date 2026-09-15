from collections.abc import Iterable
from typing import Protocol, overload, runtime_checkable


class _BoundMethodWithDefault[K, V](Protocol):
    @overload
    def __call__(self, key: K, /) -> V: ...

    @overload
    def __call__[D](
        self,
        key: K,
        /,
        default: D,
    ) -> V | D: ...


class MethodWithDefault[Self, K, V](Protocol):
    @overload
    def __call__(
        self,
        obj: Self,
        key: K,
        /,
    ) -> V: ...

    @overload
    def __call__[D](
        self,
        obj: Self,
        key: K,
        /,
        default: D,
    ) -> V | D: ...

    @overload
    def __get__(
        self,
        obj: None,
        objtype: type | None = None,
        /,
    ) -> "MethodWithDefault[Self, K, V]": ...

    @overload
    def __get__(
        self,
        obj: Self,
        objtype: type | None = None,
        /,
    ) -> _BoundMethodWithDefault[K, V]: ...


class SupportsGetItem[K, V](Protocol):
    def __getitem__(self, key: K, /) -> V: ...


@runtime_checkable
class SupportsKeysAndGetItem[K, V](Protocol):
    def keys(self) -> Iterable[K]: ...
    def __getitem__(self, key: K, /) -> V: ...


@runtime_checkable
class MappingLike[K, V](SupportsKeysAndGetItem[K, V], Protocol):
    def items(self) -> Iterable[tuple[K, V]]: ...
