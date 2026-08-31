from __future__ import annotations

import multidict
import pytest

from multicollections import MultiDict

from .minimalimpl import ListMultiDict


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_keys_view(
    cls: type[MultiDict[str, int] | ListMultiDict[str, int] | multidict.MultiDict[int]],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    keys = md.keys()

    assert len(keys) == 3
    assert list(keys) == ["a", "b", "a"]

    assert "a" in keys
    assert "b" in keys
    assert "missing" not in keys

    empty_md = cls()
    empty_keys = empty_md.keys()
    assert len(empty_keys) == 0
    assert list(empty_keys) == []


@pytest.mark.parametrize("cls1", [MultiDict, ListMultiDict, dict, multidict.MultiDict])
@pytest.mark.parametrize("cls2", [MultiDict, ListMultiDict, dict, multidict.MultiDict])
def test_keys_view_set_operations(cls1, cls2) -> None:
    md1 = cls1([("a", 1), ("b", 2), ("a", 3)])
    md2 = cls2([("a", 4), ("c", 5)])

    keys1 = md1.keys()

    assert keys1 & {"a"} == {"a"}
    assert keys1 | {"a"} == {"a", "b"}
    assert keys1 - {"a"} == {"b"}
    assert {"a"} - keys1 == set()
    assert keys1 ^ {"a"} == {"b"}
    assert keys1.isdisjoint({"c"})
    assert not keys1.isdisjoint({"a"})

    keys2 = md2.keys()

    assert keys1 & keys2 == {"a"}
    assert keys1 | keys2 == {"a", "b", "c"}
    assert keys1 - keys2 == {"b"}
    assert keys2 - keys1 == {"c"}
    assert keys1 ^ keys2 == {"b", "c"}
    assert not keys1.isdisjoint(keys2)


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_values_view(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    values = md.values()

    assert len(values) == 3
    assert list(values) == [1, 2, 3]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_values_view_contains(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    values = md.values()

    assert 1 in values
    assert 2 in values
    assert 3 in values

    assert 4 not in values
    assert 0 not in values

    empty_md = cls()
    empty_values = empty_md.values()
    assert 1 not in empty_values


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    items = md.items()

    assert len(items) == 3
    assert list(items) == [("a", 1), ("b", 2), ("a", 3)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view_contains(
    cls: type[MultiDict | ListMultiDict | multidict.MultiDict],
) -> None:
    md = cls([("a", 1), ("b", 2), ("a", 3)])
    items = md.items()

    assert ("a", 1) in items
    assert ("b", 2) in items
    assert ("a", 3) in items

    assert ("a", 2) not in items
    assert ("c", 1) not in items
    assert ("b", 1) not in items

    assert ("a", 3, "a") not in items  # ty: ignore[unsupported-operator]

    assert None not in items  # ty: ignore[unsupported-operator]

    empty_md = cls()
    empty_items = empty_md.items()
    assert ("a", 1) not in empty_items


@pytest.mark.parametrize("cls1", [MultiDict, ListMultiDict, multidict.MultiDict])
@pytest.mark.parametrize("cls2", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view_set_operations(cls1, cls2) -> None:
    md1 = cls1([("a", 1), ("b", 2), ("a", 3)])
    md2 = cls2([("a", 4), ("c", 5), ("a", 3)])

    items1 = md1.items()

    assert items1 & {("a", 3)} == {("a", 3)}
    assert items1 | {("a", 3)} == {("a", 1), ("b", 2), ("a", 3)}
    assert items1 - {("a", 3)} == {("a", 1), ("b", 2)}
    assert {("a", 2)} - items1 == {("a", 2)}
    assert items1 ^ {("a", 3)} == {("a", 1), ("b", 2)}
    assert items1.isdisjoint({("a", 4)})
    assert not items1.isdisjoint({("a", 3)})

    items2 = md2.items()

    assert items1 & items2 == {("a", 3)}
    assert items1 | items2 == {("a", 1), ("b", 2), ("a", 3), ("a", 4), ("c", 5)}
    assert items1 - items2 == {("a", 1), ("b", 2)}
    assert items2 - items1 == {("a", 4), ("c", 5)}
    assert items1 ^ items2 == {("a", 1), ("b", 2), ("a", 4), ("c", 5)}
    assert not items1.isdisjoint(items2)
