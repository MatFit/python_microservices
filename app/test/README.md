# Testing

This directory contains all test files for the microservices application.

## Running Tests

### From the test directory:
```bash
cd python_microservices/app/test

# Run all tests
python3 run_tests.py

# Run individual test files
python3 test_alpaca_service.py
python3 test_alpaca_simple.py
```

### From the app directory:
```bash
cd python_microservices/app

# Run all tests
python3 -m unittest discover test

# Run specific test file
python3 -m unittest test.test_alpaca_service
```

### From the parent directory:
```bash
cd python_microservices

# Run all tests
python3 -m app.test.run_tests

# Run specific test
python3 -m app.test.test_alpaca_service
```

## Test Files

- `test_alpaca_service.py` - Unit tests for AlpacaService
- `test_alpaca_simple.py` - Simple integration test for AlpacaService
- `test_simple_uvicorn.py` - Basic FastAPI endpoint tests
- `run_tests.py` - Test runner script

## Import Strategy

The tests use a flexible import strategy that works in all scenarios:
1. Try to import using `app.services.xxx` (for Docker/parent directory)
2. Fall back to `services.xxx` (for direct app directory usage)
3. Use sys.path manipulation when running from test directory
