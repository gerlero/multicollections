"""Basic tests for multicollections.MultiDict behavior.

This test module compares the behavior of multicollections.MultiDict 
with multidict.MultiDict for implemented functionality.
"""

import sys
import unittest
from typing import Any, Dict, List, Tuple

# Try to import the necessary modules
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    import multidict
    MULTIDICT_AVAILABLE = True
except ImportError:
    MULTIDICT_AVAILABLE = False

# Import our implementation
try:
    from multicollections import MultiDict as OurMultiDict
except ImportError:
    import sys
    import os
    # Add the parent directory to path if needed
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from multicollections import MultiDict as OurMultiDict


def run_basic_tests():
    """Run basic tests that don't require external dependencies."""
    print("Running basic functionality tests...")
    
    # Test basic creation and operations
    md = OurMultiDict()
    assert len(md) == 0
    
    # Test adding items
    md['key1'] = 'value1'
    assert len(md) == 1
    assert md['key1'] == 'value1'
    
    # Test add method
    md.add('key1', 'value2')
    assert len(md) == 2
    assert md['key1'] == 'value1'  # Should return first value
    
    # Test initialization with pairs
    md2 = OurMultiDict([('a', 1), ('b', 2), ('a', 3)])
    assert len(md2) == 3
    assert md2['a'] == 1  # First value
    assert md2['b'] == 2
    
    # Test initialization with dict
    md3 = OurMultiDict({'x': 10, 'y': 20})
    assert len(md3) == 2
    assert md3['x'] == 10
    assert md3['y'] == 20
    
    # Test initialization with kwargs
    md4 = OurMultiDict(z=30, w=40)
    assert len(md4) == 2
    assert md4['z'] == 30
    assert md4['w'] == 40
    
    # Test iteration
    md5 = OurMultiDict([('a', 1), ('b', 2), ('a', 3)])
    keys = list(md5)
    assert keys == ['a', 'b', 'a']
    
    # Test values view
    values = list(md5.values())
    assert values == [1, 2, 3]
    
    # Test items view  
    items = list(md5.items())
    assert items == [('a', 1), ('b', 2), ('a', 3)]
    
    # Test deletion
    md6 = OurMultiDict([('a', 1), ('b', 2), ('a', 3)])
    del md6['a']  # Should remove all 'a' items
    assert len(md6) == 1
    assert list(md6.items()) == [('b', 2)]
    
    # Test KeyError on missing key
    try:
        _ = md6['missing']
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    
    # Test KeyError on deleting missing key
    try:
        del md6['missing']
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    
    # Test setitem replaces all values
    md7 = OurMultiDict([('a', 1), ('b', 2), ('a', 3)])
    md7['a'] = 99
    assert len(md7) == 2
    assert list(md7.items()) == [('a', 99), ('b', 2)]
    
    print("✓ All basic functionality tests passed!")


