"""Basic tests for multicollections.MultiDict.

This module provides comprehensive tests for multicollections.MultiDict behavior.
"""

import unittest
from multicollections import MultiDict


class TestMultiDictBasic(unittest.TestCase):
    """Basic functionality tests for MultiDict."""
    
    def test_empty_creation(self):
        """Test creating an empty MultiDict."""
        md = MultiDict()
        self.assertEqual(len(md), 0)
        self.assertEqual(list(md), [])
        self.assertEqual(list(md.items()), [])
        self.assertEqual(list(md.values()), [])
    
    def test_creation_from_pairs(self):
        """Test creating MultiDict from list of pairs."""
        pairs = [('a', 1), ('b', 2), ('a', 3)]
        md = MultiDict(pairs)
        
        self.assertEqual(len(md), 3)
        self.assertEqual(md['a'], 1)  # First value for duplicate key
        self.assertEqual(md['b'], 2)
        self.assertEqual(list(md.items()), pairs)
        self.assertEqual(list(md), ['a', 'b', 'a'])
        self.assertEqual(list(md.values()), [1, 2, 3])
    
    def test_creation_from_dict(self):
        """Test creating MultiDict from regular dict."""
        d = {'x': 10, 'y': 20, 'z': 30}
        md = MultiDict(d)
        
        self.assertEqual(len(md), 3)
        for key, value in d.items():
            self.assertEqual(md[key], value)
        
        # Order is preserved (dict insertion order is preserved in Python 3.7+)
        self.assertEqual(set(md.items()), set(d.items()))
    
    def test_creation_with_kwargs(self):
        """Test creating MultiDict with keyword arguments.""" 
        md = MultiDict(a=1, b=2, c=3)
        
        self.assertEqual(len(md), 3)
        self.assertEqual(md['a'], 1)
        self.assertEqual(md['b'], 2)
        self.assertEqual(md['c'], 3)
    
    def test_creation_mixed(self):
        """Test creating MultiDict with both iterable and kwargs."""
        pairs = [('a', 1), ('b', 2)]
        md = MultiDict(pairs, c=3, d=4)
        
        self.assertEqual(len(md), 4)
        self.assertEqual(md['a'], 1)
        self.assertEqual(md['b'], 2)
        self.assertEqual(md['c'], 3)
        self.assertEqual(md['d'], 4)
    
    def test_getitem(self):
        """Test __getitem__ behavior."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        
        self.assertEqual(md['a'], 1)  # First value
        self.assertEqual(md['b'], 2)
        
        with self.assertRaises(KeyError):
            _ = md['missing']
    
    def test_setitem_new_key(self):
        """Test __setitem__ with new key."""
        md = MultiDict()
        md['new'] = 'value'
        
        self.assertEqual(len(md), 1)
        self.assertEqual(md['new'], 'value')
        self.assertEqual(list(md.items()), [('new', 'value')])
    
    def test_setitem_existing_key(self):
        """Test __setitem__ with existing key."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        md['a'] = 99
        
        # Should replace and remove all duplicates
        self.assertEqual(len(md), 2)
        self.assertEqual(md['a'], 99)
        self.assertEqual(list(md.items()), [('a', 99), ('b', 2)])
    
    def test_add_method(self):
        """Test add() method."""
        md = MultiDict()
        md.add('key', 'value1')
        md.add('key', 'value2')
        md.add('other', 'value3')
        
        self.assertEqual(len(md), 3)
        self.assertEqual(md['key'], 'value1')  # First value
        self.assertEqual(md['other'], 'value3')
        self.assertEqual(list(md.items()), [('key', 'value1'), ('key', 'value2'), ('other', 'value3')])
    
    def test_delitem(self):
        """Test __delitem__ behavior."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3), ('c', 4)])
        del md['a']  # Should remove all 'a' items
        
        self.assertEqual(len(md), 2)
        self.assertEqual(list(md.items()), [('b', 2), ('c', 4)])
        
        with self.assertRaises(KeyError):
            del md['missing']
    
    def test_iteration(self):
        """Test iteration over keys."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        keys = list(md)
        
        self.assertEqual(keys, ['a', 'b', 'a'])
        
        # Test that iteration yields duplicate keys
        key_count = {}
        for key in md:
            key_count[key] = key_count.get(key, 0) + 1
        
        self.assertEqual(key_count, {'a': 2, 'b': 1})
    
    def test_values_view(self):
        """Test values() view."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        values = md.values()
        
        self.assertEqual(len(values), 3)
        self.assertEqual(list(values), [1, 2, 3])
    
    def test_items_view(self):
        """Test items() view."""
        md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        items = md.items()
        
        self.assertEqual(len(items), 3)
        self.assertEqual(list(items), [('a', 1), ('b', 2), ('a', 3)])
    
    def test_len(self):
        """Test len() behavior."""
        md = MultiDict()
        self.assertEqual(len(md), 0)
        
        md.add('a', 1)
        self.assertEqual(len(md), 1)
        
        md.add('a', 2)  # Duplicate key
        self.assertEqual(len(md), 2)
        
        md['b'] = 3
        self.assertEqual(len(md), 3)
        
        del md['a']  # Removes both 'a' items
        self.assertEqual(len(md), 1)


class TestMultiDictEdgeCases(unittest.TestCase):
    """Test edge cases and various data scenarios."""
    
    def test_various_data_scenarios(self):
        """Test basic operations with various data sets."""
        test_cases = [
            [],
            [('a', 1)],
            [('a', 1), ('b', 2)],
            [('a', 1), ('b', 2), ('a', 3)],
            [('x', 'hello'), ('y', 'world'), ('x', 'foo'), ('z', 'bar')]
        ]
        
        for data in test_cases:
            with self.subTest(data=data):
                md = MultiDict(data)
                
                # Test basic properties
                self.assertEqual(len(md), len(data))
                self.assertEqual(list(md.items()), data)
                
                # Test that we can get all keys
                for key, expected_value in data:
                    if data and md[key] != expected_value:
                        # Should be the first occurrence
                        first_value = next(value for k, value in data if k == key)
                        self.assertEqual(md[key], first_value)
                        break
    
    def test_setitem_scenarios(self):
        """Test __setitem__ in various scenarios."""
        test_cases = [
            ([], 'new', 'value'),
            ([('a', 1)], 'b', 2),
            ([('a', 1), ('b', 2)], 'a', 99),  # Replace existing
            ([('a', 1), ('b', 2), ('a', 3)], 'a', 88),  # Replace with duplicates
        ]
        
        for initial_data, key, value in test_cases:
            with self.subTest(initial_data=initial_data, key=key, value=value):
                md = MultiDict(initial_data)
                md[key] = value
                
                self.assertEqual(md[key], value)
                
                # If key existed before, there should be exactly one occurrence now
                key_count = sum(1 for k, v in md.items() if k == key)
                self.assertEqual(key_count, 1)


class TestMultiDictInterface(unittest.TestCase):
    """Test interface compatibility."""
    
    def test_multidict_interface(self):
        """Test that our MultiDict has expected interface."""
        md = MultiDict()
        
        # Check that basic methods exist and are callable
        self.assertTrue(hasattr(md, 'add'))
        self.assertTrue(callable(md.add))
        self.assertTrue(hasattr(md, 'items'))
        self.assertTrue(callable(md.items))
        self.assertTrue(hasattr(md, 'values'))
        self.assertTrue(callable(md.values))
        
        # Check magic methods
        self.assertTrue(hasattr(md, '__getitem__'))
        self.assertTrue(hasattr(md, '__setitem__'))
        self.assertTrue(hasattr(md, '__delitem__'))
        self.assertTrue(hasattr(md, '__iter__'))
        self.assertTrue(hasattr(md, '__len__'))


if __name__ == '__main__':
    unittest.main()