"""
Error handling and retry logic module for the Distributed File Sharing System.
Implements exponential backoff and connection management.
"""

import time
import socket
from functools import wraps
from config_loader import config
from logger_config import get_logger

logger = get_logger(__name__)

class RetryableError(Exception):
    """Exception that can be retried"""
    pass

class NonRetryableError(Exception):
    """Exception that should not be retried"""
    pass

def retry_with_backoff(max_attempts=None, initial_delay=1, backoff_factor=2, max_delay=60):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts (from config if None)
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
    """
    if max_attempts is None:
        max_attempts = config.get('client.retry_attempts', 3)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except NonRetryableError as e:
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    
                    # Exponential backoff
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception
        
        return wrapper
    return decorator

class ConnectionPool:
    """Simple connection pool for socket connections"""
    
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.active_connections = 0
        self._semaphore = None
    
    def acquire(self):
        """Acquire a connection slot"""
        if self._semaphore is None:
            import threading
            self._semaphore = threading.Semaphore(self.max_connections)
        
        self._semaphore.acquire()
        self.active_connections += 1
        logger.debug(f"Connection acquired. Active: {self.active_connections}/{self.max_connections}")
    
    def release(self):
        """Release a connection slot"""
        if self._semaphore:
            self._semaphore.release()
            self.active_connections = max(0, self.active_connections - 1)
            logger.debug(f"Connection released. Active: {self.active_connections}/{self.max_connections}")

class SafeSocket:
    """Wrapper for socket with timeout and error handling"""
    
    def __init__(self, timeout=None):
        self.timeout = timeout or config.get('transfer.timeout', 30)
        self.socket = None
    
    def connect(self, host, port):
        """Connect to server with timeout"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((host, port))
            logger.debug(f"Connected to {host}:{port}")
            return True
        except socket.timeout:
            logger.error(f"Connection timeout to {host}:{port}")
            raise RetryableError(f"Connection timeout to {host}:{port}")
        except socket.error as e:
            logger.error(f"Connection error to {host}:{port}: {e}")
            raise RetryableError(f"Connection error: {e}")
    
    def send(self, data):
        """Send data with error handling"""
        try:
            if isinstance(data, str):
                data = data.encode()
            self.socket.sendall(data)
            return True
        except socket.timeout:
            logger.error("Send timeout")
            raise RetryableError("Send timeout")
        except socket.error as e:
            logger.error(f"Send error: {e}")
            raise RetryableError(f"Send error: {e}")
    
    def receive(self, buffer_size=4096):
        """Receive data with error handling"""
        try:
            data = self.socket.recv(buffer_size)
            return data
        except socket.timeout:
            logger.error("Receive timeout")
            raise RetryableError("Receive timeout")
        except socket.error as e:
            logger.error(f"Receive error: {e}")
            raise RetryableError(f"Receive error: {e}")
    
    def receive_all(self, buffer_size=4096):
        """Receive all data until connection closes"""
        data = b""
        try:
            while True:
                chunk = self.socket.recv(buffer_size)
                if not chunk:
                    break
                data += chunk
            return data
        except socket.timeout:
            logger.warning("Receive timeout while reading all data")
            return data
        except socket.error as e:
            logger.error(f"Receive error: {e}")
            raise RetryableError(f"Receive error: {e}")
    
    def close(self):
        """Close socket safely"""
        try:
            if self.socket:
                self.socket.close()
                logger.debug("Socket closed")
        except Exception as e:
            logger.warning(f"Error closing socket: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def handle_errors(func):
    """Decorator for general error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper

# Global connection pool
connection_pool = ConnectionPool(
    max_connections=config.get('transfer.max_connections', 10)
)
