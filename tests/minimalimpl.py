from __future__ import annotations

import sys
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )
else:
    from typing import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )

from multicollections.abc import MutableMultiMapping, with_default

K = TypeVar("K")
V = TypeVar("V")


class ListMultiDict(MutableMultiMapping[K, V]):
    def __init__(
        self, iterable: Mapping[K, V] | Iterable[Sequence[K | V]] = (), **kwargs: V
    ) -> None:
        self._items: list[tuple[K, V]] = []
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._items.append((key, value))
        else:
            for key, value in iterable:
                self._items.append((key, value))
        for key, value in kwargs.items():
            self._items.append((key, value))

    @with_default
    def getall(self, key: K) -> list[V]:
        ret = [v for k, v in self._items if k == key]
        if not ret:
            raise KeyError(key)
        return ret

    def __setitem__(self, key: K, value: V) -> None:
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

    def add(self, key: K, value: V) -> None:
        self._items.append((key, value))

    @with_default
    def popone(self, key: K) -> V:
        for i, (k, v) in enumerate(self._items):
            if k == key:
                del self._items[i]
                return v
        raise KeyError(key)

    def __iter__(self) -> Iterator[K]:
        return (k for k, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

