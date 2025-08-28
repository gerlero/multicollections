#!/usr/bin/env python3
"""Test script for MultiDict.__eq__ implementation."""

from multicollections import MultiDict

def test_current_behavior():
    """Test current behavior without __eq__ implemented."""
    md1 = MultiDict([('a', 1), ('b', 2), ('a', 3)])
    md2 = MultiDict([('a', 1), ('b', 2), ('a', 3)])
    md3 = MultiDict([('a', 1), ('b', 2)])
    md4 = MultiDict([('a', 3), ('b', 2), ('a', 1)])
    
    print("Testing current behavior:")
    print(f"md1 == md2: {md1 == md2}")  # Should be False (object identity)
    print(f"md1 == md3: {md1 == md3}")  # Should be False
    print(f"md1 == md4: {md1 == md4}")  # Should be False
    print(f"md1 is md1: {md1 is md1}")  # Should be True
    
    # Test with different types
    print(f"md1 == dict: {md1 == {'a': 1, 'b': 2}}")  # Should be False
    print(f"md1 == list: {md1 == [('a', 1), ('b', 2), ('a', 3)]}")  # Should be False
    
    # Test with empty
    empty1 = MultiDict()
    empty2 = MultiDict()
    print(f"empty1 == empty2: {empty1 == empty2}")  # Should be False (object identity)
    
    print(f"md1 items: {list(md1.items())}")
    print(f"md2 items: {list(md2.items())}")
    print(f"md4 items: {list(md4.items())}")

if __name__ == "__main__":
    test_current_behavior()