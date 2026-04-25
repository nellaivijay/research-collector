"""Reddit source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from research_collector.config import Config


class RedditSource:
    """Reddit social discussions source."""
    
    def __init__(self, config: Config):
        """Initialize Reddit source."""
        self.config = config
        self.base_url = "https://www.reddit.com"
        self.user_agent = "Research-Collector/1.0 (Educational Purpose)"
    
    def search(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search Reddit for discussions."""
        try:
            # Get max results from config or parameter
            if max_results is None:
                max_results = self.config.get("limits.max_results_per_source", 20)
            
            # Ensure max_results is within reasonable bounds
            max_results = min(max(max_results, 1), 100)
            
            # Calculate time difference for Reddit API time filter
            days_diff = (to_date - from_date).days
            
            # Map time difference to Reddit's time filter
            if days_diff <= 1:
                time_filter = "day"
            elif days_diff <= 7:
                time_filter = "week"
            elif days_diff <= 30:
                time_filter = "month"
            elif days_diff <= 365:
                time_filter = "year"
            else:
                time_filter = "all"
            
            # Search Reddit using the public API (no auth required for basic search)
            search_url = f"{self.base_url}/search.json"
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            params = {
                "q": topic,
                "sort": "relevance",
                "limit": min(max_results * 2, 100),  # Get more results to filter by date
                "t": time_filter  # Use dynamic time filter based on date range
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            results = []
            for post_data in posts:
                try:
                    post = post_data.get("data", {})
                    
                    # Convert timestamp to datetime
                    timestamp = post.get("created_utc", 0)
                    post_date = datetime.fromtimestamp(timestamp)
                    
                    # Filter by date range
                    if post_date < from_date or post_date > to_date:
                        continue
                    
                    # Get selftext (post content) or use title if no selftext
                    selftext = post.get("selftext", "")
                    content = selftext[:1000] if selftext else post.get("title", "")
                    
                    # Extract additional metadata
                    subreddit = post.get("subreddit", "unknown")
                    link_flair_text = post.get("link_flair_text", "")
                    link_flair_css_class = post.get("link_flair_css_class", "")
                    is_self = post.get("is_self", False)
                    url = post.get("url", "")
                    domain = post.get("domain", "")
                    
                    # Calculate engagement metrics
                    upvote_ratio = post.get("upvote_ratio", 0)
                    total_awards = post.get("total_awards_received", 0)
                    
                    # Parse created timestamp for temporal features
                    try:
                        days_since_post = (datetime.now(post_date.tzinfo) - post_date).days if post_date.tzinfo else 0
                    except:
                        days_since_post = 0
                    
                    formatted_result = {
                        "id": f"reddit_{post.get('id', 'unknown')}",
                        "title": post.get("title", "No title"),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "author": post.get("author", "Unknown"),
                        "published_date": post_date.isoformat(),
                        "citations": 0,
                        "upvotes": post.get("score", 0),
                        "downloads": 0,
                        "comments": post.get("num_comments", 0),
                        "content": content,
                        "metadata": {
                            "subreddit": subreddit,
                            "score": post.get("score", 0),
                            "num_comments": post.get("num_comments", 0),
                            "over_18": post.get("over_18", False),
                            "link_flair_text": link_flair_text,
                            "link_flair_css_class": link_flair_css_class,
                            "has_flair": bool(link_flair_text),
                            "is_self": is_self,
                            "is_link": not is_self and bool(url),
                            "external_url": url if not is_self else "",
                            "domain": domain,
                            "upvote_ratio": upvote_ratio,
                            "total_awards": total_awards,
                            "has_awards": total_awards > 0,
                            "gilded": post.get("gilded", 0),
                            "is_gilded": post.get("gilded", 0) > 0,
                            "days_since_post": days_since_post,
                            "content_length": len(content),
                            "has_external_link": bool(url and not url.startswith("https://reddit.com")),
                            "stickied": post.get("stickied", False),
                            "pinned": post.get("pinned", False),
                            "locked": post.get("locked", False),
                            "archived": post.get("archived", False),
                            "quarantined": post.get("quarantined", False)
                        }
                    }
                    
                    # Filter out NSFW content for educational purposes
                    if formatted_result["metadata"]["over_18"]:
                        continue
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            # Limit results to max_results
            return results[:max_results]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Reddit data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Reddit data: {e}")
            return []