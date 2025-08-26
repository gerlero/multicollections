# Test Configuration

This directory contains the test suite for multicollections.

## Running Tests

### Using unittest (always available)
```bash
python -m unittest discover tests -v
```

### Using pytest (if available)
```bash
pytest tests/ -v
```

### Using our custom test runner
```bash
python tests/run_tests.py
```

## Test Files

- `test_basic.py` - Basic functionality tests for MultiDict
- `test_multidict_compatibility.py` - Compatibility tests with multidict (when available)
- `run_tests.py` - Custom test runner that works with or without pytest

## Test Coverage

The test suite covers:
- Basic MultiDict creation (empty, from pairs, from dict, with kwargs)
- Getting, setting, and deleting items
- The `add()` method for adding duplicate keys
- Iteration over keys, values, and items
- View objects (values(), items())
- Edge cases and error handling
- Interface compatibility with multidict.MultiDict (when available)