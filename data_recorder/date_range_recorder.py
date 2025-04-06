"""
Date Range Recorder

This script extends the functionality of the BinanceExchange class
to fetch historical data for specific date ranges and save it to CSV files.
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


class DateRangeRecorder:
    """
    Records historical data from Binance for specific date ranges.
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

        self.logger.info(f"Initialized DateRangeRecorder for {symbol}")

    def get_historical_klines(self, interval, start_date, end_date):
        """
        Get historical klines for a specific date range.

        Args:
            interval (TimeInterval): The candlestick interval
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: DataFrame containing the historical data
        """
        try:
            # Convert interval enum to string if needed
            interval_str = interval.value if hasattr(interval, 'value') else interval

            self.logger.info(f"Fetching historical klines for {self.symbol} from {start_date} to {end_date} at {interval_str} interval")

            # Convert dates to millisecond timestamps
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

            # Use the client directly to get historical klines with specific date range
            klines = self.exchange.client.futures_historical_klines(
                symbol=self.symbol,
                interval=interval_str,
                start_str=start_ts,
                end_str=end_ts
            )

            self.logger.info(f"Received {len(klines)} klines")

            # Process the klines into a DataFrame
            if klines:
                data = [{
                    "time": candle[0],
                    "datetime": datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_time": candle[6],
                    "quote_asset_volume": float(candle[7]),
                    "number_of_trades": int(candle[8]),
                    "taker_buy_base_asset_volume": float(candle[9]),
                    "taker_buy_quote_asset_volume": float(candle[10])
                } for candle in klines]

                df = pd.DataFrame(data)
                return df
            else:
                self.logger.warning("No data returned from Binance API")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error fetching historical klines: {e}")
            return pd.DataFrame()

    def record_data_for_time_windows(self, interval=TimeInterval.ONE_HOUR):
        """
        Record data for predefined time windows.

        Args:
            interval (TimeInterval): The candlestick interval
        """
        # Define 4 time windows (10-day periods) from the last 3 years
        now = datetime.now()

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

        self.logger.info(f"Recording data for {len(windows)} time windows")

        for window in windows:
            try:
                self.logger.info(f"Processing window {window['name']}: {window['start']} to {window['end']}")

                # Get data for this window
                df = self.get_historical_klines(
                    interval=interval,
                    start_date=window['start'],
                    end_date=window['end']
                )

                if not df.empty:
                    # Save to CSV
                    filename = f"{self.symbol}_{window['name']}_{interval.value}.csv"
                    filepath = os.path.join(self.data_dir, filename)
                    df.to_csv(filepath, index=False)
                    self.logger.info(f"Saved {len(df)} records to {filepath}")
                else:
                    self.logger.warning(f"No data to save for window {window['name']}")

            except Exception as e:
                self.logger.error(f"Error processing window {window['name']}: {e}")


def main(symbol="AVAXUSDT", interval=TimeInterval.ONE_HOUR):
    """
    Main function to run the date range recorder.

    Args:
        symbol (str): Trading pair symbol (default: AVAXUSDT)
        interval (TimeInterval): Time interval for data collection (default: 1h)
    """
    # Create logger directory if it doesn't exist
    os.makedirs("log_files", exist_ok=True)

    # Create logger
    logger = get_logger_(symbol)
    logger.info(f"Starting date range recording process for {symbol} at {interval.value} interval")

    # Create recorder
    recorder = DateRangeRecorder(symbol=symbol, logger=logger)

    # Record data for the specified interval
    logger.info(f"Processing interval: {interval.value}")
    recorder.record_data_for_time_windows(interval)

    logger.info("Date range recording process completed")


if __name__ == "__main__":
    main()
