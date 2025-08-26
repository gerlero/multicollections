"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import sys
from abc import abstractmethod
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Iterator,
        Mapping,
        MutableMapping,
    )
else:
    from typing import (
        Iterator,
        Mapping,
        MutableMapping,
    )

K = TypeVar("K")
V = TypeVar("V")


class MultiMapping(Mapping[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    
    Only two methods need to be implemented by subclasses:
    - __iter__: yields all keys (with duplicates) in order
    - getall: returns all values for a key
    
    All other methods have default implementations based on these.
    """

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError

    @abstractmethod
    def getall(self, key: K, default: list[V] | None = None) -> list[V]:
        """Get all values for a key.

        Returns the default value if the key is not found.
        """
        raise NotImplementedError

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        values = self.getall(key, [])
        if not values:
            raise KeyError(key)
        return values[0]

    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        return sum(1 for _ in self)

    def items(self):
        """Return a view of the items in the multi-mapping.
        
        This override of Mapping.items() ensures that all key-value pairs
        are returned, including duplicate keys with different values.
        """
        from collections.abc import ItemsView
        
        class MultiMappingItemsView(ItemsView):
            def __init__(self, mapping):
                self._mapping = mapping
            
            def __iter__(self):
                # Build a list of all items by tracking key occurrences
                seen_counts = {}
                for key in self._mapping:
                    if key not in seen_counts:
                        seen_counts[key] = 0
                    values = self._mapping.getall(key)
                    if seen_counts[key] < len(values):
                        yield (key, values[seen_counts[key]])
                        seen_counts[key] += 1
            
            def __len__(self):
                return len(self._mapping)
        
        return MultiMappingItemsView(self)

    def values(self):
        """Return a view of the values in the multi-mapping.
        
        This override of Mapping.values() ensures that all values
        are returned in the correct order.
        """
        from collections.abc import ValuesView
        
        class MultiMappingValuesView(ValuesView):
            def __init__(self, mapping):
                self._mapping = mapping
            
            def __iter__(self):
                for key, value in self._mapping.items():
                    yield value
            
            def __len__(self):
                return len(self._mapping)
        
        return MultiMappingValuesView(self)


class MutableMultiMapping(MultiMapping[K, V], MutableMapping[K, V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    
    Only two methods need to be implemented by subclasses:
    - add: adds a value for a key without removing existing values
    - __delitem__: removes all values for a key
    
    __setitem__ has a default implementation that deletes the key and then adds the new value.
    """

    @abstractmethod
    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, key: K, value: V) -> None:
        """Add a value for a key.

        This should add the value without removing existing values for the key.
        """
        raise NotImplementedError

    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        This replaces all existing values for the key with a single new value.
        Default implementation removes the key if it exists, then adds the new value.
        """
        try:
            del self[key]
        except KeyError:
            pass
        self.add(key, value)
