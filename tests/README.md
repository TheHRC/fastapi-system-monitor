# System Performance Monitor Tests

This directory contains tests for the System Performance Monitor application.

## Test Structure

```
tests/
├── conftest.py              # Global pytest configuration and fixtures
├── fixtures/                # Test fixtures and mocks
│   ├── __init__.py
│   ├── api_fixtures.py      # Fixtures for API tests
│   └── db_fixtures.py       # Fixtures for database tests
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_api_endpoints.py # API endpoint tests
└── unit/                    # Unit tests
    ├── __init__.py
    ├── test_db_manager.py   # Database manager tests
    ├── test_metrics_recorder.py # Metrics recorder tests
    └── test_system_monitor.py   # System monitor tests
```

## Running Tests

You can run the tests using:

```bash
# From the root directory
python run_tests.py

# Or directly with pytest
pytest
```

## Test Types

The tests are organized by type:

1. **Unit Tests**: Tests individual components in isolation
2. **Integration Tests**: Tests interactions between components

You can run specific test types:

```bash
# Run only unit tests
python run_tests.py --type unit

# Run only integration tests
python run_tests.py --type integration
```

## Test Categories

Tests are also categorized by the component they test:

1. **API Tests**: Test API endpoints
2. **DB Tests**: Test database operations
3. **Monitor Tests**: Test system monitoring
4. **Metrics Tests**: Test metrics recording

You can run tests for specific components:

```bash
# Run only API tests
python run_tests.py --type api

# Run only database tests
python run_tests.py --type db
```

## Coverage Reporting

To generate a test coverage report:

```bash
python run_tests.py --coverage
```

For more detailed information, see the [Testing Documentation](../docs/testing.md).
