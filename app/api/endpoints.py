"""
API Endpoints
Defines all API endpoints for the monitoring application
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Union, Optional

from app.core.config import TEMPLATES_DIR
from app.core.system_monitor import SystemMonitor
from app.database.db_manager import DatabaseManager

# Initialize router
router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Dependency to get SystemMonitor instance
def get_system_monitor():
    return SystemMonitor()


# Dependency to get DatabaseManager instance
def get_db_manager():
    from app.core.config import DB_PATH
    return DatabaseManager(DB_PATH)


@router.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    monitor: SystemMonitor = Depends(get_system_monitor)
):
    """
    Serves the main HTML page with system performance data.
    """
    cpu_percent = monitor.get_cpu_usage()
    memory_info = monitor.get_memory_usage()

    context = {
        "request": request,
        "cpu_percent": cpu_percent,
        "memory_total_gb": memory_info["total_gb"],
        "memory_available_gb": memory_info["available_gb"],
        "memory_used_gb": memory_info["used_gb"],
        "memory_percent": memory_info["percent"],
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/api/system-info")
async def get_system_info_api(
    monitor: SystemMonitor = Depends(get_system_monitor)
):
    """
    Provides system performance data as JSON.
    """
    return monitor.get_system_info()


@router.get("/api/processes")
async def get_processes(
    monitor: SystemMonitor = Depends(get_system_monitor)
):
    """Returns list of top processes by CPU usage."""
    return monitor.get_top_processes()


@router.get("/api/history/cpu")
async def get_cpu_history(
    hours: int = 1,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """Returns CPU usage history for the specified number of hours."""
    return db_manager.get_cpu_history(hours)


@router.get("/api/history/memory")
async def get_memory_history(
    hours: int = 1,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """Returns memory usage history for the specified number of hours."""
    return db_manager.get_memory_history(hours)


@router.get("/api/alerts")
async def get_alerts(
    limit: int = 10,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """Returns the most recent system alerts."""
    return db_manager.get_alerts(limit)
