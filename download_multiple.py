"""
Download Multiple Script

This script demonstrates how to download data for multiple symbols and intervals.
"""

import os
import subprocess
import time

# Define symbols and intervals to download
SYMBOLS = ["AVAXUSDT", "BTCUSDT", "ETHUSDT"]
INTERVALS = ["1h"]  # You can add more intervals if needed: "15m", "4h", etc.

def main():
    """Download data for multiple symbols and intervals."""
    print(f"Starting download for {len(SYMBOLS)} symbols with {len(INTERVALS)} intervals each")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("log_files", exist_ok=True)
    
    # Activate virtual environment
    venv_activate = ".venv/bin/activate"
    
    # Download data for each symbol and interval
    for symbol in SYMBOLS:
        for interval in INTERVALS:
            print(f"\nDownloading {symbol} at {interval} interval...")
            
            # Build the command
            cmd = f"source {venv_activate} && python record_data.py {symbol} {interval}"
            
            # Execute the command
            try:
                subprocess.run(cmd, shell=True, check=True)
                print(f"Successfully downloaded {symbol} at {interval} interval")
            except subprocess.CalledProcessError as e:
                print(f"Error downloading {symbol} at {interval} interval: {e}")
            
            # Add a small delay between requests to avoid rate limiting
            time.sleep(1)
    
    print("\nAll downloads completed!")
    
    # List the downloaded files
    print("\nDownloaded files:")
    for file in sorted(os.listdir("data")):
        if file.endswith(".csv"):
            file_size = os.path.getsize(os.path.join("data", file)) / 1024  # Size in KB
            print(f"  - {file} ({file_size:.2f} KB)")


if __name__ == "__main__":
    main()
