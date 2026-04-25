"""Medium source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import feedparser
from research_collector.config import Config


class MediumSource:
    """Medium blog posts source."""
    
    def __init__(self, config: Config):
        """Initialize Medium source."""
        self.config = config
        # Medium RSS feeds for ML/AI topics
        self.feeds = {
            'ml': 'https://medium.com/tag/machine-learning/feed',
            'towards-data-science': 'https://towardsdatascience.com/feed',
            'artificial-intelligence': 'https://medium.com/tag/artificial-intelligence/feed',
            'deep-learning': 'https://medium.com/tag/deep-learning/feed',
            'data-science': 'https://medium.com/tag/data-science/feed'
        }
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Medium for blog posts."""
        try:
            results = []
            
            # Try relevant feeds based on topic
            topic_lower = topic.lower()
            relevant_feeds = []
            
            if 'ml' in topic_lower or 'machine' in topic_lower:
                relevant_feeds.append(self.feeds['ml'])
            if 'data' in topic_lower:
                relevant_feeds.append(self.feeds['data-science'])
                relevant_feeds.append(self.feeds['towards-data-science'])
            if 'ai' in topic_lower or 'artificial' in topic_lower:
                relevant_feeds.append(self.feeds['artificial-intelligence'])
            if 'deep' in topic_lower:
                relevant_feeds.append(self.feeds['deep-learning'])
            
            # If no specific match, use all feeds
            if not relevant_feeds:
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
                                    "tags": entry.get('tags', []),
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
