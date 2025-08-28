"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import itertools
import sys
from abc import abstractmethod
from collections import defaultdict
from typing import Any, Callable, Generic, TypeVar, overload

if sys.version_info >= (3, 9):
    from collections.abc import (
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


class _NoDefault:
    pass


_NO_DEFAULT = _NoDefault()


def withdefault(base_method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to add default parameter handling to methods that can raise KeyError.
    
    This decorator simplifies the definition of methods that have an optional default
    parameter. It automatically handles the pattern of trying the base operation and
    falling back to the default value if a KeyError is raised.
    
    The decorated method should be the base implementation that raises KeyError
    when the requested key is not found. The decorator will wrap it to handle
    the default parameter.
    
    Note: This decorator is primarily useful for creating new methods. For existing
    methods with complex type overloads, consider using _with_default_handling() helper.
    """
    def wrapper(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> Any:
        try:
            return base_method(self, key)
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default  # type: ignore[return-value]
    
    # Copy metadata from the original method
    wrapper.__name__ = base_method.__name__
    wrapper.__doc__ = base_method.__doc__
    wrapper.__annotations__ = base_method.__annotations__.copy()
    
    # Add the default parameter to annotations
    wrapper.__annotations__['default'] = D | _NoDefault
    
    return wrapper


def _with_default_handling(operation: Callable[[], V], default: D | _NoDefault) -> V | D:
    """Helper function to handle the common default parameter pattern.
    
    This function encapsulates the repetitive try/except pattern used in methods
    that have optional default parameters.
    
    Args:
        operation: A callable that performs the operation and may raise KeyError
        default: The default value to return, or _NO_DEFAULT to re-raise KeyError
        
    Returns:
        The result of the operation, or the default value if KeyError was raised
        and default is not _NO_DEFAULT.
        
    Raises:
        KeyError: If the operation raises KeyError and default is _NO_DEFAULT.
    """
    try:
        return operation()
    except KeyError:
        if default is _NO_DEFAULT:
            raise
        return default  # type: ignore[return-value]


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


class MultiMapping(Mapping[K, V], Generic[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    def _getall(self, key: K) -> list[V]:
        """Get all values for a key.

        Returns an empty list if no values are found.
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

    @overload
    def getone(self, key: K) -> V: ...

    @overload
    def getone(self, key: K, default: D) -> V | D: ...

    def getone(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return _with_default_handling(lambda: self.getall(key)[0], default)

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
        except KeyError as e:  # pragma: no cover
            msg = "_getall must return an empty list instead of raising KeyError"
            raise RuntimeError(msg) from e
        if not ret:
            if default is _NO_DEFAULT:
                raise KeyError(key)
            return default  # type: ignore[return-value]
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
    def _popone(self, key: K) -> V:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError  # pragma: no cover

    @overload
    def popone(self, key: K) -> V: ...

    @overload
    def popone(self, key: K, default: D) -> V | D: ...

    def popone(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return _with_default_handling(lambda: self._popone(key), default)

    @overload
    def popall(self, key: K) -> list[V]: ...

    @overload
    def popall(self, key: K, default: D) -> list[V] | D: ...

    def popall(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> list[V] | D:
        """Remove and return all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        return _with_default_handling(
            lambda: [self.popone(key) for _ in range(len(self.getall(key)))], 
            default
        )

    @overload
    def pop(self, key: K) -> V: ...

    @overload
    def pop(self, key: K, default: D) -> V | D: ...

    def pop(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Same as `popone`."""
        return self.popone(key, default)

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
