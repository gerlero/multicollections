"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import contextlib
import functools
import itertools
import sys
from abc import abstractmethod
from collections import defaultdict, deque
from collections.abc import (
    Callable,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    MappingView,
    MutableMapping,
)
from collections.abc import ItemsView as MappingItemsView
from collections.abc import KeysView as MappingKeysView
from collections.abc import ValuesView as MappingValuesView
from typing import Any, TypeVar, overload

from ._typing import MappingLike, MethodWithDefault, SupportsKeysAndGetItem, override

_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
_Self = TypeVar("_Self")


class MultiMappingView(MappingView):
    """Base class for MultiMapping views."""

    _mapping: MultiMapping[Any, Any]

    def __init__(self, mapping: MultiMapping[Any, Any], /) -> None:
        """Initialize the view with the given mapping."""
        super().__init__(mapping)

    @override
    def __len__(self) -> int:
        """Return the number of items in the view."""
        return len(self._mapping)


class KeysView(MappingKeysView[_K], MultiMappingView):
    """View for the keys in a MultiMapping."""

    @override
    def __contains__(self, key: object, /) -> bool:
        """Check if the key is in the multi-mapping."""
        return key in self._mapping

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys."""
        return iter(self._mapping)


class ItemsView(MappingItemsView[_K, _V], MultiMappingView):
    """View for the items (key-value pairs) in a MultiMapping."""

    @override
    def __contains__(self, item: object, /) -> bool:
        """Check if the item is in the multi-mapping."""
        match item:
            case key, value:
                try:
                    values = self._mapping.getall(key)
                except KeyError:
                    return False
                return value in values
            case _:
                return False

    @override
    def __iter__(self) -> Iterator[tuple[_K, _V]]:
        """Return an iterator over the items (key-value pairs)."""
        counts: defaultdict[_K, int] = defaultdict(int)
        for k in self._mapping:
            yield (
                k,
                next(
                    itertools.islice(self._mapping.getall(k), counts[k], counts[k] + 1)
                ),
            )
            counts[k] += 1


class ValuesView(MappingValuesView[_V], MultiMappingView):
    """View for the values in a MultiMapping."""

    @override
    def __contains__(self, value: object, /) -> bool:
        """Check if the value is in the mapping."""
        return any(v == value for v in self)

    @override
    def __iter__(self) -> Iterator[_V]:
        """Return an iterator over the values."""
        yield from (v for _, v in self._mapping.items())


if sys.version_info >= (3, 15):
    _NO_DEFAULT = sentinel("_NO_DEFAULT")  # noqa: F821
else:

    class _NoDefault:
        pass

    _NO_DEFAULT = _NoDefault()


def with_default(
    meth: Callable[[_Self, _K], _V],
    /,
) -> MethodWithDefault[_K, _V]:
    """Add a default value argument to a method that can raise a `KeyError`."""

    @overload
    def wrapper(self: _Self, key: _K, /) -> _V: ...

    @overload
    def wrapper(self: _Self, key: _K, /, default: _D) -> _V | _D: ...

    @functools.wraps(meth)
    def wrapper(
        self: _Self,
        key: _K,
        /,
        default: _D | _NO_DEFAULT = _NO_DEFAULT,  # ty: ignore[invalid-type-form]
    ) -> _V | _D:
        try:
            return meth(self, key)
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default

    return wrapper  # ty: ignore[invalid-return-type]


def _yield_items(
    obj: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]], /, **kwargs: _V
) -> Iterable[tuple[_K, _V]]:
    if isinstance(obj, MappingLike):
        yield from obj.items()
    elif isinstance(obj, SupportsKeysAndGetItem):
        yield from ((k, obj[k]) for k in obj.keys())  # noqa: SIM118
    else:
        yield from obj

    yield from kwargs.items()


class MultiMapping(Mapping[_K, _V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    @with_default
    def getall(self, key: _K, /) -> Collection[_V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    @override
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        raise NotImplementedError  # pragma: no cover

    @with_default
    def getone(self, key: _K, /) -> _V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            return next(iter(self.getall(key)))
        except StopIteration as e:  # pragma: no cover
            msg = "MultiMapping.getall returned an empty collection"
            raise RuntimeError(msg) from e

    @override
    def __getitem__(self, key: _K, /) -> _V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.getone(key)

    @override
    def keys(self) -> KeysView[_K]:
        """Return a view of the keys in the MultiMapping."""
        return KeysView(self)

    @override
    def items(self) -> ItemsView[_K, _V]:
        """Return a view of the items (key-value pairs) in the MultiMapping."""
        return ItemsView(self)

    @override
    def values(self) -> ValuesView[_V]:
        """Return a view of the values in the MultiMapping."""
        return ValuesView(self)


class MutableMultiMapping(MultiMapping[_K, _V], MutableMapping[_K, _V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    @override
    def __setitem__(self, key: _K, value: _V, /) -> None:
        """Set the value for a key.

        If the key does not exist, it is added with the specified value.

        If the key already exists, the first item is assigned the new value,
        and any other items with the same key are removed.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def add(self, key: _K, value: _V, /) -> None:
        """Add a new value for a key."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    @with_default
    def popone(self, key: _K, /) -> _V:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError  # pragma: no cover

    @with_default
    def popall(self, key: _K, /) -> Collection[_V]:
        """Remove and return all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self.popone(key)]
        with contextlib.suppress(KeyError):
            while True:
                ret.append(self.popone(key))
        return ret

    @with_default
    @override
    def pop(self, key: _K, /) -> _V:
        """Same as `popone`."""
        return self.popone(key)

    @override
    def popitem(self) -> tuple[_K, _V]:
        """Remove and return the last (key, value) pair.

        Raises a `KeyError` if the multi-mapping is empty.
        """
        if not self:
            msg = "popitem(): multi-mapping is empty"
            raise KeyError(msg)

        for key in self:
            pass
        if len(self.getall(key)) == 1:
            return key, self.popone(key)

        items = list(self.items())
        value = items.pop()[1]
        self.clear()
        self.extend(items)

        return key, value

    @override
    def __delitem__(self, key: _K, /) -> None:
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
        other: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Extend the multi-mapping with items from another object."""
        for key, value in _yield_items(other, **kwargs):
            self.add(key, value)

    def merge(
        self,
        other: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]] = (),
        /,
        **kwargs: _V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be replaced.
        """
        existing_keys = set(self.keys())
        for key, value in _yield_items(other, **kwargs):
            if key not in existing_keys:
                self.add(key, value)

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
        replacements: dict[_K, deque[_V]] = {}
        remaining: dict[_K, int] = {}
        appended: list[tuple[_K, _V]] = []

        for key, value in _yield_items(other, **kwargs):
            slots = remaining.get(key)
            if slots is None:
                slots = len(self.getall(key, ()))

            if slots:
                replacements.setdefault(key, deque()).append(value)
                slots -= 1
            else:
                appended.append((key, value))

            remaining[key] = slots

        for _ in range(len(self)):
            key = next(iter(self))
            value = self.popone(key)

            values = replacements.get(key)
            if values is None:
                self.add(key, value)
            elif values:
                self.add(key, values.popleft())

        self.extend(appended)


try:
    import multidict
except ImportError:  # pragma: no cover
    pass
else:
    MutableMultiMapping.register(multidict.MultiDict)
    MutableMultiMapping.register(multidict.CIMultiDict)
    MultiMapping.register(multidict.MultiDictProxy)
    MultiMapping.register(multidict.CIMultiDictProxy)
