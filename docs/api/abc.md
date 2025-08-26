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
        self._key_indices = {}  # Maps keys to lists of indices in _items
    
    def __getitem__(self, key):
        if key not in self._key_indices:
            raise KeyError(key)
        first_index = self._key_indices[key][0]
        return self._items[first_index][1]  # Return first value
    
    def __setitem__(self, key, value):
        if key in self._key_indices:
            # Replace first occurrence and remove others
            indices = self._key_indices[key]
            first_index = indices[0]
            self._items[first_index] = (key, value)
            
            if len(indices) > 1:
                # Mark duplicates for removal
                for idx in indices[1:]:
                    self._items[idx] = None
                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            # Add new item
            self._add_item(key, value)
    
    def __delitem__(self, key):
        if key not in self._key_indices:
            raise KeyError(key)
        
        # Mark items for removal
        indices_to_remove = self._key_indices[key]
        for idx in indices_to_remove:
            self._items[idx] = None
        
        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()
    
    def __iter__(self):
        # Yield keys in insertion order, including duplicates
        for key, _ in self._items:
            yield key
    
    def __len__(self):
        return len(self._items)
    
    def add(self, key, value):
        self._add_item(key, value)
    
    def getall(self, key, default=None):
        if key not in self._key_indices:
            return default if default is not None else []
        
        indices = self._key_indices[key]
        return [self._items[idx][1] for idx in indices]
    
    def _add_item(self, key, value):
        """Add an item and update the key index."""
        index = len(self._items)
        self._items.append((key, value))
        if key not in self._key_indices:
            self._key_indices[key] = []
        self._key_indices[key].append(index)
    
    def _rebuild_indices(self):
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)
```

## API Reference

::: multicollections.abc