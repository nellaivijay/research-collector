"""Data enrichment utilities for Research-Collector."""

from datetime import datetime
from typing import Dict, List, Any
import re
import difflib


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
            # Handle cases where tag might not be a string
            if not isinstance(tag, str):
                continue
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


def add_sentiment_analysis(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add sentiment analysis to an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Item with sentiment analysis added
    """
    try:
        # Try to use textblob if available
        from textblob import TextBlob
        text = f"{item.get('title', '')} {item.get('content', '')[:1000]}"
        
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        item['metadata']['sentiment_polarity'] = sentiment.polarity
        item['metadata']['sentiment_subjectivity'] = sentiment.subjectivity
        
        # Add sentiment category
        if sentiment.polarity > 0.3:
            item['metadata']['sentiment_category'] = 'positive'
        elif sentiment.polarity < -0.3:
            item['metadata']['sentiment_category'] = 'negative'
        else:
            item['metadata']['sentiment_category'] = 'neutral'
            
    except ImportError:
        # TextBlob not available, use simple rule-based sentiment
        text = f"{item.get('title', '')} {item.get('content', '')[:500]}".lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'best', 'success', 'improve', 'advance', 'breakthrough', 'innovative']
        negative_words = ['bad', 'poor', 'fail', 'error', 'problem', 'issue', 'worse', 'decline', 'limitation']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            item['metadata']['sentiment_category'] = 'positive'
            item['metadata']['sentiment_polarity'] = 0.3
        elif negative_count > positive_count:
            item['metadata']['sentiment_category'] = 'negative'
            item['metadata']['sentiment_polarity'] = -0.3
        else:
            item['metadata']['sentiment_category'] = 'neutral'
            item['metadata']['sentiment_polarity'] = 0.0
        
        item['metadata']['sentiment_subjectivity'] = 0.5  # Default value
    
    return item


def generate_summary(content: str, max_length: int = 300) -> str:
    """
    Generate a summary from content.
    
    Args:
        content: Content to summarize
        max_length: Maximum length of summary in characters
    
    Returns:
        Summary string
    """
    if not content:
        return ""
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return content[:max_length]
    
    # Take first 2-3 sentences
    summary = ". ".join(sentences[:min(3, len(sentences))])
    
    # Truncate if too long
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
    
    return summary


def calculate_data_quality_metrics(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate data quality metrics for an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Dictionary of quality metrics
    """
    metadata = item.get("metadata", {})
    
    # Required fields
    required_fields = ["id", "title", "url", "source", "published_date"]
    required_present = sum(1 for field in required_fields if item.get(field))
    completeness_score = (required_present / len(required_fields)) * 100
    
    # Optional important fields
    optional_fields = ["author", "content", "tags", "categories"]
    optional_present = sum(1 for field in optional_fields if item.get(field) or metadata.get(field))
    optional_score = (optional_present / len(optional_fields)) * 100
    
    # Overall completeness
    overall_completeness = (completeness_score * 0.7) + (optional_score * 0.3)
    
    # Consistency checks
    consistency_issues = []
    if item.get("published_date") and not metadata.get("year"):
        consistency_issues.append("date_without_year")
    if item.get("url") and not item.get("source"):
        consistency_issues.append("url_without_source")
    if metadata.get("ml_subfields") and not metadata.get("subfield_count"):
        consistency_issues.append("subfields_without_count")
    
    consistency_score = max(0, 100 - (len(consistency_issues) * 10))
    
    # Validity checks
    validity_issues = []
    if item.get("url") and not (item.get("url", "").startswith("http://") or item.get("url", "").startswith("https://")):
        validity_issues.append("invalid_url")
    if item.get("published_date") and item.get("published_date") == "Unknown":
        validity_issues.append("unknown_date")
    
    validity_score = max(0, 100 - (len(validity_issues) * 15))
    
    # Overall quality score
    overall_quality = (overall_completeness * 0.5) + (consistency_score * 0.3) + (validity_score * 0.2)
    
    return {
        "completeness_score": round(overall_completeness, 2),
        "consistency_score": round(consistency_score, 2),
        "validity_score": round(validity_score, 2),
        "overall_quality_score": round(overall_quality, 2),
        "completeness_issues": len(required_fields) - required_present,
        "consistency_issues": consistency_issues,
        "validity_issues": validity_issues
    }


def add_data_quality_metrics(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add data quality metrics to an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Item with quality metrics
    """
    quality_metrics = calculate_data_quality_metrics(item)
    item["metadata"]["data_quality"] = quality_metrics
    
    return item


def calculate_dataset_quality_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate overall dataset quality metrics.
    
    Args:
        results: List of research items
    
    Returns:
        Dictionary of dataset quality metrics
    """
    if not results:
        return {
            "total_items": 0,
            "avg_completeness": 0,
            "avg_consistency": 0,
            "avg_validity": 0,
            "avg_quality": 0
        }
    
    quality_scores = []
    completeness_scores = []
    consistency_scores = []
    validity_scores = []
    
    for item in results:
        quality = item.get("metadata", {}).get("data_quality", {})
        quality_scores.append(quality.get("overall_quality_score", 0))
        completeness_scores.append(quality.get("completeness_score", 0))
        consistency_scores.append(quality.get("consistency_score", 0))
        validity_scores.append(quality.get("validity_score", 0))
    
    return {
        "total_items": len(results),
        "avg_completeness": round(sum(completeness_scores) / len(completeness_scores), 2) if completeness_scores else 0,
        "avg_consistency": round(sum(consistency_scores) / len(consistency_scores), 2) if consistency_scores else 0,
        "avg_validity": round(sum(validity_scores) / len(validity_scores), 2) if validity_scores else 0,
        "avg_quality": round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0,
        "min_quality": round(min(quality_scores), 2) if quality_scores else 0,
        "max_quality": round(max(quality_scores), 2) if quality_scores else 0
    }


def add_automatic_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add automatic summary to an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Item with summary
    """
    content = item.get("content", "")
    if content:
        summary = generate_summary(content)
        item["metadata"]["summary"] = summary
        item["metadata"]["summary_length"] = len(summary)
    else:
        item["metadata"]["summary"] = ""
        item["metadata"]["summary_length"] = 0
    
    return item


def add_trending_metrics(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add trending metrics to an item.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Item with trending metrics
    """
    metadata = item.get("metadata", {})
    
    # Calculate engagement velocity (simplified)
    engagement_score = (
        item.get("upvotes", 0) + 
        item.get("citations", 0) * 2 + 
        item.get("downloads", 0) * 0.5 +
        item.get("comments", 0) * 0.3
    )
    
    # Normalize by age (items get less credit for same engagement as they age)
    days_since = metadata.get("days_since", metadata.get("days_since_publication", metadata.get("days_since_creation", 30)))
    if days_since > 0:
        trending_score = engagement_score / (days_since ** 0.5)
    else:
        trending_score = engagement_score
    
    # Add trending category
    if trending_score > 10:
        metadata["trending_category"] = "hot"
    elif trending_score > 5:
        metadata["trending_category"] = "warm"
    elif trending_score > 1:
        metadata["trending_category"] = "cool"
    else:
        metadata["trending_category"] = "cold"
    
    metadata["trending_score"] = trending_score
    metadata["engagement_score"] = engagement_score
    
    return item


def improve_metadata_completeness(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Improve metadata completeness with fallback logic.
    
    Args:
        item: Research item dictionary
    
    Returns:
        Item with improved metadata
    """
    metadata = item.get("metadata", {})
    
    # Fallback for missing author
    if not metadata.get("author") or metadata.get("author") == "Unknown":
        if item.get("source") == "github":
            metadata["author"] = metadata.get("author", "GitHub User")
        elif item.get("source") == "reddit":
            metadata["author"] = metadata.get("author", "Reddit User")
        else:
            metadata["author"] = "Unknown Author"
    
    # Fallback for missing language
    if not metadata.get("language") or metadata.get("language") == "Unknown":
        metadata["language"] = infer_language(item.get("content", "") + " " + item.get("title", ""))
    
    # Fallback for missing license
    if not metadata.get("license"):
        metadata["license"] = "Unknown"
        metadata["has_license"] = False
    
    # Fallback for missing topics (GitHub)
    if item.get("source") == "github" and not metadata.get("topics"):
        metadata["topics"] = infer_topics_from_content(item.get("content", "") + " " + item.get("title", ""))
    
    # Fallback for missing tags (Stack Overflow)
    if item.get("source") == "stackoverflow" and not metadata.get("tags"):
        metadata["tags"] = infer_tags_from_content(item.get("content", "") + " " + item.get("title", ""))
    
    # Fallback for missing categories (arXiv)
    if item.get("source") == "arxiv" and not metadata.get("categories"):
        metadata["categories"] = infer_categories_from_content(item.get("content", "") + " " + item.get("title", ""))
    
    # Ensure temporal features exist
    if not metadata.get("year"):
        metadata["year"] = extract_year_from_date(item.get("published_date", ""))
    if not metadata.get("month"):
        metadata["month"] = extract_month_from_date(item.get("published_date", ""))
    if not metadata.get("day"):
        metadata["day"] = extract_day_from_date(item.get("published_date", ""))
    
    # Ensure quality scores exist
    if not metadata.get("quality_scores"):
        quality_scores = calculate_content_quality_score(item)
        metadata["quality_scores"] = quality_scores
    
    return item


def infer_language(text: str) -> str:
    """Infer programming language from content."""
    text_lower = text.lower()
    languages = {
        'python': ['python', 'pytorch', 'tensorflow', 'keras', 'numpy', 'pandas', 'scikit'],
        'javascript': ['javascript', 'node', 'react', 'vue', 'angular', 'typescript', 'js'],
        'java': ['java', 'spring', 'maven', 'gradle'],
        'c++': ['c++', 'cpp', 'opencv', 'qt'],
        'r': ['r language', 'rstat', 'ggplot', 'dplyr'],
        'julia': ['julia', 'jupyter'],
        'go': ['golang', 'go language'],
        'rust': ['rust', 'cargo'],
        'swift': ['swift', 'ios'],
        'matlab': ['matlab', 'octave'],
    }
    
    for lang, keywords in languages.items():
        if any(keyword in text_lower for keyword in keywords):
            return lang
    
    return "Unknown"


def infer_topics_from_content(text: str) -> list:
    """Infer GitHub topics from content."""
    text_lower = text.lower()
    topic_keywords = {
        'machine-learning': ['machine learning', 'ml', 'neural network'],
        'deep-learning': ['deep learning', 'deep neural', 'cnn', 'rnn', 'lstm'],
        'computer-vision': ['computer vision', 'image processing', 'object detection'],
        'nlp': ['natural language', 'text processing', 'nlp', 'language model'],
        'data-science': ['data science', 'analytics', 'visualization'],
        'web-scraping': ['scraping', 'crawler', 'beautifulsoup'],
        'api': ['api', 'rest', 'graphql'],
        'database': ['database', 'sql', 'nosql', 'mongodb', 'postgresql'],
        'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
    }
    
    topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)
    
    return topics[:5]  # Limit to 5 topics


def infer_tags_from_content(text: str) -> list:
    """Infer Stack Overflow tags from content."""
    text_lower = text.lower()
    common_tags = {
        'python': ['python', 'pip', 'django', 'flask'],
        'javascript': ['javascript', 'node', 'npm', 'express'],
        'java': ['java', 'spring', 'maven'],
        'c#': ['c#', '.net', 'asp.net'],
        'sql': ['sql', 'database', 'query'],
        'html': ['html', 'css', 'javascript'],
        'git': ['git', 'github', 'version control'],
        'linux': ['linux', 'ubuntu', 'shell', 'bash'],
        'windows': ['windows', 'powershell'],
        'docker': ['docker', 'container'],
    }
    
    tags = []
    for tag, keywords in common_tags.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append(tag)
    
    return tags[:5]  # Limit to 5 tags


def infer_categories_from_content(text: str) -> list:
    """Infer arXiv categories from content."""
    text_lower = text.lower()
    category_keywords = {
        'cs.AI': ['artificial intelligence', 'machine learning', 'neural'],
        'cs.LG': ['language', 'nlp', 'natural language'],
        'cs.CV': ['vision', 'image', 'computer vision'],
        'cs.CL': ['computation', 'learning', 'computational learning'],
        'cs.RO': ['robotics', 'robot'],
        'cs.NE': ['neural', 'networks', 'neural networks'],
        'stat.ML': ['statistics', 'machine learning', 'statistical'],
        'cs.CR': ['cryptography', 'security'],
        'cs.DB': ['database', 'data'],
    }
    
    categories = []
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            categories.append(category)
    
    return categories[:3]  # Limit to 3 categories


def extract_year_from_date(date_str: str) -> int:
    """Extract year from date string."""
    try:
        if date_str and date_str != "Unknown":
            # Try various date formats
            import re
            year_match = re.search(r'\d{4}', date_str)
            if year_match:
                return int(year_match.group())
    except:
        pass
    return None


def extract_month_from_date(date_str: str) -> int:
    """Extract month from date string."""
    try:
        if date_str and date_str != "Unknown":
            import re
            # Look for month patterns
            if re.search(r'-(\d{2})-', date_str):
                return int(re.search(r'-(\d{2})-', date_str).group(1))
            elif re.search(r'/(\d{2})/', date_str):
                return int(re.search(r'/(\d{2})/', date_str).group(1))
    except:
        pass
    return None


def extract_day_from_date(date_str: str) -> int:
    """Extract day from date string."""
    try:
        if date_str and date_str != "Unknown":
            import re
            if re.search(r'-(\d{2})$', date_str):
                return int(re.search(r'-(\d{2})$', date_str).group(1))
            elif re.search(r'/(\d{2})$', date_str):
                return int(re.search(r'/(\d{2})$', date_str).group(1))
    except:
        pass
    return None


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


def calculate_string_similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings using difflib.
    
    Args:
        s1: First string
        s2: Second string
    
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if not s1 or not s2:
        return 0.0
    return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def are_items_similar(item1: Dict[str, Any], item2: Dict[str, Any], threshold: float = 0.85) -> bool:
    """
    Check if two items are similar using fuzzy matching on title, URL, and content.
    
    Args:
        item1: First item
        item2: Second item
        threshold: Similarity threshold (default 0.85)
    
    Returns:
        True if items are similar
    """
    # Check exact ID match first
    if item1.get("id") == item2.get("id"):
        return True
    
    # Check URL similarity
    url1 = item1.get("url", "")
    url2 = item2.get("url", "")
    if url1 and url2:
        url_similarity = calculate_string_similarity(url1, url2)
        if url_similarity > threshold:
            return True
    
    # Check title similarity
    title1 = item1.get("title", "")
    title2 = item2.get("title", "")
    if title1 and title2:
        title_similarity = calculate_string_similarity(title1, title2)
        if title_similarity > threshold:
            return True
    
    # Check content similarity (first 500 chars)
    content1 = item1.get("content", "")[:500]
    content2 = item2.get("content", "")[:500]
    if content1 and content2:
        content_similarity = calculate_string_similarity(content1, content2)
        if content_similarity > threshold * 0.9:  # Slightly lower threshold for content
            return True
    
    return False


def deduplicate_results_fuzzy(results: List[Dict[str, Any]], threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Remove duplicate items using fuzzy matching.
    
    Args:
        results: List of research items
        threshold: Similarity threshold (default 0.85)
    
    Returns:
        Deduplicated list of items
    """
    if not results:
        return results
    
    deduplicated = []
    seen_ids = set()
    
    for item in results:
        item_id = item.get("id", "")
        
        # Check exact ID match
        if item_id and item_id in seen_ids:
            continue
        
        # Check fuzzy similarity with existing items
        is_duplicate = False
        for existing_item in deduplicated:
            if are_items_similar(item, existing_item, threshold):
                is_duplicate = True
                # Merge metadata from duplicate into existing item
                existing_metadata = existing_item.get("metadata", {})
                new_metadata = item.get("metadata", {})
                
                # Merge lists
                for key in ["tags", "categories", "ml_subfields", "keywords"]:
                    if key in new_metadata and key in existing_metadata:
                        existing_metadata[key] = list(set(existing_metadata[key] + new_metadata[key]))
                    elif key in new_metadata:
                        existing_metadata[key] = new_metadata[key]
                
                # Take max of numeric fields
                for key in ["upvotes", "citations", "downloads", "comments", "stars", "forks"]:
                    if key in new_metadata and key in existing_metadata:
                        existing_metadata[key] = max(existing_metadata[key], new_metadata[key])
                    elif key in new_metadata:
                        existing_metadata[key] = new_metadata[key]
                
                break
        
        if not is_duplicate:
            deduplicated.append(item)
            if item_id:
                seen_ids.add(item_id)
    
    return deduplicated


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
    
    # Add sentiment analysis
    item = add_sentiment_analysis(item)
    
    # Add automatic summary
    item = add_automatic_summary(item)
    
    # Add data quality metrics
    item = add_data_quality_metrics(item)
    
    # Improve metadata completeness
    item = improve_metadata_completeness(item)
    
    # Add trending metrics
    item = add_trending_metrics(item)
    
    return item


def add_cross_references(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add cross-references between related items.
    
    Args:
        results: List of research items
    
    Returns:
        List of items with cross-references
    """
    if not results:
        return results
    
    # Build index of items by ID
    items_by_id = {item.get("id", str(i)): item for i, item in enumerate(results)}
    
    for item in results:
        item_id = item.get("id", "")
        metadata = item.get("metadata", {})
        
        # Find related items based on shared attributes
        related_items = []
        
        for other_id, other_item in items_by_id.items():
            if other_id == item_id:
                continue
            
            other_metadata = other_item.get("metadata", {})
            
            # Check for shared ML subfields
            subfields1 = set(metadata.get("ml_subfields", []))
            subfields2 = set(other_metadata.get("ml_subfields", []))
            shared_subfields = subfields1 & subfields2
            
            # Check for shared keywords
            keywords1 = set(metadata.get("keywords", []))
            keywords2 = set(other_metadata.get("keywords", []))
            shared_keywords = keywords1 & keywords2
            
            # Check for shared tags
            tags1 = set(metadata.get("tags", []))
            tags2 = set(other_metadata.get("tags", []))
            shared_tags = tags1 & tags2
            
            # Calculate similarity score
            similarity_score = 0
            if shared_subfields:
                similarity_score += len(shared_subfields) * 3
            if shared_keywords:
                similarity_score += len(shared_keywords) * 2
            if shared_tags:
                similarity_score += len(shared_tags) * 1
            
            # Add as related if similarity threshold met
            if similarity_score >= 3:
                related_items.append({
                    "id": other_id,
                    "title": other_item.get("title", ""),
                    "similarity_score": similarity_score,
                    "shared_subfields": list(shared_subfields),
                    "shared_keywords": list(shared_keywords),
                    "shared_tags": list(shared_tags)
                })
        
        # Sort by similarity score and keep top 5
        related_items.sort(key=lambda x: x["similarity_score"], reverse=True)
        metadata["related_items"] = related_items[:5]
        metadata["related_count"] = len(related_items[:5])
    
    return results


def enrich_results(results: List[Dict[str, Any]], use_fuzzy_dedup: bool = True, add_cross_refs: bool = True) -> List[Dict[str, Any]]:
    """
    Apply enrichment to all results.
    
    Args:
        results: List of research items
        use_fuzzy_dedup: Whether to use fuzzy deduplication (default True)
        add_cross_refs: Whether to add cross-references (default True)
    
    Returns:
        List of enriched items
    """
    # Enrich all items
    enriched = [enrich_item(item.copy()) for item in results]
    
    # Apply fuzzy deduplication
    if use_fuzzy_dedup:
        enriched = deduplicate_results_fuzzy(enriched)
    
    # Add cross-references
    if add_cross_refs:
        enriched = add_cross_references(enriched)
    
    return enriched
