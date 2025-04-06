from abc import ABC, abstractmethod

import pandas as pd


class ExchangeBase(ABC):

    def __init__(self):
        pass
    # @abstractmethod
    # def get_current_price(self, symbol: str) -> float:
    #     """Retrieve the current price of the specified symbol."""
    #     pass
    #
    # @abstractmethod
    # def get_wallet_balance(self) -> dict:
    #     """Retrieve the wallet balance."""
    #     pass
    #
    # @abstractmethod
    # def get_candles(self, symbol: str, end_time: str, interval: str) -> pd.DataFrame:
    #     """Retrieve historical candlestick data."""
    #     pass

    # @abstractmethod
    # def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None) -> dict:
    #     """Place an order."""
    #     pass
    #
    # @abstractmethod
    # def cancel_order(self, symbol: str, order_id: str) -> dict:
    #     """Cancel an existing order."""
    #     pass
