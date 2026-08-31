from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping

import multidict
import pytest

import multicollections
from multicollections import MultiDict
from multicollections._typing import MappingLike, SupportsKeysAndGetItem
from multicollections.abc import MultiMapping, MutableMultiMapping

from .minimalimpl import ListMultiDict


def test_has_version() -> None:
    assert hasattr(multicollections, "__version__")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_implements_abc(cls) -> None:
    assert issubclass(cls, MutableMultiMapping)
    assert issubclass(cls, MultiMapping)
    assert issubclass(cls, MutableMapping)
    assert issubclass(cls, Mapping)

    md = cls([("a", 1), ("b", 2)])
    assert isinstance(md, MutableMultiMapping)
    assert isinstance(md, MultiMapping)
    assert isinstance(md, MutableMapping)
    assert isinstance(md, Mapping)


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_empty_creation(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()
    assert len(md) == 0
    assert list(md) == []
    assert list(md.items()) == []
    assert list(md.values()) == []


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_from_pairs(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    pairs = [("a", 1), ("b", 2), ("a", 3)]
    md = cls(pairs)

    assert len(md) == 3
    assert md["a"] == 1
    assert md["b"] == 2
    assert list(md.items()) == pairs
    assert list(md) == ["a", "b", "a"]
    assert list(md.values()) == [1, 2, 3]


@pytest.mark.parametrize(
    "cls",
    [
        MultiDict,
        ListMultiDict,
        dict,
        multidict.MultiDict,
    ],
)
def test_creation_from_dict(
    cls: type[MultiDict | ListMultiDict | dict | multidict.MultiDict],
) -> None:
    d = {"x": 10, "y": 20, "z": 30}
    md = cls(d)

    assert len(md) == 3
    for key, value in d.items():
        assert md[key] == value

    assert list(md.items()) == list(d.items())
    assert md.items() == d.items()


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, dict])
def test_creation_from_duck_mapping(
    cls: type[MultiDict | ListMultiDict | dict],
) -> None:
    class DuckMapping:
        def __init__(self, items: Iterable[tuple[str, int]], /) -> None:
            self._dict = dict(items)

        def __getitem__(self, key: str, /) -> int:
            return self._dict[key]

        def keys(self) -> Iterable[str]:
            return self._dict.keys()

    assert issubclass(DuckMapping, SupportsKeysAndGetItem)
    assert not issubclass(DuckMapping, MappingLike)
    assert not issubclass(DuckMapping, Mapping)

    duck = DuckMapping([("p", 100), ("q", 200)])
    assert isinstance(duck, SupportsKeysAndGetItem)
    assert not isinstance(duck, MappingLike)
    assert not isinstance(duck, Mapping)

    md = cls(duck)

    assert len(md) == 2
    assert list(md.items()) == [("p", 100), ("q", 200)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict])
def test_creation_from_duck_multi_mapping(
    cls: type[MultiDict | ListMultiDict],
) -> None:
    class DuckMultiMapping:
        def __init__(self, items: Iterable[tuple[str, int]], /) -> None:
            self._items = list(items)

        def __getitem__(self, key: str, /) -> int:
            assert False

        def keys(self) -> Iterable[str]:
            assert False

        def items(self) -> Iterable[tuple[str, int]]:
            return self._items

    assert issubclass(DuckMultiMapping, MappingLike)
    assert issubclass(DuckMultiMapping, SupportsKeysAndGetItem)
    assert not issubclass(DuckMultiMapping, Mapping)

    duck = DuckMultiMapping([("p", 100), ("p", 200)])
    assert isinstance(duck, MappingLike)
    assert isinstance(duck, SupportsKeysAndGetItem)
    assert not isinstance(duck, Mapping)

    md = cls(duck)

    assert len(md) == 2
    assert list(md.items()) == [("p", 100), ("p", 200)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, dict, multidict.MultiDict])
