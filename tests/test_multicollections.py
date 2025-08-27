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

import multidict
import pytest
from multicollections import MultiDict
from multicollections.abc import MutableMultiMapping

K = TypeVar("K")
V = TypeVar("V")


class ListMultiDict(MutableMultiMapping[K, V]):
    def __init__(
        self, iterable: Mapping[K, V] | Iterable[Sequence[K | V]] = (), **kwargs: V
    ) -> None:
        self._items: list[tuple[K, V]] = []
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._items.append((key, value))
        else:
            for key, value in iterable:
                self._items.append((key, value))
        for key, value in kwargs.items():
            self._items.append((key, value))

    def __getitem__(self, key: K) -> V:
        for k, v in self._items:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        replaced: int | None = None
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                replaced = i
                break

        if replaced is not None:
            # Key existed, remove any duplicates
            self._items = [
                (k, v)
                for i, (k, v) in enumerate(self._items)
                if i == replaced or k != key
            ]
        else:
            # Key didn't exist, add it
            self._items.append((key, value))

    def add(self, key: K, value: V) -> None:
        self._items.append((key, value))

    def __delitem__(self, key: K) -> None:
        new_items = [(k, v) for k, v in self._items if k != key]
        if len(new_items) == len(self._items):
            raise KeyError(key)
        self._items = new_items

    def values(self) -> Iterable[V]:
        return [v for _, v in self._items]

    def items(self) -> Iterable[tuple[K, V]]:
        return self._items

    def __iter__(self) -> Iterator[K]:
        return (k for k, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_empty_creation(cls: type[MutableMultiMapping]) -> None:
    md = cls()
    assert len(md) == 0
    assert list(md) == []
    assert list(md.items()) == []
    assert list(md.values()) == []


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_from_pairs(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict from list of pairs."""
    pairs = [("a", 1), ("b", 2), ("a", 3)]
    md = cls(pairs)  # ty: ignore [too-many-positional-arguments]

    assert len(md) == 3
    assert md["a"] == 1  # First value for duplicate key
    assert md["b"] == 2
    assert list(md.items()) == pairs
    assert list(md) == ["a", "b", "a"]
    assert list(md.values()) == [1, 2, 3]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_from_dict(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict from regular dict."""
    d = {"x": 10, "y": 20, "z": 30}
    md = cls(d)  # ty: ignore [too-many-positional-arguments]

    assert len(md) == 3
    for key, value in d.items():
        assert md[key] == value

    # Order is preserved (dict insertion order is preserved in Python 3.7+)
    assert set(md.items()) == set(d.items())


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_with_kwargs(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict with keyword arguments."""
    md = cls(a=1, b=2, c=3)  # ty: ignore [unknown-argument]

    assert len(md) == 3
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_mixed(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict with both iterable and kwargs."""
    pairs = [("a", 1), ("b", 2)]
    md = cls(pairs, c=3, d=4)  # ty: ignore [too-many-positional-arguments, unknown-argument]

    assert len(md) == 4
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3
    assert md["d"] == 4


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getitem(cls: type[MutableMultiMapping]) -> None:
    """Test __getitem__ behavior."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    assert md["a"] == 1  # First value
    assert md["b"] == 2

    with pytest.raises(KeyError):
        _ = md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_new_key(cls: type[MutableMultiMapping]) -> None:
    """Test __setitem__ with new key."""
    md = cls()
    md["new"] = "value"

    assert len(md) == 1
    assert md["new"] == "value"
    assert list(md.items()) == [("new", "value")]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_existing_key(cls: type[MutableMultiMapping]) -> None:
    """Test __setitem__ with existing key."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    md["a"] = 99

    # Should replace and remove all duplicates
    assert len(md) == 2
    assert md["a"] == 99
    assert list(md.items()) == [("a", 99), ("b", 2)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_add_method(cls: type[MutableMultiMapping]) -> None:
    """Test add() method."""
    md = cls()
    md.add("key", "value1")
    md.add("key", "value2")
    md.add("other", "value3")

    assert len(md) == 3
    assert md["key"] == "value1"  # First value
    assert md["other"] == "value3"
    assert list(md.items()) == [
        ("key", "value1"),
        ("key", "value2"),
        ("other", "value3"),
    ]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_delitem(cls: type[MutableMultiMapping]) -> None:
    """Test __delitem__ behavior."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]
    del md["a"]  # Should remove all 'a' items

    assert len(md) == 2
    assert list(md.items()) == [("b", 2), ("c", 4)]

    with pytest.raises(KeyError):
        del md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_iteration(cls: type[MutableMultiMapping]) -> None:
    """Test iteration over keys."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    keys = list(md)

    assert keys == ["a", "b", "a"]

    # Test that iteration yields duplicate keys
    key_count = {}
    for key in md:
        key_count[key] = key_count.get(key, 0) + 1

    assert key_count == {"a": 2, "b": 1}


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_values_view(cls: type[MutableMultiMapping]) -> None:
    """Test values() view."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    values = md.values()

    assert len(values) == 3
    assert list(values) == [1, 2, 3]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view(cls: type[MutableMultiMapping]) -> None:
    """Test items() view."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    items = md.items()

    assert len(items) == 3
    assert list(items) == [("a", 1), ("b", 2), ("a", 3)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_len(cls: type[MutableMultiMapping]) -> None:
    """Test len() behavior."""
    md = cls()
    assert len(md) == 0

    md.add("a", 1)
    assert len(md) == 1

    md.add("a", 2)  # Duplicate key
    assert len(md) == 2

    md["b"] = 3
    assert len(md) == 3

    del md["a"]  # Removes both 'a' items
    assert len(md) == 1


def test_repr() -> None:
    """Test __repr__ method."""
    # Test empty MultiDict
    md_empty = MultiDict()
    assert repr(md_empty) == "MultiDict([])"

    # Test MultiDict with single item
    md_single = MultiDict([("a", 1)])
    assert repr(md_single) == "MultiDict([('a', 1)])"

    # Test MultiDict with multiple items including duplicates
    md_multi = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    assert repr(md_multi) == "MultiDict([('a', 1), ('b', 2), ('a', 3)])"

    # Test that repr can be used to recreate equivalent objects
    original = MultiDict([("x", "hello"), ("y", 42), ("x", "world")])
    repr_str = repr(original)
    recreated = eval(repr_str)  # noqa: S307
    assert list(original.items()) == list(recreated.items())
