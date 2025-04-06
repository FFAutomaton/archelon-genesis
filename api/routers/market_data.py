"""
Market data router for the Archelon Genesis API.

This module provides endpoints for accessing cryptocurrency market data
with simulation capabilities for algorithmic trading strategy testing.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import os
import sys

# Add the parent directory to the path so we can import from the services package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import API_KEY, API_SECRET
from services.binance_service import BinanceExchange
from services.simulation.price_simulator import PriceSimulator
from common.static_logger import get_logger_

# Create router
router = APIRouter()

# Create logger
logger = get_logger_("api")

# Initialize Binance exchange
def get_exchange():
    """
    Dependency to get the Binance exchange instance.

    Returns:
        BinanceExchange: Initialized Binance exchange instance
    """
    try:
        secrets = {"api_key": API_KEY, "api_secret": API_SECRET}
        return BinanceExchange(secrets, logger)
    except Exception as e:
        logger.error(f"Failed to initialize Binance exchange: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize exchange: {str(e)}")

# Initialize price simulator
def get_simulator():
    """
    Dependency to get the price simulator instance.

    Returns:
        PriceSimulator: Initialized price simulator instance
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        return PriceSimulator(data_dir=data_dir)
    except Exception as e:
        logger.error(f"Failed to initialize price simulator: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize price simulator: {str(e)}")

class CandleData(BaseModel):
    """Model for candle data."""
    time: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float

class CandleResponse(BaseModel):
    """Response model for candle data endpoint."""
    symbol: str
    interval: str
    candles: List[CandleData]

class PriceResponse(BaseModel):
    """Response model for current price endpoint."""
    symbol: str
    price: float
    timestamp: str
    simulation_progress: Optional[Dict[str, Any]] = None

class SimulationResetResponse(BaseModel):
    """Response model for simulation reset endpoint."""
    status: str
    message: str
    timestamp: str

@router.get("/candles", response_model=CandleResponse)
async def get_candles(
    symbol: str = Query("AVAXUSDT", description="Trading pair symbol"),
    interval: str = Query("1h", description="Candle interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, description="Number of candles to return", ge=1, le=1000),
    exchange: BinanceExchange = Depends(get_exchange)
):
    """
    Get historical candle data for a specific symbol and interval.

    Args:
        symbol: Trading pair symbol (default: AVAXUSDT)
        interval: Candle interval (default: 1h)
        limit: Number of candles to return (default: 100, max: 1000)

    Returns:
        CandleResponse: Historical candle data
    """
    try:
        # For now, we'll use the existing data from CSV files
        # In a real implementation, you might want to fetch this directly from the exchange

        # Check if we have the data in our CSV files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        recent_file = os.path.join(data_dir, f"{symbol}_recent_{interval}.csv")

        if os.path.exists(recent_file):
            # Load data from CSV
            df = pd.read_csv(recent_file)

            # Limit the number of candles
            df = df.tail(limit)

            # Convert DataFrame to list of dictionaries
            candles = df.to_dict('records')

            return {
                "symbol": symbol,
                "interval": interval,
                "candles": candles
            }
        else:
            # If we don't have the data in CSV, try other time windows
            for window in ["1year_ago", "2years_ago", "3years_ago"]:
                alt_file = os.path.join(data_dir, f"{symbol}_{window}_{interval}.csv")
                if os.path.exists(alt_file):
                    # Load data from CSV
                    df = pd.read_csv(alt_file)

                    # Limit the number of candles
                    df = df.tail(limit)

                    # Convert DataFrame to list of dictionaries
                    candles = df.to_dict('records')

                    return {
                        "symbol": symbol,
                        "interval": interval,
                        "candles": candles
                    }

            # If we still don't have data, log a warning and return empty response
            logger.warning(f"No data found for {symbol} at {interval} interval")
            return {
                "symbol": symbol,
                "interval": interval,
                "candles": []
            }

    except Exception as e:
        logger.error(f"Error getting candle data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get candle data: {str(e)}")

@router.get("/price", response_model=PriceResponse)
async def get_current_price(
    symbol: str = Query("AVAXUSDT", description="Trading pair symbol"),
    interval: str = Query("1h", description="Candle interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    simulator: PriceSimulator = Depends(get_simulator)
):
    """
    Get current simulated price for a specific symbol.

    This endpoint simulates realistic price movements within a candle:
    1. Prices start at the open price and end at the close price
    2. Prices touch both high and low at least once during the period
    3. Price movements follow a somewhat realistic pattern

    Args:
        symbol: Trading pair symbol (default: AVAXUSDT)
        interval: Candle interval (default: 1h)

    Returns:
        PriceResponse: Current simulated price information
    """
    try:
        # Get simulated price from the simulator
        result = simulator.get_current_price(symbol, interval)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return {
            "symbol": result["symbol"],
            "price": result["price"],
            "timestamp": result["timestamp"],
            "simulation_progress": result["simulation_progress"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulated price: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulated price: {str(e)}")

@router.post("/reset-simulation", response_model=SimulationResetResponse)
async def reset_simulation(
    symbol: str = Query("AVAXUSDT", description="Trading pair symbol"),
    interval: str = Query("1h", description="Candle interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    simulator: PriceSimulator = Depends(get_simulator)
):
    """
    Reset the price simulation for a specific symbol and interval.

    Args:
        symbol: Trading pair symbol (default: AVAXUSDT)
        interval: Candle interval (default: 1h)

    Returns:
        SimulationResetResponse: Reset status information
    """
    try:
        # Reset the simulation
        result = simulator.reset_simulation(symbol, interval)

        return {
            "status": result["status"],
            "message": result["message"],
            "timestamp": result["timestamp"]
        }

    except Exception as e:
        logger.error(f"Error resetting simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset simulation: {str(e)}")
