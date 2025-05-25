"""
Main application entry point
Initializes and runs the FastAPI application
"""
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.security import HTTPBasic

from app.core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, DB_PATH, HOST, PORT
from app.core.config import METRICS_INTERVAL_SECONDS, CPU_ALERT_THRESHOLD, MEMORY_ALERT_THRESHOLD
from app.core.system_monitor import SystemMonitor
from app.core.metrics_recorder import MetricsRecorder
from app.database.db_manager import DatabaseManager
from app.api.endpoints import router

# Initialize security
security = HTTPBasic()

# Initialize application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# Include API routes
app.include_router(router)


def initialize_app():
    """
    Initialize application components
    - Setup database
    - Start metrics recorder
    """
    # Initialize database
    db_manager = DatabaseManager(db_path=DB_PATH)
    
    # Start metrics recorder
    recorder = MetricsRecorder(
        db_manager=db_manager,
        interval=METRICS_INTERVAL_SECONDS,
        cpu_threshold=CPU_ALERT_THRESHOLD,
        memory_threshold=MEMORY_ALERT_THRESHOLD,
    )
    recorder.start()
    
    return {"db_manager": db_manager, "recorder": recorder}


# Application initialization
app_components = initialize_app()

# Make db_manager available for dependency injection
from app.api.endpoints import get_db_manager

app.dependency_overrides[get_db_manager] = lambda: app_components["db_manager"]


if __name__ == "__main__":
    print("Starting FastAPI System Monitor")
    print(f"Access the application at http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
