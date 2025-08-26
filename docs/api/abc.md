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
        self._items = []  # List of (key, value) pairs preserves insertion order
    
    def __getitem__(self, key):
        # Find first occurrence of key
        for k, v in self._items:
            if k == key:
                return v
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        # Find first occurrence and replace, remove any duplicates
        found_first = False
        new_items = []
        
        for k, v in self._items:
            if k == key:
                if not found_first:
                    # Replace first occurrence
                    new_items.append((key, value))
                    found_first = True
                # Skip duplicates (effectively removing them)
            else:
                new_items.append((k, v))
        
        if not found_first:
            # Key not found, add new item
            new_items.append((key, value))
        
        self._items = new_items
    
    def __delitem__(self, key):
        # Remove all occurrences of key
        new_items = []
        found = False
        
        for k, v in self._items:
            if k == key:
                found = True
            else:
                new_items.append((k, v))
        
        if not found:
            raise KeyError(key)
        
        self._items = new_items
    
    def __iter__(self):
        # Yield keys in insertion order, including duplicates
        for key, _ in self._items:
            yield key
    
    def __len__(self):
        return len(self._items)
    
    def add(self, key, value):
        self._items.append((key, value))
    
    def getall(self, key, default=None):
        values = []
        for k, v in self._items:
            if k == key:
                values.append(v)
        return values if values else (default if default is not None else [])
```

## API Reference

::: multicollections.abc