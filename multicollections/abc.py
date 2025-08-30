"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import contextlib
import functools
import itertools
import sys
from abc import abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Tuple, TypeVar, overload, Generic

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

if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol

from ._util import override

_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
_Self = TypeVar("_Self")


class MultiMappingView(MappingView, Collection[object], Generic[_K, _V]):
    """Base class for MultiMapping views."""
    
    _mapping: MultiMapping[_K, _V]  # Type annotation for mypy

    @override
    def __init__(self, mapping: MultiMapping[_K, _V]) -> None:
        """Initialize the view with the given mapping."""
        super().__init__(mapping)


class KeysView(MultiMappingView[_K, _V], Collection[_K]):
    """View for the keys in a MultiMapping."""

    @override
    def __contains__(self, key: object) -> bool:
        """Check if the key is in the mapping."""
        return key in self._mapping

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys."""
        return iter(self._mapping)


class ItemsView(MultiMappingView[_K, _V], Collection[Tuple[_K, _V]]):
    """View for the items (key-value pairs) in a MultiMapping."""

    @override
    def __contains__(self, item: object) -> bool:
        """Check if the item is in the mapping."""
        try:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                return False
            key, value = item
        except (TypeError, ValueError):
            return False
        try:
            return value in self._mapping.getall(key)  # ty: ignore[arg-type]
        except KeyError:
            return False

    @override
    def __iter__(self) -> Iterator[tuple[_K, _V]]:
        """Return an iterator over the items (key-value pairs)."""
        counts: defaultdict[_K, int] = defaultdict(int)
        for k in self._mapping:
            yield (k, self._mapping.getall(k)[counts[k]])
            counts[k] += 1


class ValuesView(MultiMappingView[_K, _V], Collection[_V]):
    """View for the values in a MultiMapping."""

    @override
    def __contains__(self, value: object) -> bool:
        """Check if the value is in the mapping."""
        for v in self:
            if v == value:
                return True
        return False

    @override
    def __iter__(self) -> Iterator[_V]:
        """Return an iterator over the values."""
        yield from (v for _, v in self._mapping.items())


class _NoDefault:
    pass


_NO_DEFAULT = _NoDefault()

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    _CallableWithDefault = Any  # Simplified type for mypy


def with_default(
    meth: Callable[[_Self, _K], _V],
) -> _CallableWithDefault:
    """Add a default value argument to a method that can raise a `KeyError`."""

    @overload
    def wrapper(self: _Self, key: _K) -> _V: ...  # pragma: no cover

    @overload
    def wrapper(self: _Self, key: _K, default: _D) -> _V | _D: ...  # pragma: no cover

    @functools.wraps(meth)
    def wrapper(
        self: _Self, key: _K, default: _D | _NoDefault = _NO_DEFAULT
    ) -> _V | _D:
        try:
            return meth(self, key)
        except KeyError:
            if isinstance(default, _NoDefault):
                raise
            return default  # ty: ignore [return-value]

    return wrapper  # ty: ignore [return-value]


class MultiMapping(Mapping[_K, _V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    @with_default
    def getall(self, key: _K) -> list[_V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        raise NotImplementedError  # pragma: no cover

    @with_default
    def getone(self, key: _K) -> _V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return self.getall(key)[0]  # ty: ignore[no-any-return]

    @override
    def __getitem__(self, key: _K) -> _V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.getone(key)  # ty: ignore[no-any-return]

    @override
    def keys(self) -> KeysView[_K, _V]:  # ty: ignore[override]
        """Return a view of the keys in the MultiMapping."""
        return KeysView(self)

    @override
    def items(self) -> ItemsView[_K, _V]:  # ty: ignore[override]
        """Return a view of the items (key-value pairs) in the MultiMapping."""
        return ItemsView(self)

    @override
    def values(self) -> ValuesView[_K, _V]:  # ty: ignore[override]
        """Return a view of the values in the MultiMapping."""
        return ValuesView(self)


class MutableMultiMapping(MultiMapping[_K, _V], MutableMapping[_K, _V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    def __setitem__(self, key: _K, value: _V) -> None:
        """Set the value for a key.

        If the key does not exist, it is added with the specified value.

        If the key already exists, the first item is assigned the new value,
        and any other items with the same key are removed.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def add(self, key: _K, value: _V) -> None:
        """Add a new value for a key."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    @with_default
    def popone(self, key: _K) -> _V:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError  # pragma: no cover

    @with_default
    def popall(self, key: _K) -> list[_V]:
        """Remove and return all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self.popone(key)]
        with contextlib.suppress(KeyError):
            while True:
                ret.append(self.popone(key))
        return ret

    @with_default
    def pop(self, key: _K) -> _V:
        """Same as `popone`."""
        return self.popone(key)  # ty: ignore[no-any-return]

    def popitem(self) -> tuple[_K, _V]:
        """Remove and return a (key, value) pair."""
        key = next(iter(self))
        value = self.popone(key)
        return key, value

    @override
    def __delitem__(self, key: _K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        self.popall(key)

    @override
    def clear(self) -> None:
        """Remove all items from the multi-mapping."""
        for key in set(self.keys()):
            self.popall(key)

    def extend(
        self,
        other: Mapping[_K, _V] | Iterable[tuple[_K, _V]] = (),
        **kwargs: _V,
    ) -> None:
        """Extend the multi-mapping with items from another object."""
        if isinstance(other, Mapping):
            for key, value in other.items():
                self.add(key, value)
        else:
            for key, value in other:
                self.add(key, value)
        
        # Handle kwargs separately
        for key, value in kwargs.items():
            self.add(key, value)  # ty: ignore[arg-type]

    def merge(
        self,
        other: Mapping[_K, _V] | Iterable[tuple[_K, _V]] = (),
        **kwargs: _V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be replaced.
        """
        existing_keys = set(self.keys())
        
        if isinstance(other, Mapping):
            for key, value in other.items():
                if key not in existing_keys:
                    self.add(key, value)
        else:
            for key, value in other:
                if key not in existing_keys:
                    self.add(key, value)
        
        # Handle kwargs separately
        for key, value in kwargs.items():
            if key not in existing_keys:  # ty: ignore[operator]
                self.add(key, value)  # ty: ignore[arg-type]

    @override
    def update(self, *args: Mapping[_K, _V] | Iterable[tuple[_K, _V]], **kwargs: _V) -> None:  # ty: ignore[override]
        """Update the multi-mapping with items from another object.

        This replaces existing values for keys found in the other object.
        """
        # Handle the different call signatures like dict.update()
        if args:
            other = args[0]
            existing_keys = set(self.keys())
            if isinstance(other, Mapping):
                items = other.items()
            else:
                items = other
            for key, value in items:
                if key in existing_keys:
                    self[key] = value
                    existing_keys.discard(key)
                else:
                    self.add(key, value)
        
        # Handle keyword arguments
        for key, value in kwargs.items():
            self[key] = value  # ty: ignore[index, assignment]
