"""
System Monitor - Documentation

This modular FastAPI application monitors system resources.

1. Import the needed components from the app module
2. Start the application using uvicorn

Usage:
python start.py
"""
print("System Performance Monitor - Setup")
print("==================================")

try:
    # Test importing from app module
    from app.core.system_monitor import SystemMonitor
    from app.core.config import APP_VERSION, HOST, PORT
    
    monitor = SystemMonitor()
    print(f"Successfully loaded SystemMonitor (v{APP_VERSION})")
    
    # Test CPU metrics
    cpu_percent = monitor.get_cpu_usage()
    print(f"Current CPU usage: {cpu_percent:.1f}%")
    
    # Test memory metrics
    memory_info = monitor.get_memory_usage()
    print(f"Current memory usage: {memory_info['percent']:.1f}%")
    print(f"Memory: {memory_info['used_gb']:.2f}GB / {memory_info['total_gb']:.2f}GB")
    
    print("\nSystem monitoring server is ready to start")
    print(f"Run the following command to start the server:")
    print(f"  uvicorn app.main:app --reload --host {HOST} --port {PORT}\n")
    print("Or simply run:")
    print("  python run.py")
    
except ImportError as e:
    print(f"Error importing components: {e}")
    print("\nPlease ensure you have installed the required packages:")
    print("  pip install -r requirements.txt")
    
except Exception as e:
    print(f"Unexpected error: {e}")
