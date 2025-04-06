"""
Run the Archelon Genesis API.

This script starts the FastAPI application using Uvicorn.
"""

import uvicorn
import os

if __name__ == "__main__":
    # Create log directory if it doesn't exist
    os.makedirs("log_files", exist_ok=True)
    
    # Run the FastAPI application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
