"""Test the withdefault decorator and helper functions."""

from multicollections.abc import withdefault, _with_default_handling, _NO_DEFAULT
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def test_with_default_handling_helper():
    """Test the _with_default_handling helper function."""
    
    def operation_success():
        return "success"
    
    def operation_keyerror():
        raise KeyError("test key")
    
    # Test successful operation
    result = _with_default_handling(operation_success, _NO_DEFAULT)
    assert result == "success"
    
    # Test operation with default when KeyError raised
    result = _with_default_handling(operation_keyerror, "default_value")
    assert result == "default_value"
    
    # Test operation without default when KeyError raised (should re-raise)
    try:
        _with_default_handling(operation_keyerror, _NO_DEFAULT)
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert str(e) == "'test key'"


def test_withdefault_decorator():
    """Test the withdefault decorator."""
    
    class TestClass:
        def __init__(self):
            self.data = {"key1": "value1", "key2": "value2"}
        
        @withdefault
        def get_value(self, key: K) -> V:
            """Get a value by key, may raise KeyError."""
            if key not in self.data:
                raise KeyError(key)
            return self.data[key]
    
    obj = TestClass()
    
    # Test successful retrieval
    assert obj.get_value("key1") == "value1"
    
    # Test with default value
    assert obj.get_value("missing", "default") == "default"
    
    # Test missing key without default (should raise KeyError)
    try:
        obj.get_value("missing")
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert str(e) == "'missing'"


def test_withdefault_preserves_metadata():
    """Test that the decorator preserves method metadata."""
    
    @withdefault  
    def sample_method(self, key: K) -> V:
        """Sample docstring."""
        raise KeyError(key)
    
    assert sample_method.__name__ == "sample_method"
    assert sample_method.__doc__ == "Sample docstring."
    assert "default" in sample_method.__annotations__


def test_simplified_methods_work():
    """Test that the simplified methods using the helper still work correctly."""
    from multicollections import MultiDict
    
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    
    # Test getone with simplified implementation
    assert md.getone("a") == 1
    assert md.getone("missing", "default") == "default"
    
    # Test popone with simplified implementation
    assert md.popone("b") == 2
    assert md.popone("missing", "default") == "default"
    
    # Test popall with simplified implementation  
    result = md.popall("a")
    assert result == [1, 3]
    assert md.popall("missing", []) == []
    
    # Test error cases still work
    md2 = MultiDict([("x", 10)])
    try:
        md2.getone("missing")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass  # Expected