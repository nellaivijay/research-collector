"""Stack Overflow source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
from research_collector.config import Config


class StackOverflowSource:
    """Stack Overflow technical Q&A source."""
    
    def __init__(self, config: Config):
        """Initialize Stack Overflow source."""
        self.config = config
        self.api_key = config.get_api_key("stackexchange")
        self.base_url = "https://api.stackexchange.com/2.3"
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Stack Overflow for questions and answers."""
        try:
            # Search for questions
            search_url = f"{self.base_url}/search/advanced"
            
            # Convert dates to Unix timestamps
            from_timestamp = int(from_date.timestamp())
            to_timestamp = int(to_date.timestamp())
            
            params = {
                "order": "desc",
                "sort": "relevance",
                "q": topic,
                "site": "stackoverflow",
                "filter": "withbody",  # Include question bodies
                "pagesize": 20,
                "fromdate": from_timestamp,
                "todate": to_timestamp
            }
            
            # Add API key if available for higher rate limits
            if self.api_key:
                params["key"] = self.api_key
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            questions = data.get("items", [])
            
            results = []
            for question in questions:
                try:
                    # Convert timestamp to datetime
                    timestamp = question.get("creation_date", 0)
                    question_date = datetime.fromtimestamp(timestamp)
                    
                    # Get owner info
                    owner = question.get("owner", {})
                    author = owner.get("display_name", "Unknown")
                    
                    # Get tags
                    tags = question.get("tags", [])
                    
                    # Get answer count and score
                    answer_count = question.get("answer_count", 0)
                    score = question.get("score", 0)
                    
                    # Get question body or excerpt
                    body = question.get("body_markdown", "")
                    content = body[:500] if body else question.get("title", "")
                    
                    formatted_result = {
                        "id": f"so_{question.get('question_id', 'unknown')}",
                        "title": question.get("title", "No title"),
                        "url": question.get("link", ""),
                        "author": author,
                        "published_date": question_date.isoformat(),
                        "citations": 0,
                        "upvotes": score,
                        "downloads": 0,
                        "comments": question.get("comment_count", 0),
                        "content": content,
                        "metadata": {
                            "tags": tags,
                            "answer_count": answer_count,
                            "score": score,
                            "view_count": question.get("view_count", 0),
                            "is_answered": question.get("is_answered", False)
                        }
                    }
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Stack Overflow data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Stack Overflow data: {e}")
            return []