"""
Main FastAPI application file for the Archelon Genesis API.

This module sets up the FastAPI application and includes all routers.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, market_data

# Create FastAPI app
app = FastAPI(
    title="Archelon Genesis API",
    description="API for accessing cryptocurrency market data and trading signals",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(market_data.router, prefix="/market", tags=["Market Data"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "name": "Archelon Genesis API",
        "version": "0.1.0",
        "description": "API for accessing cryptocurrency market data and trading signals",
    }
