"""
Unit tests for DatabaseManager class
"""
import pytest
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from app.database.db_manager import DatabaseManager
from tests.fixtures.db_fixtures import test_db_path, test_db_manager, test_db_with_data


class TestDatabaseManager:
    """Test suite for the DatabaseManager class"""
    
    def test_init_creates_db_file(self, test_db_path):
        """Test that initializing DatabaseManager creates the database file"""
        db_manager = DatabaseManager(db_path=test_db_path)
        
        # Check that we can connect to the database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        conn.close()
        
        assert 'cpu_history' in table_names
        assert 'memory_history' in table_names
        assert 'system_alerts' in table_names
    
    def test_get_connection(self, test_db_manager):
        """Test that get_connection returns valid connection and cursor"""
        conn, cursor = test_db_manager.get_connection()
        
        assert isinstance(conn, sqlite3.Connection)
        assert isinstance(cursor, sqlite3.Cursor)
        
        # Clean up
        conn.close()
    
    def test_insert_cpu_data(self, test_db_manager):
        """Test that CPU data is inserted correctly"""
        timestamp = "2025-05-25T12:00:00"
        usage_percent = 42.5
        
        test_db_manager.insert_cpu_data(timestamp, usage_percent)
        
        # Verify data was inserted
        conn, cursor = test_db_manager.get_connection()
        cursor.execute("SELECT * FROM cpu_history WHERE timestamp = ?", (timestamp,))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == timestamp
        assert result[1] == usage_percent
    
    def test_insert_memory_data(self, test_db_manager):
        """Test that memory data is inserted correctly"""
        timestamp = "2025-05-25T12:00:00"
        memory_data = {
            "percent": 65.7,
            "total_gb": 16.0,
            "used_gb": 10.5,
            "available_gb": 5.5
        }
        
        test_db_manager.insert_memory_data(timestamp, memory_data)
        
        # Verify data was inserted
        conn, cursor = test_db_manager.get_connection()
        cursor.execute("SELECT * FROM memory_history WHERE timestamp = ?", (timestamp,))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == timestamp
        assert result[1] == 65.7
        assert result[2] == 16.0
        assert result[3] == 10.5
        assert result[4] == 5.5
    
    def test_insert_alert(self, test_db_manager):
        """Test that an alert is inserted correctly"""
        timestamp = "2025-05-25T12:00:00"
        alert_type = "CPU"
        message = "Test CPU alert"
        value = 95.2
        
        test_db_manager.insert_alert(timestamp, alert_type, message, value)
        
        # Verify alert was inserted
        conn, cursor = test_db_manager.get_connection()
        cursor.execute(
            "SELECT timestamp, alert_type, message, value FROM system_alerts WHERE timestamp = ?",
            (timestamp,)
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == timestamp
        assert result[1] == alert_type
        assert result[2] == message
        assert result[3] == value
    
    def test_get_cpu_history(self, test_db_with_data):
        """Test retrieving CPU history"""
        # Use a fixture with pre-populated data
        result = test_db_with_data.get_cpu_history(hours=24)
        
        assert "timestamps" in result
        assert "values" in result
        assert len(result["timestamps"]) == 3
        assert len(result["values"]) == 3
        assert 25.5 in result["values"]
        assert 30.2 in result["values"]
        assert 22.8 in result["values"]
    
    def test_get_memory_history(self, test_db_with_data):
        """Test retrieving memory history"""
        # Use a fixture with pre-populated data
        result = test_db_with_data.get_memory_history(hours=24)
        
        assert "timestamps" in result
        assert "values" in result
        assert len(result["timestamps"]) == 2
        assert len(result["values"]) == 2
        assert 45.7 in result["values"]
        assert 50.2 in result["values"]
    
    def test_get_alerts(self, test_db_with_data):
        """Test retrieving system alerts"""
        # Use a fixture with pre-populated data
        result = test_db_with_data.get_alerts(limit=10)
        
        assert len(result) == 2
        
        # Check first alert
        assert result[0]["timestamp"] == "2025-05-25T10:05:00"  # Most recent first
        assert result[0]["alert_type"] == "Memory"
        assert result[0]["message"] == "High memory usage detected"
        assert result[0]["value"] == 90.1
        
        # Check second alert
        assert result[1]["timestamp"] == "2025-05-25T10:00:00"
        assert result[1]["alert_type"] == "CPU"
        assert result[1]["message"] == "High CPU usage detected"
        assert result[1]["value"] == 85.2
    
    def test_get_alerts_with_limit(self, test_db_with_data):
        """Test retrieving system alerts with a limit"""
        # Use a fixture with pre-populated data but limit to 1 result
        result = test_db_with_data.get_alerts(limit=1)
        
        assert len(result) == 1
        assert result[0]["timestamp"] == "2025-05-25T10:05:00"  # Most recent first
    
    def test_get_cpu_history_with_hours(self, test_db_with_data):
        """Test retrieving CPU history with a specific hour range"""
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be after our test data
            mock_datetime.now.return_value = datetime.fromisoformat("2025-05-25T11:00:00")
            mock_datetime.isoformat.return_value = "2025-05-25T10:00:00"
            
            # Should only include data from last hour
            result = test_db_with_data.get_cpu_history(hours=1)
            
            # All our test data is within the hour range
            assert len(result["timestamps"]) == 3
    
    def test_get_cpu_history_empty(self, test_db_manager):
        """Test retrieving CPU history when there's no data"""
        # Use an empty database
        result = test_db_manager.get_cpu_history()
        
        assert result["timestamps"] == []
        assert result["values"] == []
    
    def test_get_cpu_history_error(self, test_db_manager):
        """Test error handling in get_cpu_history"""
        with patch.object(test_db_manager, 'get_connection', side_effect=Exception("Test exception")):
            result = test_db_manager.get_cpu_history()
            
            assert result["timestamps"] == []
            assert result["values"] == []
    
    def test_get_memory_history_error(self, test_db_manager):
        """Test error handling in get_memory_history"""
        with patch.object(test_db_manager, 'get_connection', side_effect=Exception("Test exception")):
            result = test_db_manager.get_memory_history()
            
            assert result["timestamps"] == []
            assert result["values"] == []
    
    def test_get_alerts_error(self, test_db_manager):
        """Test error handling in get_alerts"""
        with patch.object(test_db_manager, 'get_connection', side_effect=Exception("Test exception")):
            result = test_db_manager.get_alerts()
            
            assert result == []
