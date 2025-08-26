"""Tests for the minimal ABC interface.

This module tests that the ABC provides sufficient default implementations
so that only a minimal set of methods need to be implemented by subclasses.
"""

import pytest
from multicollections.abc import MutableMultiMapping
from typing import Iterator


class MinimalMultiMapping(MutableMultiMapping):
    """A minimal implementation using only the 4 required abstract methods."""
    
    def __init__(self):
        self._data = {}
        self._order = []
    
    def __iter__(self) -> Iterator:
        """Required: yield all keys in order (with duplicates)."""
        return iter(self._order)
    
    def getall(self, key, default=None):
        """Required: get all values for a key."""
        if key in self._data:
            return self._data[key][:]
        return default if default is not None else []
    
    def add(self, key, value):
        """Required: add a value for a key."""
        if key not in self._data:
            self._data[key] = []
        self._data[key].append(value)
        self._order.append(key)
    
    def __delitem__(self, key):
        """Required: remove all values for a key."""
        if key not in self._data:
            raise KeyError(key)
        self._order = [k for k in self._order if k != key]
        del self._data[key]


class TestMinimalInterface:
    """Test that the minimal ABC interface provides full functionality."""
    
    def test_only_four_methods_needed(self):
        """Test that only 4 abstract methods need to be implemented."""
        mm = MinimalMultiMapping()
        
        # All these methods should work despite not being implemented directly
        assert hasattr(mm, '__getitem__')  # Provided by ABC
        assert hasattr(mm, '__len__')      # Provided by ABC
        assert hasattr(mm, '__setitem__')  # Provided by ABC
        assert hasattr(mm, 'items')        # Provided by ABC
        assert hasattr(mm, 'values')       # Provided by ABC
        assert hasattr(mm, 'get')          # Inherited from Mapping
        assert hasattr(mm, '__contains__') # Inherited from Mapping

    def test_minimal_implementation_functionality(self):
        """Test that minimal implementation provides correct behavior."""
        mm = MinimalMultiMapping()
        
        # Test basic operations
        mm.add('a', 1)
        mm.add('a', 2)
        mm.add('b', 3)
        
        # Test getall (implemented)
        assert mm.getall('a') == [1, 2]
        assert mm.getall('b') == [3]
        assert mm.getall('missing') == []
        assert mm.getall('missing', ['default']) == ['default']
        
        # Test __iter__ (implemented)
        assert list(mm) == ['a', 'a', 'b']
        
        # Test __getitem__ (ABC default)
        assert mm['a'] == 1  # First value
        assert mm['b'] == 3
        with pytest.raises(KeyError):
            _ = mm['missing']
        
        # Test __len__ (ABC default)
        assert len(mm) == 3
        
        # Test items() (ABC default)
        assert list(mm.items()) == [('a', 1), ('a', 2), ('b', 3)]
        
        # Test values() (ABC default)
        assert list(mm.values()) == [1, 2, 3]
        
        # Test __setitem__ (ABC default)
        mm['a'] = 99
        assert mm.getall('a') == [99]
        assert len(mm) == 2
        assert list(mm.items()) == [('b', 3), ('a', 99)]
        
        # Test add (implemented)
        mm.add('c', 4)
        assert len(mm) == 3
        assert mm['c'] == 4
        
        # Test __delitem__ (implemented)
        del mm['a']
        assert len(mm) == 2
        assert list(mm.items()) == [('b', 3), ('c', 4)]
        
        # Test inherited methods from Mapping
        assert mm.get('b') == 3
        assert mm.get('missing', 'default') == 'default'
        assert 'b' in mm
        assert 'missing' not in mm

    def test_abc_default_items_and_values(self):
        """Test that ABC provides correct default implementations for items() and values()."""
        mm = MinimalMultiMapping()
        mm.add('x', 10)
        mm.add('y', 20)
        mm.add('x', 30)
        
        # Test items() preserves order and duplicates
        items = list(mm.items())
        assert items == [('x', 10), ('y', 20), ('x', 30)]
        
        # Test values() preserves order
        values = list(mm.values())
        assert values == [10, 20, 30]
        
        # Test that views have correct length
        assert len(mm.items()) == 3
        assert len(mm.values()) == 3

    def test_abc_default_setitem(self):
        """Test that ABC provides correct default implementation for __setitem__."""
        mm = MinimalMultiMapping()
        
        # Test setting new key
        mm['new'] = 'value'
        assert mm.getall('new') == ['value']
        assert len(mm) == 1
        
        # Test replacing existing key with multiple values
        mm.add('key', 1)
        mm.add('key', 2)
        mm.add('key', 3)
        assert mm.getall('key') == [1, 2, 3]
        assert len(mm) == 4
        
        # Set should replace all values
        mm['key'] = 99
        assert mm.getall('key') == [99]
        assert len(mm) == 2  # 'new' + 'key'
        
        # Test setting non-existent key
        mm['another'] = 'test'
        assert mm.getall('another') == ['test']
        assert len(mm) == 3

    def test_comparison_with_multidict(self):
        """Test that minimal implementation behaves like MultiDict."""
        from multicollections import MultiDict
        
        # Same test data
        data = [('a', 1), ('b', 2), ('a', 3), ('c', 4)]
        
        mm = MinimalMultiMapping()
        md = MultiDict(data)
        
        # Add same data to minimal implementation
        for key, value in data:
            mm.add(key, value)
        
        # Both should have same behavior
        assert list(mm) == list(md)
        assert len(mm) == len(md)
        assert list(mm.items()) == list(md.items())
        assert list(mm.values()) == list(md.values())
        assert mm['a'] == md['a']
        assert mm.getall('a') == md.getall('a')
        
        # Test setitem behavior
        mm['a'] = 99
        md['a'] = 99
        assert list(mm.items()) == list(md.items())
        assert mm.getall('a') == md.getall('a')
        
        # Test delitem behavior
        del mm['a']
        del md['a']
        assert list(mm.items()) == list(md.items())