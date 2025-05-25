"""
Test fixtures for database operations
"""
import os
import sqlite3
import pytest
import tempfile
from app.database.db_manager import DatabaseManager

@pytest.fixture
def test_db_path():
    """Create a temporary database file for testing"""
    # Create a temporary file
    db_fd, db_path = tempfile.mkstemp()
    yield db_path
    
    # Clean up after test
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def test_db_manager(test_db_path):
    """Create a DatabaseManager instance with test database"""
    db_manager = DatabaseManager(db_path=test_db_path)
    return db_manager

@pytest.fixture
def test_db_with_data(test_db_manager):
    """Populate the test database with sample data"""
    # Add sample CPU data
    test_db_manager.insert_cpu_data("2025-05-25T10:00:00", 25.5)
    test_db_manager.insert_cpu_data("2025-05-25T10:01:00", 30.2)
    test_db_manager.insert_cpu_data("2025-05-25T10:02:00", 22.8)
    
    # Add sample memory data
    memory_data1 = {
        "percent": 45.7,
        "total_gb": 16.0,
        "used_gb": 7.3,
        "available_gb": 8.7
    }
    memory_data2 = {
        "percent": 50.2,
        "total_gb": 16.0,
        "used_gb": 8.0,
        "available_gb": 8.0
    }
    test_db_manager.insert_memory_data("2025-05-25T10:00:00", memory_data1)
    test_db_manager.insert_memory_data("2025-05-25T10:01:00", memory_data2)
    
    # Add sample alerts
    test_db_manager.insert_alert("2025-05-25T10:00:00", "CPU", "High CPU usage detected", 85.2)
    test_db_manager.insert_alert("2025-05-25T10:05:00", "Memory", "High memory usage detected", 90.1)
    
    return test_db_manager
