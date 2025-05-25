"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from tests.fixtures.api_fixtures import mocked_system_monitor, mocked_db_manager, test_client


class TestApiEndpoints:
    """Test suite for the API endpoints"""
    
    def test_read_root(self, test_client, mocked_system_monitor):
        """Test the root endpoint returns the dashboard HTML"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Verify that system monitor was called
        mocked_system_monitor.get_cpu_usage.assert_called_once()
        mocked_system_monitor.get_memory_usage.assert_called_once()
    
    def test_get_system_info_api(self, test_client, mocked_system_monitor):
        """Test the system info API endpoint"""
        response = test_client.get("/api/system-info")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify that the expected data is returned
        assert "cpu_percent" in json_response
        assert "memory_info" in json_response
        assert "disk_info" in json_response
        assert "per_core_cpu" in json_response
        assert "network_stats" in json_response
        
        # Verify values match our mock
        assert json_response["cpu_percent"] == 25.5
        assert json_response["memory_info"]["percent"] == 50.0
        assert json_response["per_core_cpu"] == [25.0, 26.0, 24.0, 26.0]
        
        # Verify that system monitor was called
        mocked_system_monitor.get_system_info.assert_called_once()
    
    def test_get_processes(self, test_client, mocked_system_monitor):
        """Test the processes API endpoint"""
        response = test_client.get("/api/processes")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify that we get a list with the expected process
        assert isinstance(json_response, list)
        assert len(json_response) == 1
        assert json_response[0]["name"] == "test_process"
        assert json_response[0]["cpu_percent"] == 10.5
        
        # Verify that system monitor was called
        mocked_system_monitor.get_top_processes.assert_called_once()
    
    def test_get_cpu_history(self, test_client, mocked_db_manager):
        """Test the CPU history API endpoint"""
        response = test_client.get("/api/history/cpu")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify that the expected data is returned
        assert "timestamps" in json_response
        assert "values" in json_response
        assert len(json_response["timestamps"]) == 3
        assert len(json_response["values"]) == 3
        
        # Verify that db_manager was called with default hour parameter
        mocked_db_manager.get_cpu_history.assert_called_once_with(1)
    
    def test_get_cpu_history_with_hours(self, test_client, mocked_db_manager):
        """Test the CPU history API endpoint with custom hours parameter"""
        response = test_client.get("/api/history/cpu?hours=12")
        
        assert response.status_code == 200
        
        # Verify that db_manager was called with custom hour parameter
        mocked_db_manager.get_cpu_history.assert_called_once_with(12)
    
    def test_get_memory_history(self, test_client, mocked_db_manager):
        """Test the memory history API endpoint"""
        response = test_client.get("/api/history/memory")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify that the expected data is returned
        assert "timestamps" in json_response
        assert "values" in json_response
        assert len(json_response["timestamps"]) == 2
        assert len(json_response["values"]) == 2
        
        # Verify that db_manager was called with default hour parameter
        mocked_db_manager.get_memory_history.assert_called_once_with(1)
    
    def test_get_memory_history_with_hours(self, test_client, mocked_db_manager):
        """Test the memory history API endpoint with custom hours parameter"""
        response = test_client.get("/api/history/memory?hours=24")
        
        assert response.status_code == 200
        
        # Verify that db_manager was called with custom hour parameter
        mocked_db_manager.get_memory_history.assert_called_once_with(24)
    
    def test_get_alerts(self, test_client, mocked_db_manager):
        """Test the alerts API endpoint"""
        response = test_client.get("/api/alerts")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify that we get the expected alerts
        assert isinstance(json_response, list)
        assert len(json_response) == 2
        assert json_response[0]["alert_type"] == "CPU"
        assert json_response[1]["alert_type"] == "Memory"
        
        # Verify that db_manager was called with default limit
        mocked_db_manager.get_alerts.assert_called_once_with(10)
    
    def test_get_alerts_with_limit(self, test_client, mocked_db_manager):
        """Test the alerts API endpoint with custom limit parameter"""
        response = test_client.get("/api/alerts?limit=5")
        
        assert response.status_code == 200
        
        # Verify that db_manager was called with custom limit
        mocked_db_manager.get_alerts.assert_called_once_with(5)
