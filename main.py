# main.py
import psutil
import uvicorn
import time
import sqlite3
import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import threading

# --- Application Setup ---
app = FastAPI(
    title="System Performance Monitor",
    description="A FastAPI application to monitor CPU and Memory usage.",
    version="0.1.0",
)

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Security Setup ---
security = HTTPBasic()

# --- Database Setup ---
DB_PATH = os.path.join(BASE_DIR, "system_metrics.db")

def setup_database():
    """Initialize the SQLite database and tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
def record_metrics():
    """Record system metrics to the database periodically."""
    while True:
        try:
            # Get current metrics
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            
            # Current timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Connect and insert data
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Insert CPU data
            cursor.execute(
                "INSERT INTO cpu_history VALUES (?, ?)",
                (timestamp, cpu)
            )
            
            # Insert memory data
            cursor.execute(
                "INSERT INTO memory_history VALUES (?, ?, ?, ?, ?)",
                (timestamp, memory["percent"], memory["total_gb"], 
                 memory["used_gb"], memory["available_gb"])
            )
            
            # Check for alert conditions
            if cpu > 80:
                cursor.execute(
                    "INSERT INTO system_alerts (timestamp, alert_type, message, value) VALUES (?, ?, ?, ?)",
                    (timestamp, "CPU", "High CPU usage detected", cpu)
                )
            
            if memory["percent"] > 80:
                cursor.execute(
                    "INSERT INTO system_alerts (timestamp, alert_type, message, value) VALUES (?, ?, ?, ?)",
                    (timestamp, "Memory", "High memory usage detected", memory["percent"])
                )
            
            conn.commit()
            conn.close()
            
            # Wait before next recording
            time.sleep(60)  # Record every minute
            
        except Exception as e:
            print(f"Error recording metrics: {e}")
            time.sleep(60)  # Wait and try again

# Start the metrics recording in a background thread
setup_database()
metrics_thread = threading.Thread(target=record_metrics, daemon=True)
metrics_thread.start()

# --- Templates Setup ---
# This assumes you have a 'templates' directory in the same location as main.py
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Helper Functions ---
def get_cpu_usage():
    """Retrieves the current system-wide CPU utilization percentage."""
    try:
        return psutil.cpu_percent(interval=0.5)
    except Exception as e:
        print(f"Error getting CPU usage: {e}")
        return 0.0

def get_memory_usage():
    """Retrieves current system memory usage statistics."""
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
        
def get_disk_usage():
    """Retrieves disk usage statistics."""
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

def get_per_core_cpu():
    """Gets per-core CPU utilization."""
    return psutil.cpu_percent(interval=0.5, percpu=True)

def get_network_stats():
    """Retrieves network I/O statistics."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent": round(net.bytes_sent / (1024**2), 2),  # MB
        "bytes_recv": round(net.bytes_recv / (1024**2), 2),  # MB
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv
    }

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main HTML page with system performance data.
    """
    cpu_percent = get_cpu_usage()
    memory_info = get_memory_usage()

    context = {
        "request": request,
        "cpu_percent": cpu_percent,
        "memory_total_gb": memory_info["total_gb"],
        "memory_available_gb": memory_info["available_gb"],
        "memory_used_gb": memory_info["used_gb"],
        "memory_percent": memory_info["percent"],
    }
    # Ensure your HTML file is named "index.html" and is in the "templates" directory
    return templates.TemplateResponse("index.html", context)

@app.get("/api/system-info")
async def get_system_info_api():
    """
    Provides system performance data as JSON.
    """
    return {
        "cpu_percent": get_cpu_usage(),
        "memory_info": get_memory_usage(),
        "disk_info": get_disk_usage(),
        "per_core_cpu": get_per_core_cpu(),
        "network_stats": get_network_stats()
    }

@app.get("/api/processes")
async def get_processes():
    """Returns list of top processes by CPU usage."""
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']), 
                      key=lambda x: x.info['cpu_percent'], reverse=True)[:10]:
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

@app.get("/api/history/cpu")
async def get_cpu_history(hours: int = 1):
    """Returns CPU usage history for the specified number of hours."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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

@app.get("/api/history/memory")
async def get_memory_history(hours: int = 1):
    """Returns memory usage history for the specified number of hours."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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

@app.get("/api/alerts")
async def get_alerts(limit: int = 10):
    """Returns the most recent system alerts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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

# --- Main Execution ---
if __name__ == "__main__":
    # To run: uvicorn main:app --reload
    # Ensure you have the 'templates' directory with 'index.html' inside it.
    print("Starting Uvicorn server. Ensure 'templates/index.html' exists.")
    print("Access the application at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)