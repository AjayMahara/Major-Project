import time
import logging
from collections import deque
import threading
from flask import Flask, request

app = Flask(__name__)

class RateLimiter:
    def __init__(self, limit: int, window_size: int, log_file: str = 'rate_limiter.log'):
        self.limit = limit
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()
        self.is_initialized = False
        self.logger = self.setup_logger(log_file)

    def setup_logger(self, log_file):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # To avoid duplication
        if not logger.handlers:
            try:
                file_handler = logging.FileHandler(log_file)
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - IP: %(ip_address)s - %(message)s')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Error setting up logger: {e}")

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

            self.requests = deque([t for t in self.requests if current_time - t <= self.window_size])

            if len(self.requests) < self.limit:
                self.requests.append(current_time)
                ip_address = request.remote_addr  # Extract the client's IP address from the request headers
                self.logger.info("Request allowed", extra={'ip_address': ip_address})
                return True
            else:
                ip_address = request.remote_addr  # Extract the client's IP address from the request headers
                self.logger.warning("Rate limit exceeded", extra={'ip_address': ip_address})
                return False

# Example usage with Flask
rate_limiter = RateLimiter(limit=5, window_size=60, log_file='rate_limiter.log')

@app.route('/')
def index():
    try:
        if rate_limiter.allow_request():
            return "Request allowed"
        else:
            return "Rate limit exceeded"
    except RuntimeError as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
