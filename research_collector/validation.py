"""Simple validation for research results.

Lightweight validation to catch critical data issues without over-engineering.
Focuses on data quality and educational context requirements.
"""

import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def validate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate research results and return validation summary.
    
    Args:
        results: List of research result dictionaries
    
    Returns:
        Dictionary with validation summary and issues found
    """
    if not results:
        logger.warning("No results to validate")
        return {"valid": True, "issues": [], "summary": "No results"}
    
    issues = []
    critical_issues = []
    warnings = []
    
    for i, item in enumerate(results):
        item_issues = _validate_item(item, i)
        
        if item_issues["critical"]:
            critical_issues.extend(item_issues["critical"])
        if item_issues["warnings"]:
            warnings.extend(item_issues["warnings"])
    
    # Log validation results
    total_issues = len(critical_issues) + len(warnings)
    
    if critical_issues:
        logger.error(f"Found {len(critical_issues)} critical validation issues")
        for issue in critical_issues[:10]:  # Log first 10 critical issues
            logger.error(f"  {issue}")
    
    if warnings:
        logger.warning(f"Found {len(warnings)} validation warnings")
        for warning in warnings[:5]:  # Log first 5 warnings
            logger.warning(f"  {warning}")
    
    if total_issues == 0:
        logger.info("✅ All results passed validation")
    else:
        logger.warning(f"⚠️ Validation complete: {len(critical_issues)} critical, {len(warnings)} warnings")
    
    return {
        "valid": len(critical_issues) == 0,
        "critical_issues": critical_issues,
        "warnings": warnings,
        "total_issues": total_issues,
        "total_items": len(results),
        "summary": f"{len(critical_issues)} critical, {len(warnings)} warnings out of {len(results)} items"
    }


def _validate_item(item: Dict[str, Any], index: int) -> Dict[str, List[str]]:
    """
    Validate a single research item.
    
    Args:
        item: Research item dictionary
        index: Item index for error reporting
    
    Returns:
        Dictionary with critical issues and warnings
    """
    critical = []
    warnings = []
    
    # Critical validation - these must pass
    if not item.get("id"):
        critical.append(f"Item {index}: Missing required field 'id'")
    
    if not item.get("title"):
        critical.append(f"Item {index}: Missing required field 'title'")
    
    if not item.get("url"):
        critical.append(f"Item {index}: Missing required field 'url'")
    elif not item["url"].startswith(("http://", "https://")):
        critical.append(f"Item {index}: Invalid URL format: {item['url']}")
    
    if not item.get("source"):
        critical.append(f"Item {index}: Missing required field 'source'")
    elif item["source"] not in [
        "pubmed", "arxiv", "github", "reddit", "stackoverflow",
        "semantic_scholar", "crossref", "paperswithcode", "kaggle",
        "medium", "hackernews", "gdelt"
    ]:
        critical.append(f"Item {index}: Unknown source: {item['source']}")
    
    # Educational context validation
    metadata = item.get("metadata", {})
    if metadata.get("over_18"):
        critical.append(f"Item {index}: NSFW content not allowed (educational context)")
    
    # Warning validation - nice to have but not critical
    if not item.get("author"):
        warnings.append(f"Item {index}: Missing field 'author'")
    
    if not item.get("published_date"):
        warnings.append(f"Item {index}: Missing field 'published_date'")
    
    if not item.get("content"):
        warnings.append(f"Item {index}: Missing field 'content'")
    
    # Check for reasonable field lengths
    title = item.get("title", "")
    if len(title) > 2000:
        warnings.append(f"Item {index}: Title unusually long ({len(title)} chars)")
    
    # Check for negative engagement metrics
    for field in ["citations", "upvotes", "downloads", "comments"]:
        value = item.get(field, 0)
        if value is not None and value < 0:
            warnings.append(f"Item {index}: Negative value for {field}: {value}")
    
    return {"critical": critical, "warnings": warnings}


def log_data_summary(results: List[Dict[str, Any]], topic: str = "unknown"):
    """
    Log summary statistics for research results.
    
    Args:
        results: List of research result dictionaries
        topic: Research topic for context
    """
    if not results:
        logger.info(f"No results for topic: {topic}")
        return
    
    logger.info(f"=" * 60)
    logger.info(f"DATA SUMMARY: {topic}")
    logger.info(f"=" * 60)
    logger.info(f"Total items: {len(results)}")
    
    # Count by source
    by_source = {}
    for item in results:
        source = item.get("source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1
    
    logger.info("Items by source:")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        logger.info(f"  {source:20s}: {count:4d} ({percentage:5.1f}%)")
    
    # Quality metrics from enrichment
    quality_scores = []
    completeness_scores = []
    consistency_scores = []
    validity_scores = []
    
    for item in results:
        quality = item.get("metadata", {}).get("data_quality", {})
        if quality:
            quality_scores.append(quality.get("overall_quality_score", 0))
            completeness_scores.append(quality.get("completeness_score", 0))
            consistency_scores.append(quality.get("consistency_score", 0))
            validity_scores.append(quality.get("validity_score", 0))
    
    if quality_scores:
        logger.info("Quality Metrics:")
        logger.info(f"  Average overall quality: {sum(quality_scores) / len(quality_scores):.2f}/100")
        logger.info(f"  Average completeness:     {sum(completeness_scores) / len(completeness_scores):.2f}/100")
        logger.info(f"  Average consistency:     {sum(consistency_scores) / len(consistency_scores):.2f}/100")
        logger.info(f"  Average validity:        {sum(validity_scores) / len(validity_scores):.2f}/100")
        logger.info(f"  Min quality:             {min(quality_scores):.2f}/100")
        logger.info(f"  Max quality:             {max(quality_scores):.2f}/100")
    
    # Content type distribution
    content_types = {}
    for item in results:
        content_type = item.get("metadata", {}).get("content_type", "unknown")
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    if content_types:
        logger.info("Content types:")
        for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {content_type:20s}: {count:4d}")
    
    # Trending categories
    trending_categories = {"hot": 0, "warm": 0, "cool": 0, "cold": 0}
    for item in results:
        trending = item.get("metadata", {}).get("trending_category", "cold")
        if trending in trending_categories:
            trending_categories[trending] += 1
    
    if any(trending_categories.values()):
        logger.info("Trending categories:")
        for category, count in trending_categories.items():
            if count > 0:
                logger.info(f"  {category:20s}: {count:4d}")
    
    logger.info(f"=" * 60)


def filter_invalid_items(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out items with critical validation issues.
    
    Args:
        results: List of research result dictionaries
    
    Returns:
        Filtered list with only valid items
    """
    if not results:
        return results
    
    valid_items = []
    removed_count = 0
    
    for item in results:
        issues = _validate_item(item, 0)
        if not issues["critical"]:
            valid_items.append(item)
        else:
            removed_count += 1
    
    if removed_count > 0:
        logger.warning(f"Filtered out {removed_count} items with critical issues")
        logger.info(f"Remaining items: {len(valid_items)}")
    
    return valid_items
