"""Utility functions for Research-Collector."""

import time
from functools import wraps
from typing import Callable, Any, Optional
import requests


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    retry_on: tuple = (requests.exceptions.RequestException, Exception)
) -> Callable:
    """Decorator to retry function on failure with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff delay (seconds)
        retry_on: Tuple of exception types to retry on
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt)
                        print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s (error: {str(e)[:50]})")
                        time.sleep(delay)
                    else:
                        print(f"Max retries ({max_retries}) exceeded for {func.__name__}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


def handle_api_error(response: requests.Response) -> Optional[str]:
    """Handle API error responses.
    
    Args:
        response: Requests response object
    
    Returns:
        Error message string or None if no error
    """
    if response.status_code >= 400:
        try:
            error_data = response.json()
            if 'error' in error_data:
                return error_data['error']
            elif 'message' in error_data:
                return error_data['message']
        except:
            pass
        return f"HTTP {response.status_code}: {response.reason}"
    return None


def safe_get(data: dict, *keys, default: Any = None) -> Any:
    """Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        *keys: Keys to traverse in order
        default: Default value if key not found
    
    Returns:
        Value at nested key path or default
    """
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data
