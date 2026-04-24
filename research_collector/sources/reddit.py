"""Reddit source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
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
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Reddit for discussions."""
        try:
            # Search Reddit using the public API (no auth required for basic search)
            search_url = f"{self.base_url}/search.json"
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            params = {
                "q": topic,
                "sort": "relevance",
                "limit": 25,
                "t": "week"  # Time filter: hour, day, week, month, year, all
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
                    content = selftext[:500] if selftext else post.get("title", "")
                    
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
                            "subreddit": post.get("subreddit", "unknown"),
                            "score": post.get("score", 0),
                            "num_comments": post.get("num_comments", 0),
                            "over_18": post.get("over_18", False)
                        }
                    }
                    
                    # Filter out NSFW content for educational purposes
                    if formatted_result["metadata"]["over_18"]:
                        continue
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return results[:20]  # Limit results for educational purposes
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Reddit data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Reddit data: {e}")
            return []