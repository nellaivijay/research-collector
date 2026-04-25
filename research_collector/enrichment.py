"""Data enrichment utilities for Research-Collector."""

from datetime import datetime
from typing import Dict, List, Any
import re


def standardize_date(date_str: str) -> str:
    """
    Standardize date string to ISO 8601 format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Standardized date string or original if parsing fails
    """
    if not date_str or date_str == "Unknown":
        return date_str
    
    # Already in ISO format
    if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
        return date_str[:10]
    
    # Try various date formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y %b %d",
        "%Y-%b-%d",
        "%B %d, %Y",
        "%d %B %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    
    # If all parsing fails, return original
    return date_str


def extract_temporal_features(date_str: str) -> Dict[str, Any]:
    """
    Extract temporal features from date string.
    
    Args:
        date_str: Date string
    
    Returns:
        Dictionary with temporal features
    """
    if not date_str or date_str == "Unknown":
        return {
            "year": None,
            "month": None,
            "day": None,
            "week": None,
            "quarter": None,
            "days_since": None
        }
    
    try:
        # Try to parse the date
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except:
        try:
            # Try other formats
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except:
            return {
                "year": None,
                "month": None,
                "day": None,
                "week": None,
                "quarter": None,
                "days_since": None
            }
    
    # Calculate features
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    days_since = (now - dt).days
    
    return {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "week": dt.isocalendar()[1],
        "quarter": (dt.month - 1) // 3 + 1,
        "days_since": days_since
    }


def classify_ml_subfield(title: str, content: str, tags: List[str] = None) -> List[str]:
    """
    Classify ML/AI research into subfields based on keywords.
    
    Args:
        title: Item title
        content: Item content/abstract
        tags: Existing tags/categories
    
    Returns:
        List of ML subfield tags
    """
    text = f"{title} {content}".lower()
    tags = tags or []
    
    # ML subfield keywords
    subfields = {
        "computer-vision": ["image", "vision", "cnn", "convolutional", "object detection", "segmentation", "recognition", "visual", "opencv", "yolo", "resnet", "vit"],
        "nlp": ["language", "nlp", "text", "bert", "gpt", "transformer", "embedding", "tokenization", "sentiment", "translation", "summarization", "llm", "large language model"],
        "reinforcement-learning": ["reinforcement", "rl", "q-learning", "policy", "agent", "reward", "mdp", "monte carlo", "actor-critic", "dqn", "ppo"],
        "deep-learning": ["deep learning", "neural network", "cnn", "rnn", "lstm", "gru", "transformer", "attention", "backpropagation", "gradient descent"],
        "graph-learning": ["graph", "gcn", "gnn", "node", "edge", "knowledge graph", "graph neural", "networkx"],
        "generative-ai": ["generative", "gan", "vae", "diffusion", "stable diffusion", "midjourney", "dall-e", "generation", "synthetic"],
        "time-series": ["time series", "temporal", "forecasting", "sequence", "lstm", "arima", "prophet"],
        "recommendation": ["recommendation", "collaborative filtering", "matrix factorization", "ranking", "personalization"],
        "optimization": ["optimization", "gradient", "sgd", "adam", "loss function", "convergence"],
        "interpretability": ["interpretability", "explainable", "xai", "shap", "lime", "attention visualization"],
        "federated-learning": ["federated", "distributed", "privacy-preserving", "fl"],
        "few-shot-learning": ["few-shot", "one-shot", "zero-shot", "meta-learning", "few example"],
        "transfer-learning": ["transfer learning", "pre-trained", "fine-tuning", "domain adaptation"],
        "auto-ml": ["auto ml", "automl", "hyperparameter", "neural architecture", "nas"],
        "anomaly-detection": ["anomaly", "outlier", "fraud", "detection", "isolation forest"],
    }
    
    matched_subfields = []
    
    # Check text for keywords
    for subfield, keywords in subfields.items():
        if any(keyword in text for keyword in keywords):
            matched_subfields.append(subfield)
    
    # Also check existing tags
    if tags:
        for tag in tags:
            tag_lower = tag.lower()
            for subfield, keywords in subfields.items():
                if any(keyword in tag_lower for keyword in keywords):
                    if subfield not in matched_subfields:
                        matched_subfields.append(subfield)
    
    return matched_subfields


