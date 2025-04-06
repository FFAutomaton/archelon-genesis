"""
Record Data Script

This script runs the data recording process to fetch historical data
from Binance futures and save it to CSV files.

Usage:
    python record_data.py [symbol] [interval]

    symbol: Trading pair symbol (default: AVAXUSDT)
    interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d) (default: 1h)
"""

import os
import sys
import traceback

from data_recorder.date_range_recorder import main as record_data, TimeInterval


def parse_interval(interval_str):
    """Convert string interval to TimeInterval enum."""
    interval_map = {
        "1m": TimeInterval.ONE_MINUTE,
        "5m": TimeInterval.FIVE_MINUTES,
        "15m": TimeInterval.FIFTEEN_MINUTES,
        "1h": TimeInterval.ONE_HOUR,
        "4h": TimeInterval.FOUR_HOURS,
        "1d": TimeInterval.ONE_DAY
    }

    if interval_str not in interval_map:
        print(f"Invalid interval: {interval_str}")
        print(f"Valid intervals: {', '.join(interval_map.keys())}")
        return TimeInterval.ONE_HOUR

    return interval_map[interval_str]


if __name__ == "__main__":
    try:
        print("Starting record_data.py script")

        # Parse command line arguments
        symbol = "AVAXUSDT"  # Default symbol
        interval = TimeInterval.ONE_HOUR  # Default interval

        if len(sys.argv) > 1:
            symbol = sys.argv[1]

        if len(sys.argv) > 2:
            interval = parse_interval(sys.argv[2])

        print(f"Symbol: {symbol}")
        print(f"Interval: {interval.value}")

        # Create necessary directories
        print("Creating necessary directories")
        os.makedirs("data", exist_ok=True)
        os.makedirs("log_files", exist_ok=True)

        # Run the data recording process
        print(f"Running the data recording process for {symbol} at {interval.value} interval")
        record_data(symbol=symbol, interval=interval)
        print("Data recording process completed")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
