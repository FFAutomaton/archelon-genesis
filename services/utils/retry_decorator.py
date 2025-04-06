import time
from functools import wraps
from binance.exceptions import BinanceAPIException, BinanceRequestException


def retry(max_retries=3, delay=1):


    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except (BinanceAPIException, BinanceRequestException) as e:
                    attempts += 1
                    print(f"Attempt {attempts}/{max_retries} failed: {e}")
                    if attempts < max_retries:
                        time.sleep(delay)
                    else:
                        raise  # Re-raise the last exception when retries are exhausted

        return wrapper

    return decorator
