"""
System Metrics Monitor
Handles collection of system performance metrics
"""
import psutil
from typing import Dict, List, Any, Union, Optional


class SystemMonitor:
    """
    Monitors and collects system performance metrics for CPU, memory, 
    disk usage, and network statistics.
    """
    
    @staticmethod
    def get_cpu_usage() -> float:
        """
        Retrieves the current system-wide CPU utilization percentage.
        
        Returns:
            CPU usage percentage as a float
        """
        try:
            return psutil.cpu_percent(interval=0.5)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """
        Retrieves current system memory usage statistics.
        
        Returns:
            Dictionary with memory usage metrics
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
            }
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return {
                "total_gb": 0.0,
                "available_gb": 0.0,
                "used_gb": 0.0,
                "percent": 0.0,
            }
    
    @staticmethod
    def get_disk_usage() -> List[Dict[str, Any]]:
        """
        Retrieves disk usage statistics.
        
        Returns:
            List of dictionaries with disk metrics for each partition
        """
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except (PermissionError, FileNotFoundError):
                continue
        return disks
    
    @staticmethod
    def get_per_core_cpu() -> List[float]:
        """
        Gets per-core CPU utilization.
        
        Returns:
            List of CPU usage percentages per core
        """
        return psutil.cpu_percent(interval=0.5, percpu=True)
    
    @staticmethod
    def get_network_stats() -> Dict[str, Union[float, int]]:
        """
        Retrieves network I/O statistics.
        
        Returns:
            Dictionary with network I/O metrics
        """
        net = psutil.net_io_counters()
        return {
            "bytes_sent": round(net.bytes_sent / (1024**2), 2),  # MB
            "bytes_recv": round(net.bytes_recv / (1024**2), 2),  # MB
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        }
    
    @staticmethod
    def get_top_processes(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Returns list of top processes by CPU usage.
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of dictionaries with process information
        """
        processes = []
        for proc in sorted(
            psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']), 
            key=lambda x: x.info['cpu_percent'], 
            reverse=True
        )[:limit]:
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "username": proc.info['username'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Collects all system information in a single call.
        
        Returns:
            Dictionary with all system metrics
        """
        return {
            "cpu_percent": self.get_cpu_usage(),
            "memory_info": self.get_memory_usage(),
            "disk_info": self.get_disk_usage(),
            "per_core_cpu": self.get_per_core_cpu(),
            "network_stats": self.get_network_stats()
        }
