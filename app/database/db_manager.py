"""
Database Manager for System Monitor
Handles database setup, connections, and operations
"""
import os
import sqlite3
import datetime
from typing import Dict, List, Any, Tuple, Optional


class DatabaseManager:
    """
    Manages database operations for the system monitor application.
    Provides methods to setup database, insert and retrieve metrics.
    """
    def __init__(self, db_path: str):
        """
        Initialize DatabaseManager with the path to the SQLite database file.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.setup_database()
    
    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Creates and returns a database connection and cursor.
        
        Returns:
            Tuple of (connection, cursor)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor
    
    def setup_database(self) -> None:
        """
        Initialize the SQLite database and tables if they don't exist.
        """
        conn, cursor = self.get_connection()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cpu_history (
            timestamp TEXT PRIMARY KEY,
            usage_percent REAL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_history (
            timestamp TEXT PRIMARY KEY,
            usage_percent REAL,
            total_gb REAL,
            used_gb REAL,
            available_gb REAL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            alert_type TEXT,
            message TEXT,
            value REAL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_cpu_data(self, timestamp: str, usage_percent: float) -> None:
        """
        Insert CPU usage data into the database.
        
        Args:
            timestamp: ISO format timestamp
            usage_percent: CPU usage percentage
        """
        conn, cursor = self.get_connection()
        cursor.execute(
            "INSERT INTO cpu_history VALUES (?, ?)",
            (timestamp, usage_percent)
        )
        conn.commit()
        conn.close()
    
    def insert_memory_data(self, timestamp: str, memory_data: Dict[str, float]) -> None:
        """
        Insert memory usage data into the database.
        
        Args:
            timestamp: ISO format timestamp
            memory_data: Dictionary containing memory metrics
        """
        conn, cursor = self.get_connection()
        cursor.execute(
            "INSERT INTO memory_history VALUES (?, ?, ?, ?, ?)",
            (
                timestamp, 
                memory_data["percent"], 
                memory_data["total_gb"], 
                memory_data["used_gb"], 
                memory_data["available_gb"]
            )
        )
        conn.commit()
        conn.close()
    
    def insert_alert(self, timestamp: str, alert_type: str, message: str, value: float) -> None:
        """
        Insert a system alert into the database.
        
        Args:
            timestamp: ISO format timestamp
            alert_type: Type of alert (e.g., 'CPU', 'Memory')
            message: Alert message
            value: Numeric value associated with the alert
        """
        conn, cursor = self.get_connection()
        cursor.execute(
            "INSERT INTO system_alerts (timestamp, alert_type, message, value) VALUES (?, ?, ?, ?)",
            (timestamp, alert_type, message, value)
        )
        conn.commit()
        conn.close()
    
    def get_cpu_history(self, hours: int = 1) -> Dict[str, List]:
        """
        Get CPU usage history for the specified number of hours.
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            Dictionary with timestamps and CPU usage values
        """
        try:
            conn, cursor = self.get_connection()
            
            # Get data from the last X hours
            time_ago = (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
            
            cursor.execute(
                "SELECT timestamp, usage_percent FROM cpu_history WHERE timestamp > ? ORDER BY timestamp",
                (time_ago,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return {
                "timestamps": [row[0] for row in results],
                "values": [row[1] for row in results]
            }
        except Exception as e:
            print(f"Error getting CPU history: {e}")
            return {"timestamps": [], "values": []}
    
    def get_memory_history(self, hours: int = 1) -> Dict[str, List]:
        """
        Get memory usage history for the specified number of hours.
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            Dictionary with timestamps and memory usage values
        """
        try:
            conn, cursor = self.get_connection()
            
            # Get data from the last X hours
            time_ago = (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
            
            cursor.execute(
                "SELECT timestamp, usage_percent FROM memory_history WHERE timestamp > ? ORDER BY timestamp",
                (time_ago,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return {
                "timestamps": [row[0] for row in results],
                "values": [row[1] for row in results]
            }
        except Exception as e:
            print(f"Error getting memory history: {e}")
            return {"timestamps": [], "values": []}
    
    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent system alerts.
        
        Args:
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of alert dictionaries
        """
        try:
            conn, cursor = self.get_connection()
            
            cursor.execute(
                "SELECT timestamp, alert_type, message, value FROM system_alerts ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "alert_type": row[1],
                    "message": row[2],
                    "value": row[3]
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
