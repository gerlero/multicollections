# Test Suite

This directory contains the pytest-based test suite for multicollections.

## Running Tests

```bash
pytest tests/ -v
```

## Test Files

- `test_basic.py` - Basic functionality tests for MultiDict
- `test_multidict_compatibility.py` - Compatibility tests with multidict (when available)

## Test Coverage

The test suite covers:
- Basic MultiDict creation (empty, from pairs, from dict, with kwargs)
- Getting, setting, and deleting items
- The `add()` method for adding duplicate keys
- Iteration over keys, values, and items
- View objects (values(), items())
- Edge cases and error handling
- Interface compatibility with multidict.MultiDict (when available)

## Compatibility Tests

The compatibility tests automatically skip when the `multidict` library is not available, allowing the test suite to run in any environment while providing full validation when the reference implementation is present.