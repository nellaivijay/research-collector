"""Papers With Code source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
from research_collector.config import Config


class PapersWithCodeSource:
    """Papers With Code ML papers source."""
    
    def __init__(self, config: Config):
        """Initialize Papers With Code source."""
        self.config = config
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Papers With Code for ML papers."""
        return [{
            "id": "pwc1",
            "title": f"{topic} with code implementation",
            "url": "https://paperswithcode.com/paper/1",
            "author": "ML Researcher",
            "published_date": from_date.isoformat(),
            "citations": 20,
            "upvotes": 0,
            "downloads": 150,
            "comments": 0,
            "content": f"ML paper about {topic} with code...",
            "metadata": {"framework": "pytorch", "stars": 100}
        }]