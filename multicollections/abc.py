"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import contextlib
import functools
import itertools
import sys
from abc import abstractmethod
from collections import defaultdict
from typing import Generic, TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Callable,
        Collection,
        Iterable,
        Iterator,
        Mapping,
        MappingView,
        MutableMapping,
        Sequence,
    )
else:
    from typing import (
        Callable,
        Collection,
        Iterable,
        Iterator,
        Mapping,
        MappingView,
        MutableMapping,
        Sequence,
    )

K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")


class MultiMappingView(MappingView, Collection):
    """Base class for MultiMapping views."""

    def __init__(self, mapping: MultiMapping[K, V]) -> None:
        """Initialize the view with the given mapping."""
        super().__init__(mapping)


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
        return value in iter(self)

    def __iter__(self) -> Iterator[V]:
        """Return an iterator over the values."""
        yield from (v for _, v in self._mapping.items())


class _NoDefault:
    pass


_NO_DEFAULT = _NoDefault()


def with_default(
    meth: Callable[[MultiMappingView[K, V], K], V],
) -> Callable[[MultiMappingView[K, V], K, D], V | D]:
    """Add a default value argument to a method that can raise a `KeyError`."""

    @functools.wraps(meth)
    def wrapper(
        self: MultiMappingView[K, V], key: K, default: D | _NoDefault = _NO_DEFAULT
    ) -> V | D:
        try:
            return meth(self, key)
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default  # ty: ignore [invalid-return-type]

    return wrapper


class MultiMapping(Mapping[K, V], Generic[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    @with_default
    def getall(self, key: K) -> list[V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        raise NotImplementedError  # pragma: no cover

    @with_default
    def getone(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return self.getall(key)[0]

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.getone(key)

    def keys(self) -> KeysView[K]:
        """Return a view of the keys in the MultiMapping."""
        return KeysView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items (key-value pairs) in the MultiMapping."""
        return ItemsView(self)

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the MultiMapping."""
        return ValuesView(self)


class MutableMultiMapping(MultiMapping[K, V], MutableMapping[K, V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        If the key does not exist, it is added with the specified value.

        If the key already exists, the first item is assigned the new value,
        and any other items with the same key are removed.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def add(self, key: K, value: V) -> None:
        """Add a new value for a key."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    @with_default
    def popone(self, key: K) -> V:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError  # pragma: no cover

    @with_default
    def popall(self, key: K) -> list[V]:
        """Remove and return all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self.popone(key)]
        with contextlib.suppress(KeyError):
            while True:
                ret.append(self.popone(key))
        return ret

    @with_default
    def pop(self, key: K) -> V:
        """Same as `popone`."""
        return self.popone(key)

    def popitem(self) -> tuple[K, V]:
        """Remove and return a (key, value) pair."""
        key = next(iter(self))
        value = self.popone(key)
        return key, value

    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        self.popall(key)

    def clear(self) -> None:
        """Remove all items from the multi-mapping."""
        for key in set(self.keys()):
            self.popall(key)

    def extend(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Extend the multi-mapping with items from another object."""
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            self.add(key, value)

    def merge(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be replaced.
        """
        existing_keys = set(self.keys())
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            if key not in existing_keys:
                self.add(key, value)

    def update(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Update the multi-mapping with items from another object.

        This replaces existing values for keys found in the other object.
        """
        existing_keys = set(self.keys())
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            if key in existing_keys:
                self[key] = value
                existing_keys.remove(key)
            else:
                self.add(key, value)
