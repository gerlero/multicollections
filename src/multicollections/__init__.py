"""Fully generic `MultiDict` class."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Iterable, Iterator, Mapping
from typing import TypeVar, overload

from ._typing import MappingLike, SupportsGetItem, SupportsKeysAndGetItem, override
from .abc import MultiMapping, MutableMultiMapping, with_default

__version__ = importlib.metadata.version("multicollections")


_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
_T = TypeVar("_T")


class MultiDict(MutableMultiMapping[_K, _V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    @overload
    def __init__(self, iterable: SupportsKeysAndGetItem[_K, _V] = ..., /) -> None: ...

    @overload
    def __init__(
        self: SupportsGetItem[str, _V],
        iterable: SupportsKeysAndGetItem[str, _V] = ...,
        /,
        **kwargs: _V,
    ) -> None: ...

    @overload
    def __init__(self, iterable: Iterable[tuple[_K, _V]] = ..., /) -> None: ...

    @overload
    def __init__(
        self: SupportsGetItem[str, _V],
        iterable: Iterable[tuple[str, _V]] = ...,
        /,
        **kwargs: _V,
    ) -> None: ...

    def __init__(
        self,
        iterable: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Create a MultiDict from another (multi-)mapping, an iterable of key-value pairs, or keyword arguments."""
        match iterable:
            case MappingLike():
                self._items = list(iterable.items())
            case SupportsKeysAndGetItem():
                self._items = [(k, iterable[k]) for k in iterable.keys()]  # noqa: SIM118
            case _:
                self._items = list(iterable)
        self._items.extend(kwargs.items())

        self._key_indices: dict[_K, list[int]] = {}
        if self._items:
            self._rebuild_indices()

    @override
    @with_default
    def getall(self, key: _K, /) -> list[_V]:
        ret = [self._items[i][1] for i in self._key_indices.get(key, [])]
        if not ret:
            raise KeyError(key)
        return ret

    @override
    @with_default
    def getone(self, key: _K, /) -> _V:
        return self._items[self._key_indices[key][0]][1]

    @override
    def __contains__(self, key: object, /) -> bool:
        return key in self._key_indices

    @overload
    def get(self, key: object, /) -> _V | None: ...

    @overload
    def get(self, key: object, default: _D, /) -> _V | _D: ...

    @override
    def get(self, key: object, default: _D | None = None, /) -> _V | _D | None:
        if (indices := self._key_indices.get(key)) is None:
            return default
        return self._items[indices[0]][1]

    @overload
    def setdefault(
        self: MultiDict[_K, _T | None],
        key: _K,
        default: None = None,
        /,
    ) -> _T | None: ...

    @overload
    def setdefault(self, key: _K, default: _V, /) -> _V: ...

    @override
    def setdefault(self, key: _K, default: _D | None = None, /) -> _V | _D | None:
        if (indices := self._key_indices.get(key)) is not None:
            return self._items[indices[0]][1]

        self.add(key, default)  # ty: ignore[invalid-argument-type]
        return default

    @override
    def __setitem__(self, key: _K, value: _V) -> None:
        if (indices := self._key_indices.get(key)) is not None:
            first_index = indices[0]

            self._items[first_index] = (key, value)

            if len(indices) > 1:
                for idx in indices[1:]:
                    self._items[idx] = None  # ty: ignore[invalid-assignment]

                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            self.add(key, value)

    def _rebuild_indices(self) -> None:
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            self._key_indices.setdefault(key, []).append(i)

    @override
    def add(self, key: _K, value: _V, /) -> None:
        index = len(self._items)
        self._key_indices.setdefault(key, []).append(index)
        self._items.append((key, value))

    @override
    @with_default
    def popone(self, key: _K, /) -> _V:
        indices = self._key_indices[key]

        first_index = indices[0]
        value = self._items[first_index][1]

        self._items[first_index] = None  # ty: ignore[invalid-assignment]

        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return value

    @override
    @with_default
    def popall(self, key: _K, /) -> list[_V]:
        indices_to_remove = self._key_indices[key]

        ret = [self._items[i][1] for i in indices_to_remove]

        for idx in indices_to_remove:
            self._items[idx] = None  # ty: ignore[invalid-assignment]

        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return ret

    @override
    def popitem(self) -> tuple[_K, _V]:
        if not self._items:
            msg = "popitem(): multi-mapping is empty"
            raise KeyError(msg)

        key, value = self._items.pop()
        indices = self._key_indices[key]
        indices.pop()
        if not indices:
            del self._key_indices[key]

        return key, value

    @override
    def __delitem__(self, key: _K) -> None:
        indices_to_remove = self._key_indices[key]

        for idx in indices_to_remove:
            self._items[idx] = None  # ty: ignore[invalid-assignment]

        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    @override
    def __iter__(self) -> Iterator[_K]:
        return (k for k, _ in self._items)

    @override
    def __len__(self) -> int:
        return len(self._items)

    @override
    def clear(self) -> None:
        self._items.clear()
        self._key_indices.clear()

    def copy(self) -> MultiDict[_K, _V]:
        """Return a shallow copy of the MultiDict."""
        new_md = MultiDict.__new__(MultiDict)
        new_md._items = self._items.copy()
        new_md._key_indices = {k: v.copy() for k, v in self._key_indices.items()}
        return new_md

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality with another MultiDict or mapping-like object.

        Two `MultiDict` instances (or a `MultiDict` and any `MultiMapping`) are
        considered equal if they contain the same items (including duplicates) in the
        same order.

        For comparison with another `Mapping` object, it is equal if they are the same
        length and for each item in the `MultiDict`, the corresponding key in the
        `Mapping` has the same value.
        """
        match other:
            case MultiDict():
                return self._items == other._items
            case MultiMapping():
                return len(self._items) == len(other) and all(
                    i1 == i2 for i1, i2 in zip(self._items, other.items(), strict=True)
                )
            case Mapping():
                if len(self) != len(other):
                    return False
                try:
                    for k, v in self._items:
                        if other[k] != v:
                            return False
                except KeyError:
                    return False
                return True
            case _:
                return NotImplemented

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self._items)!r})"
