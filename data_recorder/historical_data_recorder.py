"""
Historical Data Recorder

This script fetches historical data for AVAXUSDT futures from Binance
across multiple time windows and saves it to CSV files.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from enum import Enum

# Add the parent directory to the path so we can import from the services package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import API_KEY, API_SECRET
from services.binance_service import BinanceExchange
from common.static_logger import get_logger_


class TimeInterval(Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


class HistoricalDataRecorder:
    """
    Records historical data from Binance for specified time windows.
    """
    
    def __init__(self, symbol="AVAXUSDT", logger=None):
        """
        Initialize the recorder with the specified symbol.
        
        Args:
            symbol (str): The trading pair symbol (default: AVAXUSDT)
            logger: Logger instance
        """
        self.symbol = symbol
        self.logger = logger or get_logger_(symbol)
        
        # Create BinanceExchange instance
        secrets = {"api_key": API_KEY, "api_secret": API_SECRET}
        self.exchange = BinanceExchange(secrets, self.logger)
        
        # Ensure data directory exists
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.logger.info(f"Initialized HistoricalDataRecorder for {symbol}")
    
    def define_time_windows(self):
        """
        Define 4 time windows covering 10-day periods from the last 3 years.
        
        Returns:
            list: List of dictionaries with start and end dates for each window
        """
        # Current date
        now = datetime.now()
        
        # Define 4 time windows (10-day periods) from the last 3 years
        windows = [
            # Recent window (last 10 days)
            {
                "name": "recent",
                "start": (now - timedelta(days=10)).strftime("%Y-%m-%d"),
                "end": now.strftime("%Y-%m-%d")
            },
            # 1 year ago
            {
                "name": "1year_ago",
                "start": (now - timedelta(days=365+5)).strftime("%Y-%m-%d"),
                "end": (now - timedelta(days=365-5)).strftime("%Y-%m-%d")
            },
            # 2 years ago
            {
                "name": "2years_ago",
                "start": (now - timedelta(days=2*365+5)).strftime("%Y-%m-%d"),
                "end": (now - timedelta(days=2*365-5)).strftime("%Y-%m-%d")
            },
            # 3 years ago (or as far back as AVAX has been available)
            {
                "name": "3years_ago",
                "start": (now - timedelta(days=3*365+5)).strftime("%Y-%m-%d"),
                "end": (now - timedelta(days=3*365-5)).strftime("%Y-%m-%d")
            }
        ]
        
        self.logger.info(f"Defined {len(windows)} time windows for data collection")
        for window in windows:
            self.logger.info(f"Window {window['name']}: {window['start']} to {window['end']}")
        
        return windows
    
    def fetch_and_save_data(self, interval=TimeInterval.ONE_HOUR):
        """
        Fetch historical data for each time window and save to CSV.
        
        Args:
            interval (TimeInterval): The candlestick interval
        """
        windows = self.define_time_windows()
        
        for window in windows:
            self.logger.info(f"Fetching data for window {window['name']} at {interval.value} interval")
            
            try:
                # Modify the BinanceExchange.get_historical_data method to accept start and end dates
                # For now, we'll use the existing method which gets the most recent candles
                df = self.exchange.get_historical_data(self.symbol, interval)
                
                if df is not None and not df.empty:
                    # Filter data to only include the date range we want
                    start_date = datetime.strptime(window['start'], "%Y-%m-%d")
                    end_date = datetime.strptime(window['end'], "%Y-%m-%d")
                    
                    # Convert datetime column to datetime objects for filtering
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    
                    # Filter by date range
                    filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
                    
                    if not filtered_df.empty:
                        # Save to CSV
                        filename = f"{self.symbol}_{window['name']}_{interval.value}.csv"
                        filepath = os.path.join(self.data_dir, filename)
                        filtered_df.to_csv(filepath, index=False)
                        self.logger.info(f"Saved {len(filtered_df)} records to {filepath}")
                    else:
                        self.logger.warning(f"No data found in the specified date range for window {window['name']}")
                else:
                    self.logger.warning(f"No data returned from exchange for window {window['name']}")
            
            except Exception as e:
                self.logger.error(f"Error fetching data for window {window['name']}: {e}")


def main():
    """
    Main function to run the historical data recorder.
    """
    # Create logger
    logger = get_logger_("AVAXUSDT")
    logger.info("Starting historical data recording process")
    
    # Create recorder
    recorder = HistoricalDataRecorder(symbol="AVAXUSDT", logger=logger)
    
    # Fetch and save data for different intervals
    intervals = [
        TimeInterval.ONE_HOUR,
        TimeInterval.FOUR_HOURS,
        TimeInterval.ONE_DAY
    ]
    
    for interval in intervals:
        logger.info(f"Processing interval: {interval.value}")
        recorder.fetch_and_save_data(interval)
    
    logger.info("Historical data recording process completed")


if __name__ == "__main__":
    main()
