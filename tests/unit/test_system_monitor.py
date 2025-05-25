"""
Unit tests for SystemMonitor class
"""
import pytest
from unittest.mock import patch, Mock
import psutil
from app.core.system_monitor import SystemMonitor


class TestSystemMonitor:
    """Test suite for the SystemMonitor class"""
    
    def test_get_cpu_usage_success(self):
        """Test that CPU usage is correctly retrieved"""
        with patch('psutil.cpu_percent', return_value=25.5):
            monitor = SystemMonitor()
            result = monitor.get_cpu_usage()
            
            assert result == 25.5
            assert isinstance(result, float)
    
    def test_get_cpu_usage_exception(self):
        """Test that CPU usage returns 0.0 on exception"""
        with patch('psutil.cpu_percent', side_effect=Exception("Test exception")):
            monitor = SystemMonitor()
            result = monitor.get_cpu_usage()
            
            assert result == 0.0
            assert isinstance(result, float)
    
    def test_get_memory_usage_success(self):
        """Test that memory usage is correctly retrieved"""
        mock_memory = Mock()
        mock_memory.total = 17179869184  # 16 GB in bytes
        mock_memory.available = 8589934592  # 8 GB in bytes
        mock_memory.used = 8589934592  # 8 GB in bytes
        mock_memory.percent = 50.0
        
        with patch('psutil.virtual_memory', return_value=mock_memory):
            monitor = SystemMonitor()
            result = monitor.get_memory_usage()
            
            assert result["total_gb"] == pytest.approx(16.0, 0.1)
            assert result["available_gb"] == pytest.approx(8.0, 0.1)
            assert result["used_gb"] == pytest.approx(8.0, 0.1)
            assert result["percent"] == 50.0
    
    def test_get_memory_usage_exception(self):
        """Test that memory usage returns default values on exception"""
        with patch('psutil.virtual_memory', side_effect=Exception("Test exception")):
            monitor = SystemMonitor()
            result = monitor.get_memory_usage()
            
            assert result["total_gb"] == 0.0
            assert result["available_gb"] == 0.0
            assert result["used_gb"] == 0.0
            assert result["percent"] == 0.0
    
    def test_get_disk_usage_success(self):
        """Test that disk usage is correctly retrieved"""
        # Mock partition
        mock_partition = Mock()
        mock_partition.device = "C:\\"
        mock_partition.mountpoint = "C:\\"
        
        # Mock disk usage
        mock_usage = Mock()
        mock_usage.total = 536870912000  # 500 GB in bytes
        mock_usage.used = 268435456000  # 250 GB in bytes
        mock_usage.free = 268435456000  # 250 GB in bytes
        mock_usage.percent = 50.0
        
        with patch('psutil.disk_partitions', return_value=[mock_partition]), \
             patch('psutil.disk_usage', return_value=mock_usage):
            
            monitor = SystemMonitor()
            result = monitor.get_disk_usage()
            
            assert len(result) == 1
            assert result[0]["device"] == "C:\\"
            assert result[0]["mountpoint"] == "C:\\"
            assert result[0]["total_gb"] == pytest.approx(500.0, 0.1)
            assert result[0]["used_gb"] == pytest.approx(250.0, 0.1)
            assert result[0]["free_gb"] == pytest.approx(250.0, 0.1)
            assert result[0]["percent"] == 50.0
    
    def test_disk_usage_handles_permission_error(self):
        """Test that disk usage handles permission errors"""
        # Mock partition
        mock_partition = Mock()
        mock_partition.device = "C:\\"
        mock_partition.mountpoint = "C:\\"
        
        with patch('psutil.disk_partitions', return_value=[mock_partition]), \
             patch('psutil.disk_usage', side_effect=PermissionError("Test permission error")):
            
            monitor = SystemMonitor()
            result = monitor.get_disk_usage()
            
            # Should return empty list since there was a permission error
            assert result == []
    
    def test_get_per_core_cpu(self):
        """Test that per-core CPU usage is correctly retrieved"""
        with patch('psutil.cpu_percent', return_value=[10.0, 15.0, 20.0, 25.0]):
            monitor = SystemMonitor()
            result = monitor.get_per_core_cpu()
            
            assert result == [10.0, 15.0, 20.0, 25.0]
            assert len(result) == 4
            assert all(isinstance(x, float) for x in result)
    
    def test_get_network_stats(self):
        """Test that network stats are correctly retrieved"""
        mock_net = Mock()
        mock_net.bytes_sent = 100 * 1024 * 1024  # 100 MB
        mock_net.bytes_recv = 200 * 1024 * 1024  # 200 MB
        mock_net.packets_sent = 1000
        mock_net.packets_recv = 2000
        
        with patch('psutil.net_io_counters', return_value=mock_net):
            monitor = SystemMonitor()
            result = monitor.get_network_stats()
            
            assert result["bytes_sent"] == pytest.approx(100.0, 0.1)
            assert result["bytes_recv"] == pytest.approx(200.0, 0.1)
            assert result["packets_sent"] == 1000
            assert result["packets_recv"] == 2000
    
    def test_get_top_processes(self):
        """Test that top processes are correctly retrieved"""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'test_process',
            'username': 'test_user',
            'cpu_percent': 10.5,
            'memory_percent': 5.2
        }
        
        with patch('psutil.process_iter', return_value=[mock_proc]), \
             patch('sorted', return_value=[mock_proc]):
            
            monitor = SystemMonitor()
            result = monitor.get_top_processes(limit=1)
            
            assert len(result) == 1
            assert result[0]["pid"] == 1234
            assert result[0]["name"] == "test_process"
            assert result[0]["username"] == "test_user"
            assert result[0]["cpu_percent"] == 10.5
            assert result[0]["memory_percent"] == 5.2
    
    def test_get_top_processes_access_denied(self):
        """Test that top processes handles access denied errors"""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'test_process',
            'username': 'test_user',
            'cpu_percent': 10.5,
            'memory_percent': 5.2
        }
        
        mock_proc_denied = Mock()
        mock_proc_denied.info.side_effect = psutil.AccessDenied("Test access denied")
        
        with patch('psutil.process_iter', return_value=[mock_proc, mock_proc_denied]), \
             patch('sorted', return_value=[mock_proc, mock_proc_denied]):
            
            monitor = SystemMonitor()
            result = monitor.get_top_processes(limit=2)
            
            # Should only contain one process as the other raised AccessDenied
            assert len(result) == 1
            assert result[0]["pid"] == 1234
    
    def test_get_system_info(self):
        """Test that system info aggregates all metrics correctly"""
        monitor = SystemMonitor()
        
        with patch.object(SystemMonitor, 'get_cpu_usage', return_value=25.5), \
             patch.object(SystemMonitor, 'get_memory_usage', return_value={"percent": 50.0}), \
             patch.object(SystemMonitor, 'get_disk_usage', return_value=["disk_data"]), \
             patch.object(SystemMonitor, 'get_per_core_cpu', return_value=[10.0, 20.0]), \
             patch.object(SystemMonitor, 'get_network_stats', return_value={"bytes_sent": 100}):
            
            result = monitor.get_system_info()
            
            assert result["cpu_percent"] == 25.5
            assert result["memory_info"] == {"percent": 50.0}
            assert result["disk_info"] == ["disk_data"]
            assert result["per_core_cpu"] == [10.0, 20.0]
            assert result["network_stats"] == {"bytes_sent": 100}
