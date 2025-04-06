"""
Health check router for the Archelon Genesis API.

This module provides endpoints for checking the health of the API and its dependencies.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sys

# Create router
router = APIRouter()

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    timestamp: str
    version: str
    python_version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Health status information
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0",
            "python_version": sys.version,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
