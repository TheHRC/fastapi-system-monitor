"""
Global pytest configuration and fixtures
"""
import pytest
import os
from pytest import Config
from typing import List

# Make sure the tests can import from the app package
# This is needed if the tests are run from the tests directory

# Import fixtures from fixture modules so they're available to all tests
from tests.fixtures.db_fixtures import test_db_path, test_db_manager, test_db_with_data
from tests.fixtures.api_fixtures import (
    mocked_system_monitor, mocked_db_manager, test_client
)


def pytest_collection_modifyitems(config: Config, items: List[pytest.Item]):
    """
    Customize test collection:
    - Add markers for different test types
    - Modify test names for better reporting
    """
    for item in items:
        # Add markers based on path
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add specific markers based on test name
        if "api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "db" in item.nodeid:
            item.add_marker(pytest.mark.db)
        elif "monitor" in item.nodeid:
            item.add_marker(pytest.mark.monitor)
        elif "metrics" in item.nodeid:
            item.add_marker(pytest.mark.metrics)