def extract_keywords(title: str, content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from title and content.
    
    Args:
        title: Item title
        content: Item content
        max_keywords: Maximum number of keywords to extract
    
    Returns:
        List of keywords
    """
    text = f"{title} {content}".lower()
    
    # Common ML/AI technical terms to extract
    technical_terms = [
        "machine learning", "deep learning", "neural network", "transformer",
        "attention", "bert", "gpt", "llm", "reinforcement learning",
        "computer vision", "nlp", "natural language processing",
        "convolutional", "recurrent", "lstm", "gru", "cnn", "rnn",
        "gradient descent", "backpropagation", "optimization",
        "supervised", "unsupervised", "semi-supervised",
        "classification", "regression", "clustering",
        "generative", "discriminative", "adversarial",
        "graph neural", "knowledge graph", "embedding",
        "tokenization", "attention mechanism", "self-attention",
        "pre-trained", "fine-tuning", "transfer learning",
        "few-shot", "zero-shot", "meta-learning",
        "federated learning", "differential privacy",
        "explainable ai", "interpretability",
        "hyperparameter", "architecture search",
        "anomaly detection", "outlier detection"
    ]
    
    found_keywords = []
    for term in technical_terms:
        if term in text and term not in found_keywords:
            found_keywords.append(term)
            if len(found_keywords) >= max_keywords:
                break
    
    return found_keywords


def calculate_content_quality_score(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate content quality scores for an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Dictionary with quality scores
    """
    scores = {
        "abstract_length_score": 0,
        "has_code_score": 0,
        "has_doi_score": 0,
        "engagement_score": 0,
        "recency_score": 0,
        "overall_quality_score": 0
    }
    
    content = item.get("content", "")
    metadata = item.get("metadata", {})
    
    # Abstract length score (0-1, longer is better up to 1000 chars)
    abstract_length = len(content)
    scores["abstract_length_score"] = min(abstract_length / 1000, 1.0)
    
    # Has code score
    has_code = metadata.get("has_code", False)
    if not has_code:
        # Check content for code indicators
        has_code = any(marker in content.lower() for marker in ["```", "<code>", "github", "repository", "implementation"])
    scores["has_code_score"] = 1.0 if has_code else 0.0
    
    # Has DOI score
    has_doi = metadata.get("has_doi", False)
    scores["has_doi_score"] = 1.0 if has_doi else 0.0
    
    # Engagement score (normalized)
    upvotes = item.get("upvotes", 0)
    citations = item.get("citations", 0)
    comments = item.get("comments", 0)
    
    # Log-normalize engagement metrics
    import math
    engagement = math.log1p(upvotes + citations + comments * 2)
    scores["engagement_score"] = min(engagement / 10, 1.0)
    
    # Recency score (newer is better)
    days_since = metadata.get("days_since_publication", metadata.get("days_since_creation", metadata.get("days_since_post", 0)))
    if days_since is not None and days_since < 365:
        scores["recency_score"] = 1.0 - (days_since / 365)
    else:
        scores["recency_score"] = 0.0
    
    # Overall quality score (weighted average)
    scores["overall_quality_score"] = (
        scores["abstract_length_score"] * 0.2 +
        scores["has_code_score"] * 0.15 +
        scores["has_doi_score"] * 0.15 +
        scores["engagement_score"] * 0.3 +
        scores["recency_score"] * 0.2
    )
    
    return scores


def determine_content_type(item: Dict[str, Any]) -> str:
    """
    Determine the content type of an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Content type string
    """
    source = item.get("source", "")
    metadata = item.get("metadata", {})
    
    # Source-based classification
    if source == "pubmed":
        return "paper"
    elif source == "arxiv":
        return "preprint"
    elif source == "semantic_scholar":
        if metadata.get("is_journal_article"):
            return "paper"
        elif metadata.get("is_conference_paper"):
            return "conference_paper"
        elif metadata.get("is_preprint"):
            return "preprint"
        return "paper"
    elif source == "github":
        return "repository"
    elif source == "reddit":
        return "discussion"
    elif source == "stackoverflow":
        return "qa"
    elif source == "hackernews":
        return "discussion"
    elif source == "gdelt":
        return "news"
    else:
        return "unknown"


def enrich_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all enrichment to a single item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Enriched item dictionary
    """
    # Standardize date
    item["published_date"] = standardize_date(item.get("published_date", ""))
    
    # Extract temporal features
    temporal = extract_temporal_features(item["published_date"])
    item["metadata"].update({
        "year": temporal["year"],
        "month": temporal["month"],
        "day": temporal["day"],
        "week": temporal["week"],
        "quarter": temporal["quarter"],
        "days_since": temporal["days_since"]
    })
    
    # Classify ML subfield
    subfields = classify_ml_subfield(
        item.get("title", ""),
        item.get("content", ""),
        item.get("metadata", {}).get("tags", item.get("metadata", {}).get("categories", []))
    )
    item["metadata"]["ml_subfields"] = subfields
    item["metadata"]["subfield_count"] = len(subfields)
    
    # Extract keywords
    keywords = extract_keywords(item.get("title", ""), item.get("content", ""))
    item["metadata"]["keywords"] = keywords
    item["metadata"]["keyword_count"] = len(keywords)
    
    # Calculate quality scores
    quality_scores = calculate_content_quality_score(item)
    item["metadata"]["quality_scores"] = quality_scores
    
    # Determine content type
    content_type = determine_content_type(item)
    item["metadata"]["content_type"] = content_type
    
    # Add searchable flags
    item["metadata"]["has_code"] = quality_scores["has_code_score"] > 0
    item["metadata"]["has_doi"] = quality_scores["has_doi_score"] > 0
    
    return item


def enrich_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply enrichment to all results.
    
    Args:
        results: List of research items
    
    Returns:
        List of enriched items
    """
    return [enrich_item(item.copy()) for item in results]
