"""Seen papers cache to prevent duplicate processing."""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Set, Dict, Optional


class SeenPapersCache:
    """Cache for tracking seen papers to prevent duplicate processing."""
    
    def __init__(self, cache_path: Optional[str] = None, ttl_days: int = 30):
        """
        Initialize the seen papers cache.
        
        Args:
            cache_path: Path to cache file (default: /tmp/seen_papers.json)
            ttl_days: Time-to-live for cache entries in days
        """
        self.cache_path = cache_path or os.environ.get(
            "SEEN_PAPERS_CACHE_PATH", 
            "/tmp/seen_papers.json"
        )
        self.ttl_days = ttl_days
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict[str, float]:
        """Load cache from disk."""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading seen papers cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_path) or ".", exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache_data, f)
        except Exception as e:
            print(f"Error saving seen papers cache: {e}")
    
    def _clean_expired_entries(self):
        """Remove entries older than TTL."""
        current_time = datetime.now().timestamp()
        cutoff_time = current_time - (self.ttl_days * 24 * 3600)
        
        expired_keys = [
            key for key, timestamp in self.cache_data.items() 
            if timestamp < cutoff_time
        ]
        
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            print(f"Cleaned {len(expired_keys)} expired entries from seen papers cache")
    
    def _generate_paper_key(self, paper: Dict) -> str:
        """
        Generate unique key for a paper.
        
        Uses DOI if available, otherwise falls back to URL + title hash.
        """
        # Try DOI first
        doi = paper.get("doi") or paper.get("metadata", {}).get("doi")
        if doi:
            return f"doi:{doi}"
        
        # Try arXiv ID
        arxiv_id = paper.get("arxiv_id") or paper.get("metadata", {}).get("arxiv_id")
        if arxiv_id:
            return f"arxiv:{arxiv_id}"
        
        # Fall back to URL + title hash
        url = paper.get("url", "")
        title = paper.get("title", "")
        
        if url:
            return f"url:{url}"
        
        if title:
            # Create hash of title for uniqueness
            title_hash = hashlib.md5(title.encode()).hexdigest()
            return f"title:{title_hash}"
        
        # Last resort: use content hash
        content = paper.get("content", "")
        if content:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            return f"content:{content_hash}"
        
        # If nothing works, return empty string (paper won't be cached)
        return ""
    
    def is_seen(self, paper: Dict) -> bool:
        """
        Check if a paper has been seen before.
        
        Args:
            paper: Paper dictionary with at least title or url
            
        Returns:
            True if paper has been seen, False otherwise
        """
        key = self._generate_paper_key(paper)
        if not key:
            return False  # Can't cache without identifiable key
        
        # Clean expired entries first
        self._clean_expired_entries()
        
        return key in self.cache_data
    
    def mark_seen(self, paper: Dict):
        """
        Mark a paper as seen.
        
        Args:
            paper: Paper dictionary to mark as seen
        """
        key = self._generate_paper_key(paper)
        if not key:
            return  # Can't cache without identifiable key
        
        # Use current timestamp
        self.cache_data[key] = datetime.now().timestamp()
        self._save_cache()
    
    def mark_batch_seen(self, papers: list):
        """
        Mark multiple papers as seen in batch.
        
        Args:
            papers: List of paper dictionaries to mark as seen
        """
        current_time = datetime.now().timestamp()
        
        for paper in papers:
            key = self._generate_paper_key(paper)
            if key:
                self.cache_data[key] = current_time
        
        self._save_cache()
    
    def filter_unseen(self, papers: list) -> list:
        """
        Filter list to only include unseen papers.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of papers that haven't been seen before
        """
        # Clean expired entries first
        self._clean_expired_entries()
        
        unseen = []
        for paper in papers:
            if not self.is_seen(paper):
                unseen.append(paper)
        
        return unseen
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        self._clean_expired_entries()
        
        return {
            "total_entries": len(self.cache_data),
            "ttl_days": self.ttl_days,
            "cache_path": self.cache_path
        }
    
    def clear_cache(self):
        """Clear all entries from the cache."""
        self.cache_data = {}
        self._save_cache()
        print("Seen papers cache cleared")