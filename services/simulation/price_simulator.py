"""
Price Simulator Service

This module provides a service for simulating realistic price movements
for algorithmic trading strategy testing.
"""

import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

# Configure logging
logger = logging.getLogger("price_simulator")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class PriceSimulator:
    """
    Service for simulating realistic price movements for algorithmic trading testing.
    
    This simulator ensures that:
    1. Prices start at the open price and end at the close price
    2. Prices touch both high and low at least once during the period
    3. Price movements follow a somewhat realistic pattern
    """
    
    def __init__(self, data_dir: str = "data", state_file: str = "simulation_state.json"):
        """
        Initialize the price simulator.
        
        Args:
            data_dir: Directory containing historical price data
            state_file: File to store simulation state
        """
        self.data_dir = data_dir
        self.state_file = os.path.join(data_dir, state_file)
        self.state = self._load_state()
        logger.info(f"Price simulator initialized with state: {self.state}")
    
    def _load_state(self) -> Dict[str, Any]:
        """
        Load simulation state from file or create default state.
        
        Returns:
            Dict containing simulation state
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info(f"Loaded state from {self.state_file}")
                    return state
            except Exception as e:
                logger.error(f"Error loading state file: {e}")
        
        # Default state
        default_state = {
            "current_candle_index": 0,
            "current_timestamp": None,
            "current_symbol": "AVAXUSDT",
            "current_interval": "1h",
            "price_points_returned": {},
            "high_touched": {},
            "low_touched": {},
            "simulation_progress": {},
        }
        
        # Save default state
        self._save_state(default_state)
        return default_state
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """
        Save simulation state to file.
        
        Args:
            state: State dictionary to save
        """
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved state to {self.state_file}")
        except Exception as e:
            logger.error(f"Error saving state file: {e}")
    
    def reset_simulation(self, symbol: str = "AVAXUSDT", interval: str = "1h") -> Dict[str, Any]:
        """
        Reset the simulation for a specific symbol and interval.
        
        Args:
            symbol: Trading pair symbol
            interval: Candle interval
            
        Returns:
            Dict containing reset status
        """
        # Reset state for this symbol and interval
        key = f"{symbol}_{interval}"
        
        self.state["current_candle_index"] = 0
        self.state["current_timestamp"] = None
        self.state["current_symbol"] = symbol
        self.state["current_interval"] = interval
        
        if key in self.state["price_points_returned"]:
            del self.state["price_points_returned"][key]
        
        if key in self.state["high_touched"]:
            del self.state["high_touched"][key]
            
        if key in self.state["low_touched"]:
            del self.state["low_touched"][key]
            
        if key in self.state["simulation_progress"]:
            del self.state["simulation_progress"][key]
        
        # Save updated state
        self._save_state(self.state)
        
        logger.info(f"Reset simulation for {symbol} at {interval} interval")
        return {
            "status": "success",
            "message": f"Simulation reset for {symbol} at {interval} interval",
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_candle_data(self, symbol: str, interval: str) -> Optional[pd.DataFrame]:
        """
        Load historical candle data for a specific symbol and interval.
        
        Args:
            symbol: Trading pair symbol
            interval: Candle interval
            
        Returns:
            DataFrame containing historical candle data or None if not found
        """
        # Try to load from recent data first
        file_path = os.path.join(self.data_dir, f"{symbol}_recent_{interval}.csv")
        
        if not os.path.exists(file_path):
            # Try other time windows
            for window in ["1year_ago", "2years_ago", "3years_ago"]:
                alt_path = os.path.join(self.data_dir, f"{symbol}_{window}_{interval}.csv")
                if os.path.exists(alt_path):
                    file_path = alt_path
                    break
        
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                logger.info(f"Loaded {len(df)} candles from {file_path}")
                return df
            except Exception as e:
                logger.error(f"Error loading candle data: {e}")
        else:
            logger.error(f"No data file found for {symbol} at {interval} interval")
        
        return None
    
    def _generate_price_points(self, candle: Dict[str, Any], num_points: int = 60) -> List[Dict[str, Any]]:
        """
        Generate realistic price points within a candle.
        
        This ensures:
        1. First point is the open price
        2. Last point is the close price
        3. High and low are touched at least once
        4. Price movements follow a somewhat realistic pattern
        
        Args:
            candle: Candle data (open, high, low, close, etc.)
            num_points: Number of price points to generate
            
        Returns:
            List of price points with timestamp and price
        """
        open_price = candle["open"]
        high_price = candle["high"]
        low_price = candle["low"]
        close_price = candle["close"]
        
        # Convert timestamp to datetime
        start_time = datetime.fromtimestamp(candle["time"] / 1000)
        end_time = datetime.fromtimestamp(candle["close_time"] / 1000)
        
        # Generate timestamps
        timestamps = [start_time + timedelta(seconds=i * (end_time - start_time).total_seconds() / (num_points - 1)) 
                     for i in range(num_points)]
        
        # Determine when to hit high and low
        # We'll randomly select positions, but ensure they're not the first or last point
        high_idx = random.randint(1, num_points - 2)
        low_idx = random.randint(1, num_points - 2)
        
        # Make sure high and low are at different positions
        while high_idx == low_idx:
            low_idx = random.randint(1, num_points - 2)
        
        # Generate price points
        price_points = []
        
        # Create a random walk with constraints
        prices = [0] * num_points
        prices[0] = open_price
        prices[-1] = close_price
        prices[high_idx] = high_price
        prices[low_idx] = low_price
        
        # Fill in the gaps with a constrained random walk
        # From open to high
        if high_idx > 0:
            for i in range(1, high_idx):
                if prices[i] == 0:  # If not already set
                    # Weighted average between open and high
                    progress = i / high_idx
                    base = open_price + progress * (high_price - open_price)
                    # Add some randomness
                    prices[i] = base + random.uniform(-0.1, 0.1) * (high_price - open_price)
        
        # From high to low (or low to high)
        min_idx = min(high_idx, low_idx)
        max_idx = max(high_idx, low_idx)
        
        if min_idx < max_idx - 1:
            for i in range(min_idx + 1, max_idx):
                if prices[i] == 0:  # If not already set
                    # Weighted average between the two extremes
                    progress = (i - min_idx) / (max_idx - min_idx)
                    start_price = prices[min_idx]
                    end_price = prices[max_idx]
                    base = start_price + progress * (end_price - start_price)
                    # Add some randomness
                    prices[i] = base + random.uniform(-0.1, 0.1) * abs(end_price - start_price)
        
        # From last extreme to close
        last_extreme_idx = max(high_idx, low_idx)
        if last_extreme_idx < num_points - 1:
            for i in range(last_extreme_idx + 1, num_points - 1):
                if prices[i] == 0:  # If not already set
                    # Weighted average between last extreme and close
                    progress = (i - last_extreme_idx) / (num_points - 1 - last_extreme_idx)
                    base = prices[last_extreme_idx] + progress * (close_price - prices[last_extreme_idx])
                    # Add some randomness
                    prices[i] = base + random.uniform(-0.1, 0.1) * abs(close_price - prices[last_extreme_idx])
        
        # Create the price points
        for i in range(num_points):
            price_points.append({
                "timestamp": timestamps[i].isoformat(),
                "price": round(prices[i], 3),
                "is_high": i == high_idx,
                "is_low": i == low_idx,
                "is_open": i == 0,
                "is_close": i == num_points - 1,
                "point_index": i,
                "total_points": num_points
            })
        
        return price_points
    
    def get_current_price(self, symbol: str = "AVAXUSDT", interval: str = "1h") -> Dict[str, Any]:
        """
        Get the current simulated price for a specific symbol and interval.
        
        This method:
        1. Tracks which candle we're currently in
        2. Ensures we progress through the candle realistically
        3. Returns the appropriate price point based on the simulation state
        
        Args:
            symbol: Trading pair symbol
            interval: Candle interval
            
        Returns:
            Dict containing current price information
        """
        # Load candle data
        df = self._load_candle_data(symbol, interval)
        if df is None:
            return {
                "error": "No data available",
                "symbol": symbol,
                "interval": interval,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get the key for this symbol and interval
        key = f"{symbol}_{interval}"
        
        # Initialize state for this key if needed
        if key not in self.state["price_points_returned"]:
            self.state["price_points_returned"][key] = []
        
        if key not in self.state["high_touched"]:
            self.state["high_touched"][key] = False
            
        if key not in self.state["low_touched"]:
            self.state["low_touched"][key] = False
            
        if key not in self.state["simulation_progress"]:
            self.state["simulation_progress"][key] = {
                "candle_index": 0,
                "point_index": 0,
                "total_candles": len(df),
                "price_points": []
            }
        
        # Get the current candle
        candle_index = self.state["simulation_progress"][key]["candle_index"]
        if candle_index >= len(df):
            # Reset to the beginning if we've gone through all candles
            candle_index = 0
            self.state["simulation_progress"][key]["candle_index"] = 0
            self.state["simulation_progress"][key]["point_index"] = 0
            self.state["simulation_progress"][key]["price_points"] = []
        
        # Get the current candle
        candle = df.iloc[candle_index].to_dict()
        
        # Generate price points if needed
        if not self.state["simulation_progress"][key]["price_points"]:
            price_points = self._generate_price_points(candle)
            self.state["simulation_progress"][key]["price_points"] = price_points
        
        # Get the current price point
        point_index = self.state["simulation_progress"][key]["point_index"]
        price_points = self.state["simulation_progress"][key]["price_points"]
        
        if point_index >= len(price_points):
            # Move to the next candle
            candle_index += 1
            self.state["simulation_progress"][key]["candle_index"] = candle_index
            self.state["simulation_progress"][key]["point_index"] = 0
            
            # Check if we've gone through all candles
            if candle_index >= len(df):
                # Reset to the beginning
                candle_index = 0
                self.state["simulation_progress"][key]["candle_index"] = 0
            
            # Get the new candle
            candle = df.iloc[candle_index].to_dict()
            
            # Generate new price points
            price_points = self._generate_price_points(candle)
            self.state["simulation_progress"][key]["price_points"] = price_points
            point_index = 0
        
        # Get the current price point
        price_point = price_points[point_index]
        
        # Update high/low touched state
        if price_point["is_high"]:
            self.state["high_touched"][key] = True
        
        if price_point["is_low"]:
            self.state["low_touched"][key] = True
        
        # Add to returned price points
        self.state["price_points_returned"][key].append(price_point)
        
        # Increment point index for next call
        self.state["simulation_progress"][key]["point_index"] = point_index + 1
        
        # Save state
        self._save_state(self.state)
        
        # Return the price information
        return {
            "symbol": symbol,
            "price": price_point["price"],
            "timestamp": price_point["timestamp"],
            "candle_timestamp": datetime.fromtimestamp(candle["time"] / 1000).isoformat(),
            "candle_close_timestamp": datetime.fromtimestamp(candle["close_time"] / 1000).isoformat(),
            "is_open": price_point["is_open"],
            "is_high": price_point["is_high"],
            "is_low": price_point["is_low"],
            "is_close": price_point["is_close"],
            "simulation_progress": {
                "candle_index": candle_index,
                "point_index": point_index,
                "total_candles": len(df),
                "total_points": len(price_points),
                "high_touched": self.state["high_touched"][key],
                "low_touched": self.state["low_touched"][key]
            }
        }
