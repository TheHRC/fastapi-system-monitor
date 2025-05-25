"""
Test fixtures for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch

from app.main import app
from app.core.system_monitor import SystemMonitor
from app.database.db_manager import DatabaseManager


@pytest.fixture
def mocked_system_monitor():
    """Create a mocked SystemMonitor for testing API endpoints"""
    monitor = Mock(spec=SystemMonitor)
    
    # Mock CPU usage
    monitor.get_cpu_usage.return_value = 25.5
    
    # Mock memory usage
    monitor.get_memory_usage.return_value = {
        "total_gb": 16.0,
        "available_gb": 8.0,
        "used_gb": 8.0,
        "percent": 50.0,
    }
    
    # Mock disk usage
    monitor.get_disk_usage.return_value = [
        {
            "device": "C:\\",
            "mountpoint": "C:\\",
            "total_gb": 500.0,
            "used_gb": 250.0,
            "free_gb": 250.0,
            "percent": 50.0
        }
    ]
    
    # Mock per-core CPU
    monitor.get_per_core_cpu.return_value = [25.0, 26.0, 24.0, 26.0]
    
    # Mock network stats
    monitor.get_network_stats.return_value = {
        "bytes_sent": 100.5,
        "bytes_recv": 200.3,
        "packets_sent": 1000,
        "packets_recv": 2000
    }
    
    # Mock top processes
    monitor.get_top_processes.return_value = [
        {
            "pid": 1234,
            "name": "test_process",
            "username": "test_user",
            "cpu_percent": 10.5,
            "memory_percent": 5.2
        }
    ]
    
    # Mock system info
    monitor.get_system_info.return_value = {
        "cpu_percent": 25.5,
        "memory_info": monitor.get_memory_usage.return_value,
        "disk_info": monitor.get_disk_usage.return_value,
        "per_core_cpu": monitor.get_per_core_cpu.return_value,
        "network_stats": monitor.get_network_stats.return_value
    }
    
    return monitor


@pytest.fixture
def mocked_db_manager():
    """Create a mocked DatabaseManager for testing API endpoints"""
    db_manager = Mock(spec=DatabaseManager)
    
    # Mock CPU history
    db_manager.get_cpu_history.return_value = {
        "timestamps": ["2025-05-25T10:00:00", "2025-05-25T10:01:00", "2025-05-25T10:02:00"],
        "values": [25.5, 30.2, 22.8]
    }
    
    # Mock memory history
    db_manager.get_memory_history.return_value = {
        "timestamps": ["2025-05-25T10:00:00", "2025-05-25T10:01:00"],
        "values": [45.7, 50.2]
    }
    
    # Mock alerts
    db_manager.get_alerts.return_value = [
        {
            "timestamp": "2025-05-25T10:00:00",
            "alert_type": "CPU",
            "message": "High CPU usage detected",
            "value": 85.2
        },
        {
            "timestamp": "2025-05-25T10:05:00",
            "alert_type": "Memory",
            "message": "High memory usage detected",
            "value": 90.1
        }
    ]
    
    return db_manager


@pytest.fixture
def test_client(mocked_system_monitor, mocked_db_manager):
    """Create a test client for FastAPI application with mocked dependencies"""
    # Override dependency injection
    from app.api.endpoints import get_system_monitor, get_db_manager
    
    app.dependency_overrides[get_system_monitor] = lambda: mocked_system_monitor
    app.dependency_overrides[get_db_manager] = lambda: mocked_db_manager
    
    client = TestClient(app)
    
    yield client
    
    # Clean up
    app.dependency_overrides = {}