def test_creation_with_kwargs(
    cls: type[MultiDict | ListMultiDict | dict | multidict.MultiDict],
) -> None:
    md = cls(a=1, b=2, c=3)

    assert len(md) == 3
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, dict, multidict.MultiDict])
def test_creation_mixed(
    cls: type[MultiDict | ListMultiDict | dict | multidict.MultiDict],
) -> None:
    pairs = [("a", 1), ("b", 2)]
    md = cls(pairs, c=3, d=4)

    assert len(md) == 4
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3
    assert md["d"] == 4


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getitem(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    assert md["a"] == 1
    assert md["b"] == 2

    with pytest.raises(KeyError):
        _ = md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_new_key(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()
    md["new"] = "value"

    assert len(md) == 1
    assert md["new"] == "value"
    assert list(md.items()) == [("new", "value")]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_existing_key(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    md["a"] = 99

    assert len(md) == 2
    assert md["a"] == 99
    assert list(md.items()) == [("a", 99), ("b", 2)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_add_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()
    md.add("key", "value1")
    md.add("key", "value2")
    md.add("other", "value3")

    assert len(md) == 3
    assert md["key"] == "value1"
    assert md["other"] == "value3"
    assert list(md.items()) == [
        ("key", "value1"),
        ("key", "value2"),
        ("other", "value3"),
    ]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_delitem(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])
    del md["a"]

    assert len(md) == 2
    assert list(md.items()) == [("b", 2), ("c", 4)]

    with pytest.raises(KeyError):
        del md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_iteration(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    keys = list(md)

    assert keys == ["a", "b", "a"]

    key_count: dict[str, int] = {}
    for key in md:
        key_count[key] = key_count.get(key, 0) + 1

    assert key_count == {"a": 2, "b": 1}


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_len(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()
    assert len(md) == 0

    md.add("a", 1)
    assert len(md) == 1

    md.add("a", 2)
    assert len(md) == 2

    md["b"] = 3
    assert len(md) == 3

    del md["a"]
    assert len(md) == 1


def test_repr() -> None:
    md_empty = MultiDict()
    assert repr(md_empty) == "MultiDict([])"

    md_single = MultiDict([("a", 1)])
    assert repr(md_single) == "MultiDict([('a', 1)])"

    md_multi = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    assert repr(md_multi) == "MultiDict([('a', 1), ('b', 2), ('a', 3)])"

    original = MultiDict([("x", "hello"), ("y", 42), ("x", "world")])
    repr_str = repr(original)
    recreated = eval(repr_str)
    assert list(original.items()) == list(recreated.items())


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_contains(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    assert "a" in md
    assert "b" in md
    assert "missing" not in md
    assert None not in md

    empty_md = cls()
    assert "any" not in empty_md


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getone_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    assert md.getone("a") == 1
    assert md.getone("b") == 2

    assert md.getone("missing", "default") == "default"
    assert md.getone("missing", None) is None

    with pytest.raises(KeyError):
        md.getone("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getall_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])

    assert md.getall("a") == [1, 3]
    assert md.getall("b") == [2]
    assert md.getall("c") == [4]

    assert md.getall("missing", []) == []
    assert md.getall("missing", "default") == "default"

    with pytest.raises(KeyError):
        md.getall("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_get_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    assert md.get("a") == 1
    assert md.get("b") == 2

    assert md.get("missing") is None
    assert md.get("missing", "default") == "default"
    assert md.get("missing", 42) == 42


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popone_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])

    result = md.popone("a")
    assert result == 1
    assert len(md) == 3
    assert md.getall("a") == [3]

    result = md.popone("b")
    assert result == 2
    assert len(md) == 2
    with pytest.raises(KeyError):
        md.getall("b")

    result2 = md.popone("missing", "default")
    assert result2 == "default"
    assert len(md) == 2

    with pytest.raises(KeyError):
        md.popone("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popall_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])

    result = md.popall("a")
    assert result == [1, 3]
    assert len(md) == 2
    with pytest.raises(KeyError):
        md.getall("a")

    result = md.popall("b")
    assert result == [2]
    assert len(md) == 1

    result = md.popall("missing", [])
    assert result == []
    assert len(md) == 1

    result2 = md.popall("missing", "default")
    assert result2 == "default"

    with pytest.raises(KeyError):
        md.popall("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_pop_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    result = md.pop("a")
    assert result == 1
    assert md.getall("a") == [3]

    result2 = md.pop("missing", "default")
    assert result2 == "default"

    with pytest.raises(KeyError):
        md.pop("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    original_len = len(md)

    key, value = md.popitem()
    assert key == "a"
    assert value == 3
    assert len(md) == original_len - 1

    single_md = cls([("x", 42)])
    key, value = single_md.popitem()
    assert key == "x"
    assert value == 42
    assert len(single_md) == 0

    empty_md = cls()
    with pytest.raises(KeyError):
        empty_md.popitem()


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
@pytest.mark.parametrize(
    "items",
    [
        [("a", 1)],
        [("a", 1), ("b", 2)],
        [("a", 1), ("b", 2), ("c", 3)],
        [("a", 1), ("a", 2)],
        [("a", 1), ("b", 2), ("a", 3)],
        [("b", 2), ("a", 1), ("b", 22)],
        [("x", 0), ("y", 1), ("x", 2), ("z", 3), ("y", 4), ("x", 5)],
    ],
)
def test_popitem_removes_the_last_item(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
    items: list[tuple[str, int]],
) -> None:
    md = cls(items)

    assert md.popitem() == items[-1]
    assert list(md.items()) == items[:-1]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_drains_in_reverse_order(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    items = [("a", 1), ("b", 2), ("a", 3), ("c", 4)]
    md = cls(items)

    assert [md.popitem() for _ in range(len(items))] == items[::-1]
    assert len(md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_takes_the_last_item_for_a_repeated_key(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2)])
    md.add("a", 3)

    assert md.popitem() == ("a", 3)
    assert list(md.items()) == [("a", 1), ("b", 2)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_forgets_the_key_of_the_popped_item(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2)])

    assert md.popitem() == ("b", 2)
    assert "b" not in md
    with pytest.raises(KeyError):
        md["b"]

    assert md.popitem() == ("a", 1)
    assert "a" not in md
    assert len(md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_on_empty_raises_key_error(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()

    with pytest.raises(KeyError):
        md.popitem()

    def drain() -> Iterator[tuple[str, int]]:
        while True:
            yield md.popitem()

    md.add("a", 1)
    with pytest.raises(KeyError):
        list(drain())


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setdefault_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2)])

    result = md.setdefault("a", 999)
    assert result == 1
    assert md["a"] == 1
    assert len(md) == 2

    result = md.setdefault("c", 3)
    assert result == 3
    assert md["c"] == 3
    assert len(md) == 3

    result = md.setdefault("d", None)
    assert result is None
    assert md["d"] is None
    assert len(md) == 4

    result = md.setdefault("e")
    assert result is None
    assert md["e"] is None
    assert len(md) == 5


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_clear_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])

    assert len(md) == 4
    md.clear()

    assert len(md) == 0
    assert list(md.items()) == []
    assert list(md.keys()) == []
    assert list(md.values()) == []

    empty_md = cls()
    empty_md.clear()
    assert len(empty_md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_extend_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1)])

    md.extend([("b", 2), ("a", 3), ("c", 4)])
    assert len(md) == 4
    assert list(md.items()) == [("a", 1), ("b", 2), ("a", 3), ("c", 4)]

    md2 = cls([("x", 10)])
    md2.extend({"y": 20, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 10
    assert md2["y"] == 20
    assert md2["z"] == 30

    md3 = cls([("m", 100)])
    other_md = cls([("n", 200), ("m", 300)])
    md3.extend(other_md)
    assert len(md3) == 3
    assert list(md3.items()) == [("m", 100), ("n", 200), ("m", 300)]

    md4 = cls([("a", 1)])
    md4.extend(b=2, c=3)
    assert len(md4) == 3
    assert md4["a"] == 1
    assert md4["b"] == 2
    assert md4["c"] == 3

    md5 = cls()
    md5.extend([("x", 1)], y=2, z=3)
    assert len(md5) == 3
    assert md5["x"] == 1
    assert md5["y"] == 2
    assert md5["z"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_merge_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2)])

    md.merge([("a", 999), ("c", 3), ("d", 4)])
    assert len(md) == 4
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3
    assert md["d"] == 4

    md2 = cls([("x", 10), ("y", 20)])
    md2.merge({"x": 999, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 10
    assert md2["y"] == 20
    assert md2["z"] == 30

    md3 = cls([("a", 1)])
    md3.merge(a=999, b=2, c=3)
    assert len(md3) == 3
    assert md3["a"] == 1
    assert md3["b"] == 2
    assert md3["c"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_update_method(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])

    md.update([("a", 999), ("c", 4), ("a", 5)])
    assert len(md) == 4
    assert md["a"] == 999
    assert md["b"] == 2
    assert md["c"] == 4
    assert md.getall("a") == [999, 5]
    assert list(md.items()) == [("a", 999), ("b", 2), ("a", 5), ("c", 4)]

    md2 = cls([("x", 10), ("y", 20)])
    md2.update({"x": 999, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 999
    assert md2["y"] == 20
    assert md2["z"] == 30
    assert list(md2.items()) == [("x", 999), ("y", 20), ("z", 30)]

    md3 = cls([("a", 1), ("b", 2)])
    md3.update(a=999, c=3)
    assert len(md3) == 3
    assert md3["a"] == 999
    assert md3["b"] == 2
    assert md3["c"] == 3
    assert list(md3.items()) == [("a", 999), ("b", 2), ("c", 3)]

    md4 = cls([("a", 1), ("b", 2)])
    md4.update([("a", 999), ("c", 3)], a=4)
    assert len(md4) == 4
    assert md4["a"] == 999
    assert md4["b"] == 2
    assert md4["c"] == 3
    assert md4.getall("a") == [999, 4]
    assert list(md4.items()) == [("a", 999), ("b", 2), ("c", 3), ("a", 4)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_update_replaces_in_place(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("c", 3)])
    md.update([("b", 99)])
    assert list(md.items()) == [("a", 1), ("b", 99), ("c", 3)]

    md2 = cls([("a", 1), ("b", 2), ("c", 3)])
    md2["b"] = 99
    assert list(md2.items()) == list(md.items())

    md3 = cls([("a", 1), ("b", 2), ("b", 22), ("c", 3)])
    md3.update([("b", 99)])
    assert list(md3.items()) == [("a", 1), ("b", 99), ("c", 3)]

    md4 = cls([("a", 1), ("b", 2), ("b", 22), ("c", 3)])
    md4.update([("b", 99), ("b", 100), ("b", 101)])
    assert list(md4.items()) == [("a", 1), ("b", 99), ("b", 100), ("c", 3), ("b", 101)]

    md5 = cls([("a", 1), ("b", 2)])
    md5.update([("z", 9), ("b", 99), ("y", 8)])
    assert list(md5.items()) == [("a", 1), ("b", 99), ("z", 9), ("y", 8)]

    md6 = cls([("a", 1), ("b", 2)])
    md6.update([("b", 5), ("a", 4), ("b", 6), ("a", 7)])
    assert list(md6.items()) == [("a", 4), ("b", 5), ("b", 6), ("a", 7)]

    md7 = cls()
    md7.update([("a", 1), ("a", 2)])
    assert list(md7.items()) == [("a", 1), ("a", 2)]

    md8 = cls([("a", 1), ("b", 2), ("a", 3)])
    md8.update()
    assert list(md8.items()) == [("a", 1), ("b", 2), ("a", 3)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, dict])
def test_update_method_from_duck_mapping(
    cls: type[MultiDict | ListMultiDict | dict],
) -> None:
    class DuckMapping:
        def __init__(self, items: Iterable[tuple[str, int]], /) -> None:
            self._dict = dict(items)

        def __getitem__(self, key: str, /) -> int:
            return self._dict[key]

        def keys(self) -> Iterable[str]:
            return self._dict.keys()

    assert issubclass(DuckMapping, SupportsKeysAndGetItem)
    assert not issubclass(DuckMapping, MappingLike)
    assert not issubclass(DuckMapping, Mapping)

    d = cls([("a", 1)])
    duck = DuckMapping({"a": 999, "b": 2})

    assert isinstance(duck, SupportsKeysAndGetItem)
    d.update(duck)
    assert len(d) == 2
    assert d["a"] == 999
    assert d["b"] == 2


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict])
def test_update_method_from_duck_multi_mapping(
    cls: type[MultiDict | ListMultiDict],
) -> None:
    class DuckMultiMapping:
        def __init__(self, items: Iterable[tuple[str, int]], /) -> None:
            self._items = list(items)

        def __getitem__(self, key: str, /) -> int:
            assert False

        def keys(self) -> Iterable[str]:
            assert False

        def items(self) -> Iterable[tuple[str, int]]:
            return self._items

    assert issubclass(DuckMultiMapping, MappingLike)
    assert issubclass(DuckMultiMapping, SupportsKeysAndGetItem)
    assert not issubclass(DuckMultiMapping, Mapping)

    d = cls([("a", 1)])
    duck = DuckMultiMapping([("a", 999), ("b", 2)])

    assert isinstance(duck, MappingLike)
    d.update(duck)
    assert len(d) == 2
    assert d["a"] == 999
    assert d["b"] == 2


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_none_values(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()

    md.add("key", None)
    md.add("key", "value")
    md.add("other", None)

    assert len(md) == 3
    assert md["key"] is None
    assert md.getall("key") == [None, "value"]
    assert md["other"] is None

    md["new"] = None
    assert md["new"] is None

    assert "key" in md
    assert "other" in md
    assert "new" in md


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_empty_operations(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()

    assert len(md) == 0
    assert list(md) == []
    assert list(md.items()) == []
    assert list(md.values()) == []
    assert list(md.keys()) == []

    with pytest.raises(KeyError):
        _ = md["missing"]

    with pytest.raises(KeyError):
        md.getone("missing")

    with pytest.raises(KeyError):
        md.getall("missing")

    assert md.get("missing") is None
    assert md.get("missing", "default") == "default"

    with pytest.raises(KeyError):
        md.popone("missing")

    with pytest.raises(KeyError):
        md.popall("missing")

    assert md.popone("missing", "default") == "default"
    assert md.popall("missing", []) == []

    md.clear()
    assert len(md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_single_item_operations(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("single", "value")])

    assert len(md) == 1
    assert md["single"] == "value"
    assert md.getone("single") == "value"
    assert md.getall("single") == ["value"]

    result = md.popone("single")
    assert result == "value"
    assert len(md) == 0

    with pytest.raises(KeyError):
        _ = md["single"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_duplicate_handling(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls()

    for i in range(5):
        md.add("key", i)

    assert len(md) == 5
    assert md["key"] == 0
    assert md.getall("key") == [0, 1, 2, 3, 4]

    result = md.popone("key")
    assert result == 0
    assert md.getall("key") == [1, 2, 3, 4]

    result2 = md.popall("key")
    assert result2 == [1, 2, 3, 4]
    assert len(md) == 0

    md.add("key", 1)
    md.add("key", 2)
    md.add("key", 3)
    md["key"] = 999
    assert len(md) == 1
    assert md["key"] == 999


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict])
def test_edge_cases_mixed_types(
    cls: type[MultiDict | ListMultiDict],
) -> None:
    md: MutableMultiMapping[object, str] = cls()

    md.add("string", "value1")
    md.add(42, "value2")
    md.add(("tuple", "key"), "value3")
    md.add(None, "value4")

    assert len(md) == 4
    assert md["string"] == "value1"
    assert md[42] == "value2"
    assert md[("tuple", "key")] == "value3"
    assert md[None] == "value4"

    md2 = cls()
    md2.add("key", "string")
    md2.add("key", 42)
    md2.add("key", [1, 2, 3])
    md2.add("key", {"nested": "dict"})

    assert len(md2) == 4
    assert md2.getall("key") == ["string", 42, [1, 2, 3], {"nested": "dict"}]


def test_edge_cases_multidict_specific() -> None:
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])

    assert len(md._items) == 3
    assert len(md._key_indices) == 2
    assert md._key_indices["a"] == [0, 2]
    assert md._key_indices["b"] == [1]

    del md["a"]
    assert len(md._items) == 1
    assert len(md._key_indices) == 1
    assert "a" not in md._key_indices
    assert md._key_indices["b"] == [0]

    md.add("c", 1)
    md.add("c", 2)
    md.add("c", 3)
    md["c"] = 999

    assert len(md._items) == 2
    assert md._key_indices["c"] == [1]


@pytest.mark.parametrize("cls", [MultiDict, multidict.MultiDict])
def test_copy_method(cls: type[MultiDict | multidict.MultiDict]) -> None:
    empty_md = cls()
    empty_copy = empty_md.copy()
    assert len(empty_copy) == 0
    assert list(empty_copy.items()) == []
    assert empty_md is not empty_copy

    single_md = cls([("a", 1)])
    single_copy = single_md.copy()
    assert len(single_copy) == 1
    assert list(single_copy.items()) == [("a", 1)]
    assert single_md is not single_copy

    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])
    copied = md.copy()

    assert len(copied) == len(md)
    assert list(copied.items()) == list(md.items())
    assert list(copied.keys()) == list(md.keys())
    assert list(copied.values()) == list(md.values())

    assert copied.getall("a") == md.getall("a") == [1, 3]

    assert md is not copied

    md.add("d", 5)
    assert len(md) == 5
    assert len(copied) == 4
    assert "d" not in copied

    copied.add("e", 6)
    assert len(copied) == 5
    assert len(md) == 5
    assert "e" not in md


def test_exception_safety() -> None:
    class BadKey:
        def __hash__(self) -> int:
            raise RuntimeError("I'm a bad key")

    md: MultiDict[str | BadKey, str] = MultiDict([("good", "value")])
    with pytest.raises(RuntimeError):
        md.add(BadKey(), "value")

    assert list(md.items()) == [("good", "value")]


def test_empty_init_no_rebuild() -> None:
    md = MultiDict()
    assert len(md._items) == 0
    assert len(md._key_indices) == 0


def test_update_with_empty_input() -> None:
    md = MultiDict([("a", 1)])
    md.update()
    assert len(md) == 1
    assert md["a"] == 1

    md.update([])
    assert len(md) == 1
    assert md["a"] == 1


def test_merge_with_empty_input() -> None:
    md = MultiDict([("a", 1)])
    md.merge()
    assert len(md) == 1
    assert md["a"] == 1

    md.merge([])
    assert len(md) == 1
    assert md["a"] == 1


def test_extend_with_empty_input() -> None:
    md = MultiDict([("a", 1)])
    md.extend()
    assert len(md) == 1
    assert md["a"] == 1

    md.extend([])
    assert len(md) == 1
    assert md["a"] == 1


def test_merge_all_existing_keys() -> None:
    md = MultiDict([("a", 1), ("b", 2)])
    md.merge([("a", 999), ("b", 888)])
    assert len(md) == 2
    assert md["a"] == 1
    assert md["b"] == 2


def test_merge_existing_key_in_indices() -> None:
    md = MultiDict([("a", 1)])
    existing_keys = set(md._key_indices.keys())
    assert "a" in existing_keys

    md.merge([("b", 2)])
    assert "b" in md._key_indices
    assert md["b"] == 2


def test_extend_existing_key_in_indices() -> None:
    md = MultiDict([("a", 1)])

    md.extend([("a", 2)])
    assert len(md._key_indices["a"]) == 2
    assert md._key_indices["a"] == [0, 1]


def test_update_only_updates_no_additions() -> None:
    md = MultiDict([("a", 1), ("b", 2)])
    md.update([("a", 999), ("b", 888)])

    assert len(md) == 2
    assert md["a"] == 999
    assert md["b"] == 888


def test_update_only_additions_no_updates() -> None:
    md = MultiDict([("a", 1)])
    md.update([("b", 2), ("c", 3)])

    assert len(md) == 3
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3


def test_init_with_no_items_and_no_kwargs() -> None:
    md = MultiDict(())
    assert len(md._items) == 0
    assert len(md._key_indices) == 0


def test_update_keeps_indices_consistent() -> None:
    md = MultiDict([("a", 1), ("b", 2), ("a", 3), ("c", 4)])
    md.update([("a", 999), ("d", 5), ("a", 6), ("a", 7)])

    assert md._items == [("a", 999), ("b", 2), ("a", 6), ("c", 4), ("d", 5), ("a", 7)]
    assert md._key_indices == {"a": [0, 2, 5], "b": [1], "c": [3], "d": [4]}


def test_multidict_equality() -> None:
    md1 = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    md2 = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    md3 = MultiDict([("a", 1), ("b", 2)])
    md4 = MultiDict([("b", 2), ("a", 1), ("a", 3)])

    assert md1 == md2
    assert md1 != md3
    assert md1 != md4

    empty1 = MultiDict()
    empty2 = MultiDict()
    assert empty1 == empty2
    assert md1 != empty1

    mdict1 = multidict.MultiDict([("a", 1), ("b", 2), ("a", 3)])
    mdict2 = multidict.MultiDict([("a", 1), ("b", 2)])
    mdict3 = multidict.MultiDict([("b", 2), ("a", 1), ("a", 3)])

    assert md1 == mdict1
    assert md1 != mdict2
    assert md1 != mdict3

    lmd1 = ListMultiDict([("a", 1), ("b", 2), ("a", 3)])
    lmd2 = ListMultiDict([("a", 1), ("b", 2)])
    lmd3 = ListMultiDict([("b", 2), ("a", 1), ("a", 3)])

    assert md1 == lmd1
    assert md1 != lmd2
    assert md1 != lmd3

    md_no_dups = MultiDict([("a", 1), ("b", 2)])
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 3, "b": 2}
    dict3 = {"a": 1, "b": 2, "c": 4}
    dict4 = {"a": 1}

    assert md_no_dups == dict1
    assert md_no_dups != dict2
    assert md_no_dups != dict3
    assert md_no_dups != dict4

    assert md1 != dict1

    md_partial = MultiDict([("a", 1)])
    dict_with_missing = {"b": 2}
    assert md_partial != dict_with_missing

    assert md1.__eq__("string") is NotImplemented
    assert md1.__eq__(42) is NotImplemented
    assert md1.__eq__([1, 2, 3]) is NotImplemented
    assert md1.__eq__(None) is NotImplemented

    assert (md1 == "string") is False
    assert (md1 == 42) is False
    assert (md1 == [1, 2, 3]) is False
    assert (md1 is None) is False

    empty_dict = {}
    assert empty1 == empty_dict

    md_special = MultiDict([("a", None), ("b", 0), ("c", "")])
    dict_special = {"a": None, "b": 0, "c": ""}
    assert md_special == dict_special

    lmd_shorter = ListMultiDict([("a", 1)])
    assert md1 != lmd_shorter
