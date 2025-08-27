"""Fully generic `MultiDict` class."""

from __future__ import annotations

import sys
from typing import TypeVar, overload

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

import itertools

from .abc import MutableMultiMapping, _NoDefault, _NO_DEFAULT

K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")


class MultiDict(MutableMultiMapping[K, V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    def __init__(
        self, iterable: Mapping[K, V] | Iterable[Sequence[K | V]] = (), **kwargs: V
    ) -> None:
        """Create a MultiDict."""
        self._items: list[tuple[K, V]] = []
        self._key_indices: dict[K, list[int]] = {}
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._add_item(key, value)
        else:
            for key, value in iterable:
                self._add_item(key, value)
        for key, value in kwargs.items():
            self._add_item(key, value)

    def _add_item(self, key: K, value: V) -> None:
        """Add an item and update the key index."""
        index = len(self._items)
        self._items.append((key, value))
        if key not in self._key_indices:
            self._key_indices[key] = []
        self._key_indices[key].append(index)

    def _getall(self, key: K) -> list[V]:
        """Get all values for a key."""
        return [self._items[i][1] for i in self._key_indices.get(key, [])]

    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        Replaces the first value for a key if it exists; otherwise, it adds a new item.
        Any other items with the same key are removed.
        """
        if key in self._key_indices:
            # Key exists, replace first occurrence and remove others
            indices = self._key_indices[key]
            first_index = indices[0]

            # Update the first occurrence
            self._items[first_index] = (key, value)

            if len(indices) > 1:
                # Remove duplicates efficiently by marking items as None and filtering
                for idx in indices[1:]:
                    self._items[idx] = None

                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
            else:
                # Only one value existed, just update the index (no rebuild needed)
                self._key_indices[key] = [first_index]
        else:
            # Key doesn't exist, add it
            self._add_item(key, value)

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    def add(self, key: K, value: V) -> None:
        """Add a value for a key."""
        self._add_item(key, value)

    def _popone(self, key: K) -> V:
        """Remove and return the first value for a key."""
        if key not in self._key_indices:
            raise KeyError(key)

        indices = self._key_indices[key]
        first_index = indices[0]
        value = self._items[first_index][1]

        if len(indices) == 1:
            # Only one item with this key - can remove efficiently
            del self._items[first_index]
            del self._key_indices[key]
            
            # Update indices for items that came after the removed one
            for k, idx_list in self._key_indices.items():
                self._key_indices[k] = [idx - 1 if idx > first_index else idx for idx in idx_list]
        else:
            # Multiple items with this key - mark and rebuild
            self._items[first_index] = None
            self._items = [item for item in self._items if item is not None]
            self._rebuild_indices()

        return value

    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        if key not in self._key_indices:
            raise KeyError(key)

        # Mark items for removal
        indices_to_remove = self._key_indices[key]
        for idx in indices_to_remove:
            self._items[idx] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)

    @overload
    def popall(self, key: K) -> list[V]: ...

    @overload  
    def popall(self, key: K, default: D) -> list[V] | D: ...

    def popall(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> list[V] | D:
        """Remove and return all values for a key as a list.
        
        More efficient than the ABC implementation which calls popone() repeatedly.
        """
        if key not in self._key_indices:
            if default is _NO_DEFAULT:
                raise KeyError(key)
            return default  # type: ignore[return-value]
        
        # Get all indices for this key
        indices = self._key_indices[key]
        
        # Collect all values before removal
        values = [self._items[i][1] for i in indices]
        
        # Mark all items for removal
        for idx in indices:
            self._items[idx] = None
        
        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()
        
        return values

    def update(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Update the multi-mapping with items from another object.

        This replaces existing values for keys found in the other object.
        More efficient than the ABC implementation for our data structure.
        """
        existing_keys = set(self._key_indices.keys())
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        
        for key, value in items:
            if key in existing_keys:
                self[key] = value
                existing_keys.discard(key)  # Remove from set to avoid duplicate processing
            else:
                self.add(key, value)

    def clear(self) -> None:
        """Remove all items from the multi-mapping.
        
        More efficient than the ABC implementation which calls popall() for each key.
        """
        self._items.clear()
        self._key_indices.clear()

    def __repr__(self) -> str:
        """Return a string representation of the MultiDict."""
        return f"{self.__class__.__name__}({list(self._items)!r})"
