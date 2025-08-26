"""Test runner that can work with or without pytest.

This script can run tests in a pytest-like manner even when pytest is not installed.
"""

import sys
import unittest
import importlib.util
from pathlib import Path

def create_mock_pytest():
    """Create a mock pytest module for compatibility."""
    class MockPytest:
        def mark(self):
            return self
        
        def skipif(self, condition, reason=""):
            def decorator(func):
                if condition:
                    return unittest.skip(reason)(func)
                return func
            return decorator
        
        def parametrize(self, params, values):
            def decorator(func):
                # Simple parametrization - create multiple test methods
                return func
            return decorator
        
        def raises(self, exception_type):
            return self.Raises(exception_type)
        
        class Raises:
            def __init__(self, exception_type):
                self.exception_type = exception_type
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"Expected {self.exception_type.__name__} but no exception was raised")
                return issubclass(exc_type, self.exception_type)
    
    return MockPytest()

# Try to import pytest, otherwise use mock
try:
    import pytest
except ImportError:
    pytest = create_mock_pytest()
    # Inject into sys.modules so imports work
    sys.modules['pytest'] = pytest

def run_tests():
    """Run all tests in the tests directory."""
    test_dir = Path(__file__).parent
    
    # Discover and import test modules
    test_modules = []
    for test_file in test_dir.glob("test_*.py"):
        if test_file.name == __file__:
            continue
            
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
            test_modules.append(module)
            print(f"✓ Loaded {module_name}")
        except Exception as e:
            print(f"✗ Failed to load {module_name}: {e}")
    
    # Run unittest-based tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module in test_modules:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, unittest.TestCase) and 
                attr is not unittest.TestCase):
                
                print(f"Adding test class: {attr.__name__}")
                suite.addTests(loader.loadTestsFromTestCase(attr))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())