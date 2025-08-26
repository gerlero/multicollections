"""Fully generic `MultiDict` class."""

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

from .abc import MutableMultiMapping

K = TypeVar("K")
V = TypeVar("V")


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

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    def getall(self, key: K, default: list[V] | None = None) -> list[V]:
        """Get all values for a key.

        Returns the default value if the key is not found.
        """
        if key not in self._key_indices:
            if default is None:
                return []
            return default

        indices = self._key_indices[key]
        return [self._items[idx][1] for idx in indices]

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
            self._items[idx] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    def __repr__(self) -> str:
        """Return a string representation of the MultiDict."""
        return f"{self.__class__.__name__}({list(self._items)!r})"
