"""Fully generic `MultiDict` class."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Iterable, Iterator, Mapping
from typing import TypeVar, overload

from ._typing import SupportsKeysAndGetItem, override
from .abc import (
    MultiMapping,
    MutableMultiMapping,
    _updated_items,
    _yield_items,
    with_default,
)

__version__ = importlib.metadata.version("multicollections")


_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
_T = TypeVar("_T")


class MultiDict(MutableMultiMapping[_K, _V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    def __init__(
        self,
        iterable: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Create a MultiDict."""
        self._items: list[tuple[_K, _V]] = list(_yield_items(iterable, **kwargs))
        self._key_indices: dict[_K, list[int]] = {}

        # Build indices in one pass for better performance
        if self._items:
            self._rebuild_indices()

    @override
    @with_default
    def getall(self, key: _K, /) -> list[_V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self._items[i][1] for i in self._key_indices.get(key, [])]
        if not ret:
            raise KeyError(key)
        return ret

    @override
    @with_default
    def getone(self, key: _K, /) -> _V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return self._items[self._key_indices[key][0]][1]

    @override
    def __contains__(self, key: object, /) -> bool:
        """Check if a key exists in the multi-mapping.

        This is optimized to directly check the key indices without
        calling __getitem__, avoiding exception handling overhead.
        """
        return key in self._key_indices

    @overload
    def get(self, key: object, /) -> _V | None: ...

    @overload
    def get(self, key: object, default: _D, /) -> _V | _D: ...

    @override
    def get(self, key: object, default: _D | None = None, /) -> _V | _D | None:
        """Get the first value for a key, or a default value if not found."""
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
        """Get the first value for a key, or set and return a default if not found."""
        if (indices := self._key_indices.get(key)) is not None:
            # Key exists, return its first value
            return self._items[indices[0]][1]
        # Key doesn't exist, add it with the default value
        self.add(key, default)  # ty: ignore[invalid-argument-type]
        return default

    @override
    def __setitem__(self, key: _K, value: _V, /) -> None:
        """Set the value for a key.

        Replaces the first value for a key if it exists; otherwise, it adds a new item.
        Any other items with the same key are removed.
        """
        if (indices := self._key_indices.get(key)) is not None:
            # Key exists, replace first occurrence and remove others
            first_index = indices[0]

            # Update the first occurrence
            self._items[first_index] = (key, value)

            if len(indices) > 1:
                # Remove duplicates efficiently by marking items as None and filtering
                for idx in indices[1:]:
                    self._items[idx] = None  # ty: ignore[invalid-assignment]

                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            # Key doesn't exist, add it
            self.add(key, value)

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            self._key_indices.setdefault(key, []).append(i)

    @override
    def add(self, key: _K, value: _V, /) -> None:
        """Add a new value for a key."""
        index = len(self._items)
        self._items.append((key, value))
        self._key_indices.setdefault(key, []).append(index)

    @override
    @with_default
    def popone(self, key: _K, /) -> _V:
        """Remove and return the first value for a key."""
        indices = self._key_indices[key]

        first_index = indices[0]
        value = self._items[first_index][1]

        # Mark the first item for removal
        self._items[first_index] = None  # ty: ignore[invalid-assignment]

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return value

    @override
    @with_default
    def popall(self, key: _K, /) -> list[_V]:
        """Remove and return all values for a key."""
        indices_to_remove = self._key_indices[key]

        ret = [self._items[i][1] for i in indices_to_remove]

        # Mark items for removal
        for idx in indices_to_remove:
            self._items[idx] = None  # ty: ignore[invalid-assignment]

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return ret

    @override
    def popitem(self) -> tuple[_K, _V]:
        """Remove and return the last (key, value) pair.

        Raises a `KeyError` if the MultiDict is empty.
        """
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
    def __delitem__(self, key: _K, /) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        indices_to_remove = self._key_indices[key]

        # Mark items for removal
        for idx in indices_to_remove:
            self._items[idx] = None  # ty: ignore[invalid-assignment]

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    @override
    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)

    @override
    def clear(self) -> None:
        """Remove all items from the multi-mapping."""
        self._items.clear()
        self._key_indices.clear()

    @override
    def update(
        self,
        other: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Update the multi-mapping with items from another object.

        Values for keys that already exist replace them in place, keeping their
        positions; values for new keys are appended.
        """
        # Collect all items first
        updates = list(_yield_items(other, **kwargs))

        if not updates:
            return

        self._items = _updated_items(self._items, updates, self._key_indices)
        self._rebuild_indices()

    @override
    def merge(
        self,
        other: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be added.
        """
        # Get existing keys once for efficiency
        existing_keys = set(self._key_indices.keys())

        # Collect all items and filter out existing keys
        new_items = [
            (key, value)
            for key, value in _yield_items(other, **kwargs)
            if key not in existing_keys
        ]

        if not new_items:
            return

        # Add all items to the list at once
        start_index = len(self._items)
        self._items.extend(new_items)

        # Update indices incrementally for better performance
        for i, (key, _) in enumerate(new_items, start_index):
            self._key_indices.setdefault(key, []).append(i)

    @override
    def extend(
        self,
        other: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Extend the multi-mapping with items from another object."""
        # Collect all new items first
        new_items = list(_yield_items(other, **kwargs))

        if not new_items:
            return

        # Add all items to the list at once
        start_index = len(self._items)
        self._items.extend(new_items)

        # Update indices incrementally for better performance
        for i, (key, _) in enumerate(new_items, start_index):
            self._key_indices.setdefault(key, []).append(i)

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
        """Return a string representation of the MultiDict."""
        return f"{self.__class__.__name__}({list(self._items)!r})"
