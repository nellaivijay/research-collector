"""Stack Overflow source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
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
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search Stack Overflow for questions and answers."""
        try:
            # Search for questions
            search_url = f"{self.base_url}/search/advanced"
            
            # Convert dates to Unix timestamps
            from_timestamp = int(from_date.timestamp())
            to_timestamp = int(to_date.timestamp())
            
            # Stack Exchange API doesn't support OR queries in q parameter
            # Use first keyword only if OR is present
            search_query = topic.split(" OR ")[0].strip() if " OR " in topic else topic
            
            params = {
                "order": "desc",
                "sort": "relevance",
                "q": search_query,
                "site": "stackoverflow",
                "filter": "withbody",  # Include question bodies
                "pagesize": 200,  # Increased from 100 to 200 for better coverage
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
                    content = body[:1000] if body else question.get("title", "")
                    
                    # Extract additional metadata
                    owner_reputation = owner.get("reputation", 0)
                    owner_user_type = owner.get("user_type", "")
                    accepted_answer_id = question.get("accepted_answer_id")
                    favorite_count = question.get("favorite_count", 0)
                    closed_date = question.get("closed_date")
                    last_activity_date = question.get("last_activity_date")
                    last_edit_date = question.get("last_edit_date")
                    
                    # Calculate temporal features
                    try:
                        days_since_creation = (datetime.now(question_date.tzinfo) - question_date).days if question_date.tzinfo else 0
                        if last_activity_date:
                            last_activity = datetime.fromtimestamp(last_activity_date)
                            days_since_activity = (datetime.now(last_activity.tzinfo) - last_activity).days if last_activity.tzinfo else 0
                        else:
                            days_since_activity = 0
                    except:
                        days_since_creation = 0
                        days_since_activity = 0
                    
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
                            "is_answered": question.get("is_answered", False),
                            "has_accepted_answer": bool(accepted_answer_id),
                            "accepted_answer_id": accepted_answer_id,
                            "favorite_count": favorite_count,
                            "is_favorited": favorite_count > 0,
                            "owner_reputation": owner_reputation,
                            "owner_user_type": owner_user_type,
                            "owner_user_id": owner.get("user_id"),
                            "closed_date": closed_date,
                            "is_closed": bool(closed_date),
                            "last_activity_date": last_activity_date,
                            "last_edit_date": last_edit_date,
                            "is_edited": bool(last_edit_date),
                            "days_since_creation": days_since_creation,
                            "days_since_activity": days_since_activity,
                            "content_length": len(content),
                            "has_code": "<code>" in content or "```" in content,
                            "question_id": question.get("question_id"),
                            "community_owned": question.get("community_owned_date") is not None
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