"""Medium source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
import feedparser
from research_collector.config import Config


class MediumSource:
    """Medium blog posts source."""
    
    def __init__(self, config: Config):
        """Initialize Medium source."""
        self.config = config
        # Medium RSS feeds - working publication feeds
        # Note: Medium tag-based feeds (medium.com/tag/*/feed) are deprecated and return 404
        self.feeds = {
            'towards-data-science': 'https://towardsdatascience.com/feed',
            'towards-ai': 'https://towardsai.com/feed',
            'medium-ai-blog': 'https://medium.com/machine-learning-mastery/feed',
            'data-science-medium': 'https://medium.com/data-science-group-ii/feed',
            'ai-research-feed': 'https://medium.com/the-ai-blog/feed',
            # Add more working Medium publication feeds as needed
        }
    
    def search(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search Medium for blog posts."""
        try:
            results = []
            
            # Extract keywords from topic if it contains OR (for expanded search)
            search_terms = topic.split(" OR ") if " OR " in topic else [topic]
            search_terms = [term.strip().lower() for term in search_terms]
            
            # Use all available feeds
            relevant_feeds = list(self.feeds.values())
            
            # Fetch from each relevant feed
            for feed_url in relevant_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries:
                        try:
                            # Parse publication date
                            pub_date = entry.get('published_parsed')
                            if pub_date:
                                pub_dt = datetime(*pub_date[:6])
                            else:
                                pub_dt = datetime.fromtimestamp(entry.get('published_parsed', 0))
                            
                            # Filter by date range
                            if pub_dt < from_date or pub_dt > to_date:
                                continue
                            
                            # Topic filtering - check if title or content contains any search terms
                            title = entry.get('title', '').lower()
                            content = entry.get('summary', entry.get('description', '')).lower()
                            
                            # Check if any search term matches title or content
                            topic_match = any(term in title or term in content for term in search_terms)
                            if not topic_match:
                                continue
                            
                            # Extract content
                            content = entry.get('summary', entry.get('description', ''))
                            if content:
                                # Remove HTML tags
                                import re
                                content = re.sub('<[^<]+?>', '', content)
                                content = content[:1000]
                            else:
                                content = entry.get('title', '')
                            
                            # Extract author
                            author = entry.get('author', 'Unknown')
                            
                            # Calculate engagement metrics
                            comments = entry.get('comments', 0)
                            
                            # Convert tags to list of strings (feedparser returns FeedParserDict)
                            tags = entry.get('tags', [])
                            if tags and isinstance(tags, dict):
                                tags = list(tags.keys()) if hasattr(tags, 'keys') else []
                            elif tags and hasattr(tags, '__iter__') and not isinstance(tags, str):
                                tags = [str(tag) for tag in tags]
                            
                            formatted_result = {
                                "id": f"medium_{entry.get('link', '').split('/')[-1].replace('-', '_')}",
                                "title": entry.get('title', 'No title'),
                                "url": entry.get('link', ''),
                                "author": author,
                                "published_date": pub_dt.strftime("%Y-%m-%d"),
                                "citations": 0,
                                "upvotes": 0,
                                "downloads": 0,
                                "comments": comments,
                                "content": content,
                                "metadata": {
                                    "source_feed": feed_url,
                                    "tags": tags,
                                    "author": author,
                                    "word_count": len(content.split()),
                                    "has_images": '<img' in entry.get('summary', ''),
                                    "reading_time_estimate": len(content.split()) // 200  # ~200 words per minute
                                }
                            }
                            
                            results.append(formatted_result)
                            
                        except Exception:
                            continue
                            
                except Exception as e:
                    print(f"Error fetching Medium feed {feed_url}: {e}")
                    continue
            
            return results[:200]  # Limit to 200 results
            
        except Exception as e:
            print(f"Error processing Medium data: {e}")
            return []
