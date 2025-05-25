# Testing Documentation

This document provides information on testing the System Performance Monitor application.

## Testing Philosophy

The tests for this application follow these principles:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test how components interact with each other
3. **Mocking**: External dependencies like `psutil` are mocked to ensure reliable tests
4. **Test Coverage**: Aim for high test coverage of core functionality

## Test Components

### Unit Tests

- **SystemMonitor Tests**: Test the system monitoring functionality
  - Ensure CPU metrics are collected correctly
  - Ensure memory metrics are collected correctly
  - Ensure disk usage metrics are collected correctly
  - Ensure network statistics are collected correctly
  - Ensure process information is collected correctly
  - Test error handling for all metrics collection

- **DatabaseManager Tests**: Test the database operations
  - Test database initialization and schema creation
  - Test data insertion operations
  - Test data retrieval operations
  - Test query parameters (time ranges, limits)
  - Test error handling

- **MetricsRecorder Tests**: Test the background metrics recording
  - Test starting and stopping recording
  - Test threshold-based alerts
  - Test error handling during recording

### Integration Tests

- **API Endpoint Tests**: Test the API endpoints
  - Test that endpoints return expected data
  - Test query parameters
  - Test response formats
  - Test dependency injection

## Running Tests

Use the `run_tests.py` script to run tests with various options:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run with coverage reporting
python run_tests.py --coverage
```

## Writing New Tests

When adding new functionality, follow these guidelines for writing tests:

1. **Unit Tests First**: Write unit tests for all new components
2. **Mock Dependencies**: Use mocks for external dependencies
3. **Test Edge Cases**: Include tests for error conditions and edge cases
4. **Test Parameters**: Test all parameter combinations for functions
5. **Integration Testing**: Add integration tests for new API endpoints

## Test Fixtures

Reusable fixtures are located in the `tests/fixtures` directory:

- `db_fixtures.py`: Database fixtures
- `api_fixtures.py`: API fixtures

## Continuous Integration

Tests should be run before each commit to ensure code quality. They are also run automatically in the CI pipeline.
