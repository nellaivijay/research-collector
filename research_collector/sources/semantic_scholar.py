"""Semantic Scholar source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
from research_collector.config import Config


class SemanticScholarSource:
    """Semantic Scholar academic papers source."""
    
    def __init__(self, config: Config):
        """Initialize Semantic Scholar source."""
        self.config = config
        self.api_key = config.get_api_key("semantic_scholar")
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for papers."""
        return [{
            "id": "ss1",
            "title": f"Semantic Scholar research on {topic}",
            "url": "https://www.semanticscholar.org/paper/1",
            "author": "Scholar Author",
            "published_date": from_date.isoformat(),
            "citations": 15,
            "upvotes": 0,
            "downloads": 75,
            "comments": 0,
            "content": f"Academic paper about {topic}...",
            "metadata": {"venue": "Conference", "year": from_date.year}
        }]