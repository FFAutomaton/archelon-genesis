from datetime import datetime

import pandas as pd
from binance import Client, BinanceAPIException, BinanceRequestException

from services.exchange_base import ExchangeBase
from services.utils.health_decorator import binance_health_check
from services.utils.retry_decorator import retry


class BinanceExchange(ExchangeBase):
    # constants
    MAX_RETRIES = 3
    SLEEP_TIME = 1

    max_candle_count = 100
    contract_type = "PERPETUAL"

    def __init__(self, secrets, logger=None):
        super().__init__()
        self.client = Client(secrets["api_key"], secrets["api_secret"])
        self.logger = logger
        if self.logger:
            self.logger.info("Initializing Binance Exchange")

    @retry(max_retries=MAX_RETRIES, delay=SLEEP_TIME)
    @binance_health_check()
    def get_current_futures_price(self, symbol) -> float:
        try:
            if self.logger:
                self.logger.debug(f"Fetching current futures price for {symbol}")
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            if self.logger:
                self.logger.info(f"Current futures price for {symbol}: {price}")
            return price
        except (BinanceAPIException, BinanceRequestException) as e:
            if self.logger:
                self.logger.error(f"Error fetching futures price for {symbol}: {e}")
            raise e


    @retry(max_retries=MAX_RETRIES, delay=SLEEP_TIME)
    @binance_health_check()
    def get_historical_data(self, symbol, interval):
        try:
            # Convert TimeInterval enum to string if needed
            interval_str = interval.value if hasattr(interval, 'value') else interval

            if self.logger:
                self.logger.debug(f"Fetching historical data for {symbol} at {interval_str} interval")

            candles = self.client.futures_continous_klines(
                pair=symbol,
                interval=interval_str,
                contractType=self.__class__.contract_type,
                limit=self.__class__.max_candle_count
            )

            if self.logger:
                self.logger.debug(f"Received {len(candles)} candles for {symbol}")

            data = [{
                "time": candle[0],
                "datetime": datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                # Human readable time
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            } for candle in candles]

            df = pd.DataFrame(data)
            if self.logger:
                self.logger.debug(f"Historical data processed for {symbol}, first timestamp: {data[0]['datetime']}, last: {data[-1]['datetime']}")
            return df

        except (BinanceAPIException, BinanceRequestException) as e:
            if self.logger:
                self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            else:
                print(f"Error fetching historical data for {symbol}: {e}")
            raise e
