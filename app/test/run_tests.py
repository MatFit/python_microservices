import unittest
import sys
import os

# Add the parent directory (app) to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_tests():
    """Discover and run all tests in the current directory"""
    # Discover tests in the current directory
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

    

if __name__ == '__main__':
    print("Running tests from test directory...")
    success = run_tests()
    
    if success:
        print("All tests passed")
        sys.exit(0)
    else:
        print("Some tests failed")
        sys.exit(1)
