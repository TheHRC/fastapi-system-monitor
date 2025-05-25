"""
Application Configuration
Contains constants and settings for the system monitor
"""
import os

# Application Info
APP_TITLE = "System Performance Monitor"
APP_DESCRIPTION = "A FastAPI application to monitor CPU and Memory usage."
APP_VERSION = "0.1.0"

# Path Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "system_metrics.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Metrics Recording Settings
METRICS_INTERVAL_SECONDS = 60  # Record every minute
CPU_ALERT_THRESHOLD = 80  # CPU usage percentage threshold for alerts
MEMORY_ALERT_THRESHOLD = 80  # Memory usage percentage threshold for alerts

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
