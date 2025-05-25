"""
FastAPI System Monitor - Main Entry Point
"""
import uvicorn
from app.core.config import HOST, PORT

if __name__ == "__main__":
    print("Starting FastAPI System Monitor")
    print("Ensure 'templates/index.html' exists.")
    print(f"Access the application at http://{HOST}:{PORT}")
    
    # Start the application with hot reloading for development
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
