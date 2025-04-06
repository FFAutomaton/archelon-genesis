"""
Binance Service Module

This module provides a service for interacting with the Binance API
using the python-binance package.
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BinanceService:
    """
    Service class for interacting with the Binance API.
    
    This class provides methods to fetch market data, account information,
    and execute trades using the Binance API.
    """
    
    def __init__(self, api_key=None, api_secret=None, testnet=False):
        """
        Initialize the BinanceService.
        
        Args:
            api_key (str, optional): Binance API key. Defaults to None.
            api_secret (str, optional): Binance API secret. Defaults to None.
            testnet (bool, optional): Whether to use the testnet. Defaults to False.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize client
        if api_key and api_secret:
            self.client = Client(api_key, api_secret, testnet=testnet)
            logger.info("Initialized Binance client with API key")
        else:
            self.client = Client(None, None)
            logger.info("Initialized Binance client without API key (limited functionality)")
    
    def get_exchange_info(self):
        """
        Get exchange information.
        
        Returns:
            dict: Exchange information.
        """
        try:
            return self.client.get_exchange_info()
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error getting exchange info: {e}")
            return None
    
    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        """
        Get historical klines (candlestick data).
        
        Args:
            symbol (str): Symbol to get klines for (e.g., 'BTCUSDT').
            interval (str): Kline interval (e.g., '1m', '1h', '1d').
            start_str (str): Start time in format 'YYYY-MM-DD' or timestamp.
            end_str (str, optional): End time. Defaults to None.
            
        Returns:
            list: List of klines.
        """
        try:
            return self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str
            )
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error getting historical klines: {e}")
            return None
    
    def get_ticker_price(self, symbol=None):
        """
        Get ticker price for a symbol or all symbols.
        
        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None.
            
        Returns:
            dict or list: Price data.
        """
        try:
            return self.client.get_ticker(symbol=symbol)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error getting ticker price: {e}")
            return None
    
    def get_account_info(self):
        """
        Get account information.
        
        Returns:
            dict: Account information.
        """
        if not self.api_key or not self.api_secret:
            logger.warning("API key and secret required for account information")
            return None
        
        try:
            return self.client.get_account()
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error getting account info: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Initialize service without API credentials (read-only)
    binance_service = BinanceService()
    
    # Get exchange information
    exchange_info = binance_service.get_exchange_info()
    if exchange_info:
        print(f"Exchange status: {exchange_info['status']}")
        print(f"Number of symbols: {len(exchange_info['symbols'])}")
    
    # Get Bitcoin price
    btc_price = binance_service.get_ticker_price(symbol="BTCUSDT")
    if btc_price:
        print(f"Current BTC price: {btc_price['price']}")
