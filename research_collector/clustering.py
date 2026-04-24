"""Result clustering and deduplication for Research-Collector."""

from typing import List, Dict, Set, Tuple
import hashlib
import re
from difflib import SequenceMatcher


def cluster_results(results: List[Dict]) -> List[Dict]:
    """
    Cluster and deduplicate results across sources using multiple strategies.
    
    Args:
        results: List of normalized result dictionaries
    
    Returns:
        List of deduplicated and clustered results
    """
    if not results:
        return results
    
    # Multi-strategy deduplication
    deduplicated = []
    seen_signatures: Set[str] = set()
    
    for result in results:
        # Generate multiple signatures for robust deduplication
        signatures = _generate_signatures(result)
        
        # Check if any signature matches existing
        is_duplicate = False
        for sig in signatures:
            if sig in seen_signatures:
                is_duplicate = True
                # Merge engagement metrics from duplicate
                _merge_metrics(deduplicated, result)
                break
        
        if not is_duplicate:
            deduplicated.append(result)
            for sig in signatures:
                seen_signatures.add(sig)
    
    # Cluster similar results
    clustered = _cluster_similar_results(deduplicated)
    
    return clustered


def _generate_signatures(result: Dict) -> List[str]:
    """Generate multiple signatures for a result.
    
    Args:
        result: Result dictionary
    
    Returns:
        List of signature strings
    """
    signatures = []
    
    # URL-based signature
    if result.get("url"):
        url_hash = hashlib.md5(result["url"].encode()).hexdigest()
        signatures.append(f"url:{url_hash}")
    
    # Title-based signature (normalized)
    if result.get("title"):
        normalized_title = _normalize_text(result["title"])
        title_hash = hashlib.md5(normalized_title.encode()).hexdigest()
        signatures.append(f"title:{title_hash}")
    
    # Author + year signature
    if result.get("author") and result.get("published_date"):
        year = result["published_date"][:4] if len(result["published_date"]) >= 4 else ""
        author_year = f"{result['author']}:{year}"
        author_hash = hashlib.md5(author_year.encode()).hexdigest()
        signatures.append(f"author:{author_hash}")
    
    return signatures


def _normalize_text(text: str) -> str:
    """Normalize text for comparison.
    
    Args:
        text: Input text
    
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove common stop words (simplified)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = [w for w in text.split() if w not in stop_words]
    return ' '.join(words)


def _merge_metrics(existing_results: List[Dict], new_result: Dict) -> None:
    """Merge engagement metrics from duplicate into existing result.
    
    Args:
        existing_results: List of existing results
        new_result: New result with potentially higher metrics
    """
    # Find the most similar existing result
    best_match_idx = -1
    best_similarity = 0.0
    
    for i, existing in enumerate(existing_results):
        similarity = _calculate_similarity(existing, new_result)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_idx = i
    
    if best_match_idx >= 0:
        # Merge metrics (take max)
        existing_results[best_match_idx]['citations'] = max(
            existing_results[best_match_idx].get('citations', 0),
            new_result.get('citations', 0)
        )
        existing_results[best_match_idx]['upvotes'] = max(
            existing_results[best_match_idx].get('upvotes', 0),
            new_result.get('upvotes', 0)
        )
        existing_results[best_match_idx]['downloads'] = max(
            existing_results[best_match_idx].get('downloads', 0),
            new_result.get('downloads', 0)
        )
        
        # Add source to metadata if not present
        existing_sources = existing_results[best_match_idx].get('metadata', {}).get('sources', [])
        new_source = new_result.get('source')
        if new_source and new_source not in existing_sources:
            if 'metadata' not in existing_results[best_match_idx]:
                existing_results[best_match_idx]['metadata'] = {}
            if 'sources' not in existing_results[best_match_idx]['metadata']:
                existing_results[best_match_idx]['metadata']['sources'] = []
            existing_results[best_match_idx]['metadata']['sources'].append(new_source)


def _calculate_similarity(result1: Dict, result2: Dict) -> float:
    """Calculate similarity between two results.
    
    Args:
        result1: First result
        result2: Second result
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Title similarity
    title1 = result1.get('title', '')
    title2 = result2.get('title', '')
    title_sim = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    
    # URL similarity (if both have URLs)
    url1 = result1.get('url', '')
    url2 = result2.get('url', '')
    url_sim = 1.0 if url1 == url2 else 0.0
    
    # Author similarity
    author1 = result1.get('author', '').lower()
    author2 = result2.get('author', '').lower()
    author_sim = SequenceMatcher(None, author1, author2).ratio()
    
    # Weighted combination
    return 0.5 * title_sim + 0.3 * url_sim + 0.2 * author_sim


def _cluster_similar_results(results: List[Dict], similarity_threshold: float = 0.8) -> List[Dict]:
    """Cluster similar results together.
    
    Args:
        results: List of results
        similarity_threshold: Minimum similarity to cluster
    
    Returns:
        List of clustered results
    """
    if len(results) <= 1:
        return results
    
    clustered = []
    used_indices = set()
    
    for i, result in enumerate(results):
        if i in used_indices:
            continue
        
        # Find similar results
        similar_indices = [i]
        for j in range(i + 1, len(results)):
            if j in used_indices:
                continue
            
            similarity = _calculate_similarity(result, results[j])
            if similarity >= similarity_threshold:
                similar_indices.append(j)
        
        # If we found similar results, merge them
        if len(similar_indices) > 1:
            merged = result.copy()
            for idx in similar_indices[1:]:
                _merge_metrics([merged], results[idx])
                used_indices.add(idx)
            
            # Add cluster metadata
            if 'metadata' not in merged:
                merged['metadata'] = {}
            merged['metadata']['cluster_size'] = len(similar_indices)
            merged['metadata']['cluster_sources'] = list(set(
                results[idx].get('source') for idx in similar_indices
            ))
            
            clustered.append(merged)
            used_indices.add(i)
        else:
            clustered.append(result)
            used_indices.add(i)
    
    return clustered