class TestMultiDictCompatibility(unittest.TestCase):
    """Test compatibility between our MultiDict and multidict.MultiDict."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [
            ('key1', 'value1'),
            ('key2', 'value2'), 
            ('key1', 'value3'),
            ('key3', 'value4')
        ]
        self.test_dict = {'a': 1, 'b': 2, 'c': 3}
        self.test_kwargs = {'x': 10, 'y': 20}
    
    def test_basic_construction_empty(self):
        """Test creating empty MultiDict instances."""
        our_md = OurMultiDict()
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict()
            self.assertEqual(len(our_md), len(their_md))
            self.assertEqual(list(our_md), list(their_md))
    
    def test_construction_from_pairs(self):
        """Test creating MultiDict from pairs."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            self.assertEqual(len(our_md), len(their_md))
            self.assertEqual(list(our_md.items()), list(their_md.items()))
            self.assertEqual(list(our_md), list(their_md))
            
            # Test that first value is returned for duplicate keys
            self.assertEqual(our_md['key1'], their_md['key1'])
    
    def test_construction_from_dict(self):
        """Test creating MultiDict from regular dict."""
        our_md = OurMultiDict(self.test_dict)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_dict)
            self.assertEqual(len(our_md), len(their_md))
            self.assertEqual(set(our_md.items()), set(their_md.items()))
            
            # Check all key-value pairs match
            for key in self.test_dict:
                self.assertEqual(our_md[key], their_md[key])
    
    def test_construction_with_kwargs(self):
        """Test creating MultiDict with keyword arguments.""" 
        our_md = OurMultiDict(**self.test_kwargs)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(**self.test_kwargs)
            self.assertEqual(len(our_md), len(their_md))
            
            for key in self.test_kwargs:
                self.assertEqual(our_md[key], their_md[key])
    
    def test_getitem_behavior(self):
        """Test __getitem__ behavior."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            
            # Test getting existing keys
            self.assertEqual(our_md['key1'], their_md['key1'])
            self.assertEqual(our_md['key2'], their_md['key2'])
            self.assertEqual(our_md['key3'], their_md['key3'])
            
            # Test KeyError for missing keys
            with self.assertRaises(KeyError):
                _ = our_md['missing']
            with self.assertRaises(KeyError):
                _ = their_md['missing']
    
    def test_setitem_behavior(self):
        """Test __setitem__ behavior."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            
            # Test setting new key
            our_md['new_key'] = 'new_value'
            their_md['new_key'] = 'new_value' 
            self.assertEqual(our_md['new_key'], their_md['new_key'])
            
            # Test replacing existing key (should remove all duplicates)
            our_md['key1'] = 'replaced'
            their_md['key1'] = 'replaced'
            self.assertEqual(our_md['key1'], their_md['key1'])
            
            # Check that all duplicate values are gone
            our_items = list(our_md.items())
            their_items = list(their_md.items())
            
            our_key1_count = sum(1 for k, v in our_items if k == 'key1')
            their_key1_count = sum(1 for k, v in their_items if k == 'key1')
            
            self.assertEqual(our_key1_count, their_key1_count)
            self.assertEqual(our_key1_count, 1)
    
    def test_add_behavior(self):
        """Test add() method behavior."""
        our_md = OurMultiDict()
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict()
            
            # Add some values
            our_md.add('key1', 'value1')
            our_md.add('key1', 'value2')
            our_md.add('key2', 'value3')
            
            their_md.add('key1', 'value1')
            their_md.add('key1', 'value2')  
            their_md.add('key2', 'value3')
            
            self.assertEqual(list(our_md.items()), list(their_md.items()))
            self.assertEqual(our_md['key1'], their_md['key1'])  # First value
    
    def test_delitem_behavior(self):
        """Test __delitem__ behavior."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            
            # Delete a key that appears multiple times
            del our_md['key1']
            del their_md['key1']
            
            self.assertEqual(list(our_md.items()), list(their_md.items()))
            
            # Test KeyError for missing key
            with self.assertRaises(KeyError):
                del our_md['missing']
            with self.assertRaises(KeyError):
                del their_md['missing']
    
    def test_iteration_behavior(self):
        """Test iteration behavior."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            
            # Test key iteration
            self.assertEqual(list(our_md), list(their_md))
            
            # Test items iteration
            self.assertEqual(list(our_md.items()), list(their_md.items()))
            
            # Test values iteration
            self.assertEqual(list(our_md.values()), list(their_md.values()))
    
    def test_len_behavior(self):
        """Test len() behavior."""
        our_md = OurMultiDict(self.test_data)
        
        if MULTIDICT_AVAILABLE:
            their_md = multidict.MultiDict(self.test_data)
            self.assertEqual(len(our_md), len(their_md))
        
        # Test with empty
        our_empty = OurMultiDict()
        if MULTIDICT_AVAILABLE:
            their_empty = multidict.MultiDict()
            self.assertEqual(len(our_empty), len(their_empty))


def main():
    """Main test runner."""
    print("=" * 60)
    print("Testing multicollections.MultiDict")
    print("=" * 60)
    
    if not MULTIDICT_AVAILABLE:
        print("WARNING: multidict not available, running limited tests only")
    else:
        print("✓ multidict available, running full compatibility tests")
    
    if not PYTEST_AVAILABLE:
        print("WARNING: pytest not available, using unittest only")
    else:
        print("✓ pytest available")
    
    print()
    
    # Run basic tests first
    try:
        run_basic_tests()
    except Exception as e:
        print(f"✗ Basic tests failed: {e}")
        return 1
    
    print()
    
    # Run unittest tests
    print("Running unittest compatibility tests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMultiDictCompatibility)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())