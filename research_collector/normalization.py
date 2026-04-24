"""Data normalization for Research-Collector."""

from typing import Dict, List, Any


def normalize_results(raw_results: Dict[str, List], topic: str) -> List[Dict]:
    """
    Normalize results from all sources to unified format.
    
    Args:
        raw_results: Dictionary of source-specific results
        topic: Research topic for relevance scoring
    
    Returns:
        List of normalized result dictionaries
    """
    normalized = []
    
    for source_name, results in raw_results.items():
        for result in results:
            normalized_item = {
                "id": result.get("id", ""),
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "source": source_name,
                "author": result.get("author", ""),
                "published_date": result.get("published_date", ""),
                "engagement": {
                    "citations": result.get("citations", 0),
                    "upvotes": result.get("upvotes", 0),
                    "downloads": result.get("downloads", 0),
                    "comments": result.get("comments", 0),
                },
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
            }
            normalized.append(normalized_item)
    
    return normalized