# Abstract Base Classes

The `multicollections.abc` module provides abstract base classes for multi-mapping collections. These classes define the interface for multi-mappings and provide useful default implementations for common operations.

## Overview

Multi-mappings are collections that can hold multiple values for the same key. The abstract base classes in this module provide a foundation for implementing such collections:

- **`MultiMapping`**: Read-only interface for multi-mappings
- **`MutableMultiMapping`**: Mutable interface that extends `MultiMapping`

## Usage Example

```python
from multicollections.abc import MutableMultiMapping

class MyMultiMap(MutableMultiMapping):
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data[key][0]  # Return first value
    
    def __setitem__(self, key, value):
        self._data[key] = [value]  # Replace all values
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __iter__(self):
        for key, values in self._data.items():
            for _ in values:
                yield key
    
    def __len__(self):
        return sum(len(values) for values in self._data.values())
    
    def add(self, key, value):
        if key in self._data:
            self._data[key].append(value)
        else:
            self._data[key] = [value]
```

## API Reference

::: multicollections.abc