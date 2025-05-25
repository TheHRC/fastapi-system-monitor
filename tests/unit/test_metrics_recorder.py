"""
Unit tests for MetricsRecorder class
"""
import pytest
import time
from unittest.mock import patch, Mock, call
import threading

from app.core.metrics_recorder import MetricsRecorder
from app.core.system_monitor import SystemMonitor
from app.database.db_manager import DatabaseManager


class TestMetricsRecorder:
    """Test suite for the MetricsRecorder class"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager"""
        return Mock(spec=DatabaseManager)
    
    @pytest.fixture
    def mock_system_monitor(self):
        """Create a mock system monitor"""
        monitor = Mock(spec=SystemMonitor)
        monitor.get_cpu_usage.return_value = 75.0
        monitor.get_memory_usage.return_value = {
            "percent": 75.0,
            "total_gb": 16.0,
            "used_gb": 12.0,
            "available_gb": 4.0
        }
        return monitor
    
    @pytest.fixture
    def metrics_recorder(self, mock_db_manager):
        """Create a metrics recorder with short interval for testing"""
        with patch('app.core.metrics_recorder.SystemMonitor'):
            recorder = MetricsRecorder(
                db_manager=mock_db_manager,
                interval=0.1,  # Short interval for testing
                cpu_threshold=70,
                memory_threshold=70
            )
            return recorder
    
    def test_init(self, metrics_recorder, mock_db_manager):
        """Test initializing the metrics recorder"""
        assert metrics_recorder.db_manager == mock_db_manager
        assert metrics_recorder.interval == 0.1
        assert metrics_recorder.cpu_threshold == 70
        assert metrics_recorder.memory_threshold == 70
        assert metrics_recorder._running is False
        assert metrics_recorder._thread is None
    
    def test_start_and_stop(self, metrics_recorder):
        """Test starting and stopping the metrics recorder"""
        # Start the recorder
        metrics_recorder.start()
        
        assert metrics_recorder._running is True
        assert metrics_recorder._thread is not None
        assert metrics_recorder._thread.is_alive() is True
        
        # Stop the recorder
        metrics_recorder.stop()
        
        assert metrics_recorder._running is False
        # Give the thread time to terminate
        time.sleep(0.2)
        assert metrics_recorder._thread.is_alive() is False
    
    def test_start_already_running(self, metrics_recorder):
        """Test starting the metrics recorder when it's already running"""
        # Mock the thread to simulate it's already running
        metrics_recorder._running = True
        metrics_recorder._thread = Mock()
        metrics_recorder._thread.is_alive.return_value = True
        
        # Try to start it again
        metrics_recorder.start()
        
        # Should not create a new thread
        assert metrics_recorder._thread.start.called is False
    
    def test_stop_not_running(self, metrics_recorder):
        """Test stopping the metrics recorder when it's not running"""
        # Ensure it's not running
        metrics_recorder._running = False
        metrics_recorder._thread = None
        
        # Try to stop it
        metrics_recorder.stop()
        
        # Should not cause any errors
        assert metrics_recorder._running is False
    
    def test_record_metrics_below_threshold(self, metrics_recorder, mock_db_manager):
        """Test recording metrics when values are below thresholds"""
        # Setup mocks
        with patch('app.core.metrics_recorder.datetime') as mock_datetime, \
             patch.object(metrics_recorder.monitor, 'get_cpu_usage', return_value=50.0), \
             patch.object(metrics_recorder.monitor, 'get_memory_usage', return_value={"percent": 50.0}), \
             patch('time.sleep'):
            
            mock_datetime.datetime.now.return_value.isoformat.return_value = "2025-05-25T12:00:00"
            
            # Run record_metrics once
            metrics_recorder._running = True
            # Use a side effect to ensure we only run the loop once
            mock_db_manager.insert_cpu_data.side_effect = [None, Exception("Stop the loop")]
            
            try:
                metrics_recorder._record_metrics()
            except Exception:
                pass
            
            # Check that metrics were recorded but no alerts
            mock_db_manager.insert_cpu_data.assert_called_once_with("2025-05-25T12:00:00", 50.0)
            mock_db_manager.insert_memory_data.assert_called_once()
            mock_db_manager.insert_alert.assert_not_called()
    
    def test_record_metrics_above_threshold(self, metrics_recorder, mock_db_manager):
        """Test recording metrics when values are above thresholds"""
        # Setup mocks
        with patch('app.core.metrics_recorder.datetime') as mock_datetime, \
             patch.object(metrics_recorder.monitor, 'get_cpu_usage', return_value=80.0), \
             patch.object(metrics_recorder.monitor, 'get_memory_usage', return_value={"percent": 90.0}), \
             patch('time.sleep'):
            
            mock_datetime.datetime.now.return_value.isoformat.return_value = "2025-05-25T12:00:00"
            
            # Run record_metrics once
            metrics_recorder._running = True
            # Use a side effect to ensure we only run the loop once
            mock_db_manager.insert_cpu_data.side_effect = [None, Exception("Stop the loop")]
            
            try:
                metrics_recorder._record_metrics()
            except Exception:
                pass
            
            # Check that metrics and alerts were recorded
            mock_db_manager.insert_cpu_data.assert_called_once_with("2025-05-25T12:00:00", 80.0)
            mock_db_manager.insert_memory_data.assert_called_once()
            
            # Check that both CPU and memory alerts were created
            assert mock_db_manager.insert_alert.call_count == 2
            
            # First call should be CPU alert
            cpu_alert_call = mock_db_manager.insert_alert.call_args_list[0]
            assert cpu_alert_call[0][1] == "CPU"
            assert "CPU" in cpu_alert_call[0][2]
            assert cpu_alert_call[0][3] == 80.0
            
            # Second call should be memory alert
            memory_alert_call = mock_db_manager.insert_alert.call_args_list[1]
            assert memory_alert_call[0][1] == "Memory"
            assert "Memory" in memory_alert_call[0][2]
            assert memory_alert_call[0][3] == 90.0
    
    def test_exception_handling(self, metrics_recorder):
        """Test that exceptions in record_metrics are handled properly"""
        # Setup mocks to raise exception
        with patch.object(metrics_recorder.monitor, 'get_cpu_usage', side_effect=Exception("Test exception")), \
             patch('time.sleep'):
            
            # Run record_metrics once
            metrics_recorder._running = True
            # Use a side effect to ensure we only run the loop twice
            time.sleep.side_effect = [None, Exception("Stop the loop")]
            
            try:
                metrics_recorder._record_metrics()
            except Exception:
                pass
            
            # Should not crash and should continue to next iteration
            assert time.sleep.call_count == 1
