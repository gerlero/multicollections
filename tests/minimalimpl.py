from collections.abc import Iterable, Iterator, Mapping
from typing import overload, override

from multicollections._typing import (
    MappingLike,
    SupportsGetItem,
    SupportsKeysAndGetItem,
)
from multicollections.abc import MutableMultiMapping, with_default


class ListMultiDict[K, V](MutableMultiMapping[K, V]):
    @overload
    def __init__(self, iterable: SupportsKeysAndGetItem[K, V] = ..., /) -> None: ...

    @overload
    def __init__(
        self: SupportsGetItem[str, V],
        iterable: SupportsKeysAndGetItem[str, V] = ...,
        /,
        **kwargs: V,
    ) -> None: ...

    @overload
    def __init__(self, iterable: Iterable[tuple[K, V]] = ..., /) -> None: ...

    @overload
    def __init__(
        self: SupportsGetItem[str, V],
        iterable: Iterable[tuple[str, V]] = ...,
        /,
        **kwargs: V,
    ) -> None: ...

    def __init__(
        self, iterable: Mapping[K, V] | Iterable[tuple[K, V]] = (), /, **kwargs: V
    ) -> None:
        match iterable:
            case MappingLike():
                self._items = list(iterable.items())
            case SupportsKeysAndGetItem():
                self._items = [(k, iterable[k]) for k in iterable.keys()]  # noqa: SIM118
            case _:
                self._items = list(iterable)

        self._items.extend(kwargs.items())

    @override
    @with_default
    def getall(self, key: K, /) -> list[V]:
        ret = [v for k, v in self._items if k == key]
        if not ret:
            raise KeyError(key)
        return ret

    @override
    def __setitem__(self, key: K, value: V, /) -> None:
        replaced: int | None = None
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                replaced = i
                break

        if replaced is not None:
            self._items = [
                (k, v)
                for i, (k, v) in enumerate(self._items)
                if i == replaced or k != key
            ]
        else:
            self._items.append((key, value))

    @override
    def add(self, key: K, value: V, /) -> None:
        self._items.append((key, value))

    @override
    @with_default
    def popone(self, key: K, /) -> V:
        for i, (k, v) in enumerate(self._items):
            if k == key:
                del self._items[i]
                return v
        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[K]:
        return (k for k, _ in self._items)

    @override
    def __len__(self) -> int:
        return len(self._items)
