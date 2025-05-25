"""
Metrics Recorder
Responsible for recording metrics to the database periodically
"""
import time
import datetime
import threading
from typing import Any

from app.core.system_monitor import SystemMonitor
from app.database.db_manager import DatabaseManager


class MetricsRecorder:
    """
    Records system metrics to the database at regular intervals
    """
    
    def __init__(self, db_manager: DatabaseManager, interval: int = 60, cpu_threshold: int = 80, memory_threshold: int = 80):
        """
        Initialize the metrics recorder.
        
        Args:
            db_manager: DatabaseManager instance for database operations
            interval: Recording interval in seconds (default 60)
            cpu_threshold: Threshold for CPU usage alerts
            memory_threshold: Threshold for memory usage alerts
        """
        self.db_manager = db_manager
        self.interval = interval
        self.monitor = SystemMonitor()
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self._running = False
        self._thread = None
    
    def _record_metrics(self) -> None:
        """
        Record system metrics to the database periodically.
        """
        while self._running:
            try:
                # Get current metrics
                cpu = self.monitor.get_cpu_usage()
                memory = self.monitor.get_memory_usage()
                
                # Current timestamp
                timestamp = datetime.datetime.now().isoformat()
                
                # Insert CPU data
                self.db_manager.insert_cpu_data(timestamp, cpu)
                
                # Insert memory data
                self.db_manager.insert_memory_data(timestamp, memory)
                
                # Check for alert conditions
                if cpu > self.cpu_threshold:
                    self.db_manager.insert_alert(
                        timestamp, "CPU", "High CPU usage detected", cpu
                    )
                
                if memory["percent"] > self.memory_threshold:
                    self.db_manager.insert_alert(
                        timestamp, "Memory", "High memory usage detected", memory["percent"]
                    )
                
                # Wait before next recording
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error recording metrics: {e}")
                time.sleep(self.interval)  # Wait and try again
    
    def start(self) -> None:
        """
        Start the metrics recording in a background thread.
        """
        if self._thread is not None and self._thread.is_alive():
            print("Metrics recorder is already running.")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._record_metrics, daemon=True)
        self._thread.start()
        print(f"Metrics recorder started. Recording metrics every {self.interval} seconds.")
    
    def stop(self) -> None:
        """
        Stop the metrics recording.
        """
        self._running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            print("Metrics recorder stopped.")
        else:
            print("Metrics recorder is not running.")
