import time
import logging
from collections import deque
import threading

class RateLimiter:
    def __init__(self, limit: int, window_size: int):
        self.limit = limit
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()
        self.is_initialized = False
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create a file handler and set the formatter
        file_handler = logging.FileHandler('rate_limiter.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        return logger

    def initialize(self):
        with self.lock:
            self.requests.clear()
            self.is_initialized = True

    def allow_request(self) -> bool:
        with self.lock:
            if not self.is_initialized:
                raise RuntimeError("Rate limiter not initialized. Call initialize() first.")

            current_time = time.time()

            # Remove requests older than the window
            self.requests = deque([t for t in self.requests if current_time - t <= self.window_size])

            # Check if the limit is exceeded
            if len(self.requests) < self.limit:
                self.requests.append(current_time)
                self.logger.info("Request allowed")
                return True
            else:
                self.logger.warning("Rate limit exceeded")
                return False

# Example usage
if __name__ == "__main__":
    rate_limiter = RateLimiter(limit=5, window_size=60)

    try:
        # Simulate requests without initialization
        for _ in range(10):
            rate_limiter.allow_request()
    except RuntimeError as e:
        print(f"Error: {e}")

    # Initialize the rate limiter
    rate_limiter.initialize()

    # Simulate requests after initialization
    for _ in range(10):
        rate_limiter.allow_request()
