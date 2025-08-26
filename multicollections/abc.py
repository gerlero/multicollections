"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        ItemsView,
        Iterable,
        Iterator,
        KeysView,
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
        KeysView,
        Mapping,
        MutableMapping,
        Sequence,
        ValuesView,
    )

K = TypeVar("K")
V = TypeVar("V")


class MultiMapping(Mapping[K, V], ABC):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys.

        Keys with multiple values may be yielded multiple times.
        """
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        ...

    @abstractmethod
    def getall(self, key: K, default: list[V] | None = None) -> list[V]:
        """Get all values for a key.

        Returns the default value if the key is not found.
        """
        ...

    def keys(self) -> KeysView[K]:
        """Return a view of the keys in the mapping."""
        return super().keys()

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the mapping."""
        return super().values()

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items in the mapping."""
        return super().items()

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get the first value for a key, or return default if not found."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: object) -> bool:
        """Check if a key is in the mapping."""
        try:
            self[key]  # type: ignore[misc]
        except KeyError:
            return False
        else:
            return True


class MutableMultiMapping(MultiMapping[K, V], MutableMapping[K, V], ABC):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        This should replace all existing values for the key with a single new value.
        """
        ...

    @abstractmethod
    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        ...

    @abstractmethod
    def add(self, key: K, value: V) -> None:
        """Add a value for a key.

        This should add the value without removing existing values for the key.
        """
        ...

    def clear(self) -> None:
        """Remove all items from the mapping."""
        # Default implementation - get unique keys to avoid iteration issues
        keys_to_delete = list(set(self.keys()))
        for key in keys_to_delete:
            del self[key]

    def pop(self, key: K, default: V | None = None) -> V:
        """Remove and return the first value for a key.

        If key is not found, default is returned if given, otherwise
        KeyError is raised.
        """
        try:
            value = self[key]
            del self[key]
        except KeyError:
            if default is not None:
                return default
            raise
        else:
            return value

    def popitem(self) -> tuple[K, V]:
        """Remove and return an arbitrary (key, value) pair from the mapping.

        Raises KeyError if the mapping is empty.
        """
        if not self:
            msg = "popitem(): mapping is empty"
            raise KeyError(msg)
        key = next(iter(self))
        value = self[key]
        del self[key]
        return (key, value)

    def setdefault(self, key: K, default: V | None = None) -> V:
        """Get the first value for a key, or set and return default if not found."""
        try:
            return self[key]
        except KeyError:
            if default is not None:
                self[key] = default
                return default
            raise

    def update(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V
    ) -> None:
        """Update the mapping with key-value pairs from other.

        Overwrites existing keys.
        """
        if isinstance(other, Mapping):
            for key, value in other.items():
                self[key] = value
        else:
            for key, value in other:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
