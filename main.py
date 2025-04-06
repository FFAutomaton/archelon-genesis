import os
from config import API_KEY, API_SECRET
from services.binance_service import BinanceExchange
from common.static_logger import get_logger_


if __name__ == '__main__':
    try:
        LOOP_SECS = 2
        TOKEN = os.environ.get("TOKEN", "AVAXUSDT")

        logger = get_logger_(TOKEN)
        logger.info(f"Starting Archelon Genesis for {TOKEN}")

        secrets = {"api_key": API_KEY, "api_secret": API_SECRET}
        exchange = BinanceExchange(secrets, logger)