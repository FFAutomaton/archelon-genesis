from functools import wraps
import time
from binance.exceptions import BinanceAPIException, BinanceRequestException


def binance_health_check(max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]  # Assumes the first argument to the function is 'self'
            for attempt in range(max_retries):
                try:
                    self.client.get_server_time()  # Simple health check
                    print("Binance client is healthy. Proceeding with the operation.")
                    return func(*args, **kwargs)
                except (BinanceAPIException, BinanceRequestException) as e:
                    print(f"Health check attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"Waiting {delay} seconds before retrying...")
                        time.sleep(delay)
                    else:
                        print("Binance client is unhealthy after all attempts. Please check the system status.")
                        return None  # Or raise an exception, based on your preference

        return wrapper

    return decorator
