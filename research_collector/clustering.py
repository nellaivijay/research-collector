"""Result clustering and deduplication for Research-Collector."""

from typing import List, Dict
import hashlib


def cluster_results(results: List[Dict]) -> List[Dict]:
    """
    Cluster and deduplicate results across sources.
    
    Args:
        results: List of normalized result dictionaries
    
    Returns:
        List of deduplicated and clustered results
    """
    # Simple deduplication based on URL hash
    seen_urls = set()
    deduplicated = []
    
    for result in results:
        url_hash = hashlib.md5(result["url"].encode()).hexdigest()
        if url_hash not in seen_urls:
            seen_urls.add(url_hash)
            deduplicated.append(result)
    
    return deduplicated