"""Tests for optimized ABC method implementations in MultiDict."""

from __future__ import annotations

from multicollections import MultiDict


def test_contains_optimization() -> None:
    """Test that __contains__ is implemented and works correctly."""
    md: MultiDict[str, int] = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    
    # Test existing key
    assert "a" in md
    assert "b" in md
    
    # Test non-existing key
    assert "missing" not in md
    assert "c" not in md
    
    # Test with None
    assert None not in md
    
    # Test after modifications
    md.add("c", 4)
    assert "c" in md
    
    del md["a"]
    assert "a" not in md
    
    # Test with empty MultiDict
    empty_md: MultiDict[None, None] = MultiDict()
    assert "anything" not in empty_md


def test_get_optimization() -> None:
    """Test that get is implemented and works correctly."""
    md: MultiDict[str, int] = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    
    # Test existing key returns first value
    assert md.get("a") == 1
    assert md.get("b") == 2
    
    # Test non-existing key returns None by default
    assert md.get("missing") is None
    
    # Test non-existing key with default
    assert md.get("missing", 42) == 42
    assert md.get("missing", "default") == "default"
    
    # Test with None value
    md_with_none: MultiDict[str, int | None] = MultiDict([("x", None), ("y", 0)])
    assert md_with_none.get("x") is None
    assert md_with_none.get("y") == 0
    assert md_with_none.get("z") is None
    assert md_with_none.get("z", "default") == "default"
    
    # Test after modifications
    md["a"] = 99
    assert md.get("a") == 99
    
    # Test with empty MultiDict
    empty_md: MultiDict[None, None] = MultiDict()
    assert empty_md.get("anything") is None
    assert empty_md.get("anything", "default") == "default"


def test_setdefault_optimization() -> None:
    """Test that setdefault is implemented and works correctly."""
    md: MultiDict[str, int | None] = MultiDict([("a", 1), ("b", 2)])
    
    # Test existing key returns existing value, doesn't modify
    result = md.setdefault("a", 999)
    assert result == 1
    assert md["a"] == 1
    assert len(md) == 2
    
    # Test non-existing key sets and returns default
    result = md.setdefault("c", 3)
    assert result == 3
    assert md["c"] == 3
    assert len(md) == 3
    
    # Test with None default
    result = md.setdefault("d", None)
    assert result is None
    assert md["d"] is None
    assert len(md) == 4
    
    # Test implicit None default
    result = md.setdefault("e")
    assert result is None
    assert md["e"] is None
    assert len(md) == 5
    
    # Test with duplicate keys
    md_dup: MultiDict[str, int] = MultiDict([("x", 1), ("x", 2), ("x", 3)])
    result = md_dup.setdefault("x", 999)
    assert result == 1  # Returns first value
    assert len(md_dup) == 3  # Doesn't add
    assert md_dup.getall("x") == [1, 2, 3]  # All values preserved
    
    # Test on empty MultiDict
    empty_md: MultiDict[str, int] = MultiDict()
    result = empty_md.setdefault("key", 42)
    assert result == 42
    assert empty_md["key"] == 42
    assert len(empty_md) == 1


def test_optimized_methods_performance() -> None:
    """Test that optimized methods have the expected O(1) performance."""
    # Create a large MultiDict
    md: MultiDict[int, str] = MultiDict()
    for i in range(1000):
        md.add(i, f"value_{i}")
    
    # Test __contains__ - should be O(1)
    assert 500 in md
    assert 9999 not in md
    
    # Test get - should be O(1)
    assert md.get(500) == "value_500"
    assert md.get(9999) is None
    assert md.get(9999, "default") == "default"
    
    # Test setdefault - should be O(1)
    result = md.setdefault(500, "new_value")
    assert result == "value_500"  # Existing value
    
    result = md.setdefault(1000, "value_1000")
    assert result == "value_1000"  # New value
    assert md[1000] == "value_1000"


def test_optimized_methods_with_complex_types() -> None:
    """Test optimized methods with complex key and value types."""
    md: MultiDict[tuple[str, int], dict[str, str]] = MultiDict()
    
    key1 = ("a", 1)
    key2 = ("b", 2)
    val1 = {"x": "y"}
    val2 = {"p": "q"}
    
    # Test __contains__ with complex keys
    assert key1 not in md
    md.add(key1, val1)
    assert key1 in md
    assert key2 not in md
    
    # Test get with complex keys and values
    assert md.get(key1) == val1
    assert md.get(key2) is None
    assert md.get(key2, {"default": "value"}) == {"default": "value"}
    
    # Test setdefault with complex keys and values
    result = md.setdefault(key2, val2)
    assert result == val2
    assert md[key2] == val2
    
    result = md.setdefault(key1, {"new": "dict"})
    assert result == val1  # Existing value
    assert md[key1] == val1


def test_optimized_methods_consistency() -> None:
    """Test that optimized methods are consistent with other MultiDict operations."""
    md: MultiDict[str, int] = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    
    # __contains__ consistency with __getitem__
    for key in ["a", "b"]:
        assert (key in md) == (md.get(key) is not None)
    
    assert ("missing" in md) == (md.get("missing") is not None)
    
    # get consistency with __getitem__
    assert md.get("a") == md["a"]
    assert md.get("b") == md["b"]
    
    # setdefault consistency with add
    md_test: MultiDict[str, int] = MultiDict()
    md_test.setdefault("x", 10)
    assert md_test["x"] == 10
    
    md_compare: MultiDict[str, int] = MultiDict()
    md_compare.add("x", 10)
    assert list(md_test.items()) == list(md_compare.items())
