"""Fully generic `MultiDict` class."""

from __future__ import annotations

import sys
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        ItemsView,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        Sequence,
        ValuesView,
    )
else:
    from typing import (
        ItemsView,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        Sequence,
        ValuesView,
    )

K = TypeVar("K")
V = TypeVar("V")


class MultiDict(MutableMapping[K, V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    class ValuesView(ValuesView[V]):  # noqa: D106
        def __init__(self, mapping: MultiDict[K, V]) -> None:  # noqa: D107
            super().__init__(mapping)

        def __iter__(self) -> Iterator[V]:  # noqa: D105
            return (v for _, v in self._mapping._items)  # noqa: SLF001

        def __len__(self) -> int:  # noqa: D105
            return len(self._mapping._items)  # noqa: SLF001

    class ItemsView(ItemsView[K, V]):  # noqa: D106
        def __init__(self, mapping: MultiDict[K, V]) -> None:  # noqa: D107
            self._mapping = mapping

        def __iter__(self) -> Iterator[tuple[K, V]]:  # noqa: D105
            return iter(self._mapping._items)  # noqa: SLF001

        def __len__(self) -> int:  # noqa: D105
            return len(self._mapping._items)  # noqa: SLF001

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

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        if key not in self._key_indices:
            raise KeyError(key)
        first_index = self._key_indices[key][0]
        return self._items[first_index][1]

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
                    self._items[idx] = None  # type: ignore
                
                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            # Key doesn't exist, add it
            self._add_item(key, value)

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, value) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    def add(self, key: K, value: V) -> None:
        """Add a value for a key."""
        self._add_item(key, value)

    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        if key not in self._key_indices:
            raise KeyError(key)
        
        # Mark items for removal
        indices_to_remove = self._key_indices[key]
        for idx in indices_to_remove:
            self._items[idx] = None  # type: ignore
        
        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the MultiDict."""
        return self.ValuesView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items in the MultiDict."""
        return self.ItemsView(self)

    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)
