"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import sys
from abc import abstractmethod
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Iterator,
        Mapping,
        MutableMapping,
    )
else:
    from typing import (
        Iterator,
        Mapping,
        MutableMapping,
    )

K = TypeVar("K")
V = TypeVar("V")


class MultiMapping(Mapping[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        raise NotImplementedError

    @abstractmethod
    def getall(self, key: K, default: list[V] | None = None) -> list[V]:
        """Get all values for a key.

        Returns the default value if the key is not found.
        """
        raise NotImplementedError


class MutableMultiMapping(MultiMapping[K, V], MutableMapping[K, V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        This should replace all existing values for the key with a single new value.
        """
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, key: K, value: V) -> None:
        """Add a value for a key.

        This should add the value without removing existing values for the key.
        """
        raise NotImplementedError
