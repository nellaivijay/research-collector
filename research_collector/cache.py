"""Caching system for API responses."""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


class Cache:
    """Simple file-based cache for API responses."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24):
        """Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.research-collector/cache
            ttl_hours: Time-to-live for cache entries in hours
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".research-collector" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, source: str, topic: str, from_date: str, to_date: str) -> str:
        """Generate cache key from parameters."""
        key_string = f"{source}:{topic}:{from_date}:{to_date}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, source: str, topic: str, from_date: str, to_date: str) -> Optional[Any]:
        """Get cached data if available and not expired."""
        cache_key = self._get_cache_key(source, topic, from_date, to_date)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_entry = json.load(f)
            
            # Check if cache is expired
            cached_at = datetime.fromisoformat(cache_entry['cached_at'])
            if datetime.now() - cached_at > self.ttl:
                # Cache expired
                cache_path.unlink()
                return None
            
            return cache_entry['data']
            
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, source: str, topic: str, from_date: str, to_date: str, data: Any) -> None:
        """Store data in cache."""
        cache_key = self._get_cache_key(source, topic, from_date, to_date)
        cache_path = self._get_cache_path(cache_key)
        
        cache_entry = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cache_entry, f)
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def clear_expired(self) -> int:
        """Clear expired cache files.
        
        Returns:
            Number of files cleared
        """
        cleared = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_entry = json.load(f)
                
                cached_at = datetime.fromisoformat(cache_entry['cached_at'])
                if datetime.now() - cached_at > self.ttl:
                    cache_file.unlink()
                    cleared += 1
                    
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink()
                cleared += 1
        
        return cleared
