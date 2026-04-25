"""Hacker News source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
from research_collector.config import Config


class HackerNewsSource:
    """Hacker News technology discussions source."""
    
    def __init__(self, config: Config):
        """Initialize Hacker News source."""
        self.config = config
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Hacker News for discussions."""
        try:
            # Get recent stories
            stories_url = f"{self.base_url}/newstories.json"
            response = requests.get(stories_url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()
            
            # Limit to recent stories for performance
            story_ids = story_ids[:100]  # Increased from 50 to 100
            
            results = []
            for story_id in story_ids:
                try:
                    # Get story details
                    story_url = f"{self.base_url}/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=5)
                    story_response.raise_for_status()
                    
                    story = story_response.json()
                    
                    # Filter by topic relevance (simple keyword matching)
                    title = story.get("title", "").lower()
                    text = story.get("text", "").lower()
                    topic_lower = topic.lower()
                    
                    # Check if topic is mentioned in title or text
                    if topic_lower not in title and topic_lower not in text:
                        continue
                    
                    # Convert timestamp to datetime
                    timestamp = story.get("time", 0)
                    story_date = datetime.fromtimestamp(timestamp)
                    
                    # Filter by date range
                    if story_date < from_date or story_date > to_date:
                        continue
                    
                    formatted_result = {
                        "id": f"hn_{story_id}",
                        "title": story.get("title", "No title"),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "author": story.get("by", "Unknown"),
                        "published_date": story_date.isoformat(),
                        "citations": 0,
                        "upvotes": story.get("score", 0),
                        "downloads": 0,
                        "comments": story.get("descendants", 0),
                        "content": text[:500] if text else title,
                        "metadata": {
                            "points": story.get("score", 0),
                            "comment_count": story.get("descendants", 0),
                            "type": story.get("type", "story")
                        }
                    }
                    
                    results.append(formatted_result)
                    
                except requests.exceptions.RequestException:
                    continue
                except Exception:
                    continue
            
            return results[:20]  # Limit results for educational purposes
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Hacker News data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Hacker News data: {e}")
            return []