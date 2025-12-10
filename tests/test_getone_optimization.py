"""Test that MultiDict.getone doesn't call getall."""
from __future__ import annotations

import inspect
import time

from multicollections import MultiDict


def test_getone_does_not_call_getall() -> None:
    """Verify that MultiDict.getone doesn't call getall."""
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])

    # Get the actual method implementation
    getone_method = md.getone.__func__

    # Check that getone is implemented in MultiDict, not just inherited
    assert getone_method.__qualname__ == "MultiDict.getone"

    # Check that the implementation doesn't call getall
    source = inspect.getsource(getone_method)
    assert "getall" not in source, "getone should not call getall"

    # Verify functionality still works
    assert md.getone("a") == 1
    assert md.getone("b") == 2
    assert md.getone("missing", "default") == "default"


def test_getone_performance() -> None:
    """Verify that getone is O(1) and doesn't iterate through all values."""
    # Create a MultiDict with many values for one key
    md = MultiDict()
    for i in range(10000):
        md.add("key", i)

    # Time getone - should be very fast (O(1))
    start = time.time()
    for _ in range(1000):
        result = md.getone("key")
    getone_time = time.time() - start

    # Time getall - should be much slower (O(n))
    start = time.time()
    for _ in range(1000):
        all_values = md.getall("key")
    getall_time = time.time() - start

    # getone should be significantly faster than getall
    # If getone was calling getall, they would have similar performance
    assert getone_time < getall_time / 10, (
        f"getone ({getone_time:.6f}s) should be much faster than "
        f"getall ({getall_time:.6f}s)"
    )

    # Verify results are correct
    assert result == 0
    assert len(all_values) == 10000
