"""Crossref source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
from research_collector.config import Config


class CrossrefSource:
    """Crossref academic metadata source."""
    
    def __init__(self, config: Config):
        """Initialize Crossref source."""
        self.config = config
        self.api_key = config.get_api_key("crossref")
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Crossref for academic papers."""
        return [{
            "id": "cr1",
            "title": f"Crossref analysis of {topic}",
            "url": "https://doi.org/10.1000/1",
            "author": "Academic Author",
            "published_date": from_date.isoformat(),
            "citations": 5,
            "upvotes": 0,
            "downloads": 50,
            "comments": 0,
            "content": f"Academic paper about {topic}...",
            "metadata": {"doi": "10.1000/1", "type": "journal-article"}
        }]