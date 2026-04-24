"""Scoring algorithms for Research-Collector."""

from typing import List, Dict
from datetime import datetime
from research_collector.config import Config


def rank_results(results: List[Dict], topic: str, config: Config) -> List[Dict]:
    """
    Rank results by relevance, recency, and engagement.
    
    Args:
        results: List of normalized result dictionaries
        topic: Research topic for relevance scoring
        config: Configuration object with scoring weights
    
    Returns:
        List of ranked results with scores
    """
    weights = config.get("scoring.weights", {
        "relevance": 0.4,
        "recency": 0.3,
        "engagement": 0.3,
    })
    
    for result in results:
        # Calculate relevance score (simple keyword matching)
        relevance_score = _calculate_relevance(result, topic)
        
        # Calculate recency score
        recency_score = _calculate_recency(result)
        
        # Calculate engagement score
        engagement_score = _calculate_engagement(result)
        
        # Calculate weighted score
        result["score"] = (
            weights["relevance"] * relevance_score +
            weights["recency"] * recency_score +
            weights["engagement"] * engagement_score
        )
    
    # Sort by score descending
    return sorted(results, key=lambda x: x["score"], reverse=True)


def _calculate_relevance(result: Dict, topic: str) -> float:
    """Calculate relevance score based on keyword matching."""
    topic_words = topic.lower().split()
    title_words = result["title"].lower().split()
    content_words = result["content"].lower().split()
    
    matches = sum(1 for word in topic_words if word in title_words or word in content_words)
    return min(matches / max(len(topic_words), 1), 1.0)


def _calculate_recency(result: Dict) -> float:
    """Calculate recency score based on publication date."""
    if not result["published_date"]:
        return 0.5  # Default score for unknown dates
    
    try:
        pub_date = datetime.fromisoformat(result["published_date"])
        days_old = (datetime.now() - pub_date).days
        # Score decays over time, max score for recent items
        return max(0.1, 1.0 - (days_old / 365.0))
    except:
        return 0.5


def _calculate_engagement(result: Dict) -> float:
    """Calculate engagement score from various metrics."""
    engagement = result.get("engagement", {})
    total_engagement = (
        engagement.get("citations", 0) * 10 +
        engagement.get("upvotes", 0) +
        engagement.get("downloads", 0) * 0.1 +
        engagement.get("comments", 0) * 0.5
    )
    # Normalize to 0-1 range (log scale)
    import math
    return min(math.log1p(total_engagement) / 10.0, 1.0)