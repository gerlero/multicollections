"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import sys
from abc import abstractmethod
from collections import defaultdict
from typing import Generic, TypeVar, overload

if sys.version_info >= (3, 9):
    from collections.abc import Collection, Iterator
else:
    from typing import Collection, Iterator

K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")


class MultiMappingView(Collection):
    """Base class for MultiMapping views."""

    def __init__(self, mapping: MultiMapping[K, V]) -> None:
        """Initialize the view with the given mapping."""
        self._mapping = mapping

    def __len__(self) -> int:
        """Return the number of items in the mapping."""
        return len(self._mapping)


class KeysView(MultiMappingView):
    """View for the keys in a MultiMapping."""

    def __contains__(self, key: K) -> bool:
        """Check if the key is in the mapping."""
        return key in self._mapping

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys."""
        return iter(self._mapping)


class ItemsView(MultiMappingView):
    """View for the items (key-value pairs) in a MultiMapping."""

    def __contains__(self, item: tuple[K, V]) -> bool:
        """Check if the item is in the mapping."""
        key, value = item
        try:
            return value in self._mapping.getall(key)
        except KeyError:
            return False

    def __iter__(self) -> Iterator[tuple[K, V]]:
        """Return an iterator over the items (key-value pairs)."""
        counts = defaultdict(int)
        for k in self._mapping:
            yield (k, self._mapping.getall(k)[counts[k]])
            counts[k] += 1


class ValuesView(MultiMappingView):
    """View for the values in a MultiMapping."""

    def __contains__(self, value: V) -> bool:
        """Check if the value is in the mapping."""
        return any(value in self._mapping.getall(key) for key in set(self._mapping))

    def __iter__(self) -> Iterator[V]:
        """Return an iterator over the values."""
        yield from (v for _, v in self._mapping.items())


class MultiMapping(Generic[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    class _NoDefault:
        pass

    _NO_DEFAULT = _NoDefault()

    @abstractmethod
    def _getall(self, key: K) -> list[V]:
        """Get all values for a key."""
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

    def __contains__(self, key: K) -> bool:
        """Check if the key is present in the multi-mapping."""
        try:
            self[key]
        except KeyError:
            return False
        return True

    @overload
    def getone(self, key: K) -> V: ...

    @overload
    def getone(self, key: K, default: D) -> V | D: ...

    def getone(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            return self.getall(key)[0]
        except KeyError:
            if default is self._NO_DEFAULT:
                raise
            return default  # ty: ignore[invalid-return-type]

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.getone(key)

    @overload
    def getall(self, key: K) -> list[V]: ...

    @overload
    def getall(self, key: K, default: D) -> list[V] | D: ...

    def getall(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> list[V] | D:
        """Get all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            ret = self._getall(key)
        except KeyError:
            if default is self._NO_DEFAULT:
                raise
            return default  # ty: ignore[invalid-return-type]
        if not ret:
            if default is self._NO_DEFAULT:
                raise KeyError(key)
            return default  # ty: ignore[invalid-return-type]
        return ret

    def keys(self) -> KeysView[K]:
        """Return a view of the keys in the MultiMapping."""
        return KeysView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items (key-value pairs) in the MultiMapping."""
        return ItemsView(self)

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the MultiMapping."""
        return ValuesView(self)


class MutableMultiMapping(MultiMapping[K, V]):
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
