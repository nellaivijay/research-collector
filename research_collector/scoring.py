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
    
    # Get domain-specific keyword weights
    keyword_weights = config.get("scoring.keyword_weights", {})
    
    # Get preferred researchers for boosting
    preferred_researchers = config.get("scoring.preferred_researchers", [])
    
    for result in results:
        # Calculate relevance score (with domain-specific keyword weighting)
        relevance_score = _calculate_relevance(result, topic, keyword_weights)
        
        # Calculate recency score
        recency_score = _calculate_recency(result)
        
        # Calculate engagement score
        engagement_score = _calculate_engagement(result)
        
        # Apply collaborator/author boost if applicable
        author_boost = _calculate_author_boost(result, preferred_researchers)
        
        # Calculate weighted score with author boost
        result["score"] = (
            weights["relevance"] * relevance_score +
            weights["recency"] * recency_score +
            weights["engagement"] * engagement_score
        )
        
        # Apply author boost as multiplier (max 2x boost)
        if author_boost > 0:
            result["score"] = min(result["score"] * (1.0 + author_boost), 2.0)
            result["author_boosted"] = True
    
    # Sort by score descending
    return sorted(results, key=lambda x: x["score"], reverse=True)


def _calculate_relevance(result: Dict, topic: str, keyword_weights: Dict[str, float] = None) -> float:
    """
    Calculate relevance score based on keyword matching with optional domain-specific weighting.
    
    Args:
        result: Result dictionary with title and content
        topic: Research topic
        keyword_weights: Optional domain-specific keyword weights
    
    Returns:
        Relevance score between 0 and 1
    """
    keyword_weights = keyword_weights or {}
    
    topic_words = topic.lower().split()
    title_lower = result["title"].lower()
    content_lower = result["content"].lower()
    
    # Base relevance from topic words
    base_matches = sum(1 for word in topic_words if word in title_lower or word in content_lower)
    base_score = min(base_matches / max(len(topic_words), 1), 1.0)
    
    # Add figure caption relevance if available
    figure_score = _calculate_figure_caption_relevance(result, topic_words, keyword_weights)
    
    # Apply domain-specific keyword weighting if available
    if keyword_weights:
        weighted_score = 0.0
        total_weight = 0.0
        
        for keyword, weight in keyword_weights.items():
            if keyword.lower() in title_lower or keyword.lower() in content_lower:
                weighted_score += weight
            total_weight += weight
        
        if total_weight > 0:
            # Normalize weighted score and combine with base score
            normalized_weighted = weighted_score / total_weight
            # Give 60% weight to domain-specific keywords, 30% to base topic matching, 10% to figures
            return 0.6 * normalized_weighted + 0.3 * base_score + 0.1 * figure_score
    
    # If no keyword weights, combine base score with figure score
    return 0.9 * base_score + 0.1 * figure_score


def _calculate_figure_caption_relevance(result: Dict, topic_words: list, keyword_weights: Dict[str, float] = None) -> float:
    """
    Calculate relevance score based on figure and table captions.
    
    Args:
        result: Result dictionary potentially containing figure_captions
        topic_words: List of topic words to match
        keyword_weights: Optional domain-specific keyword weights
    
    Returns:
        Figure caption relevance score between 0 and 1
    """
    figure_captions = result.get("figure_captions", [])
    if not figure_captions:
        return 0.0
    
    keyword_weights = keyword_weights or {}
    total_score = 0.0
    caption_count = 0
    
    for fig_type, caption in figure_captions:
        caption_lower = caption.lower()
        caption_count += 1
        
        # Check for topic word matches
        topic_matches = sum(1 for word in topic_words if word in caption_lower)
        total_score += topic_matches / max(len(topic_words), 1)
        
        # Check for weighted keyword matches
        if keyword_weights:
            for keyword, weight in keyword_weights.items():
                if keyword.lower() in caption_lower:
                    total_score += weight / 10.0  # Normalize weight contribution
    
    if caption_count == 0:
        return 0.0
    
    # Normalize to 0-1 range
    return min(total_score / caption_count, 1.0)


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
    total_engagement = (
        result.get("citations", 0) * 10 +
        result.get("upvotes", 0) +
        result.get("downloads", 0) * 0.1 +
        result.get("comments", 0) * 0.5
    )
    # Normalize to 0-1 range (log scale)
    import math
    # Ensure total_engagement is non-negative for log1p
    total_engagement = max(0, total_engagement)
    return min(math.log1p(total_engagement) / 10.0, 1.0)


def _calculate_author_boost(result: Dict, preferred_researchers: list) -> float:
    """
    Calculate author boost based on preferred researchers/collaborators.
    
    Args:
        result: Result dictionary with authors field
        preferred_researchers: List of preferred researcher names/identifiers
    
    Returns:
        Boost value between 0 and 1 (0 = no boost, 1 = max boost)
    """
    if not preferred_researchers:
        return 0.0
    
    # Get authors from result
    authors = result.get("authors", "")
    if not authors:
        return 0.0
    
    # Convert to lowercase for case-insensitive matching
    authors_lower = authors.lower()
    
    # Check if any preferred researcher is in the authors list
    for researcher in preferred_researchers:
        researcher_lower = researcher.lower()
        
        # Check for exact match or partial match (last name)
        if researcher_lower in authors_lower:
            return 1.0  # Maximum boost for preferred researchers
    
    return 0.0