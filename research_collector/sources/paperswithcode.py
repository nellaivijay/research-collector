"""Papers With Code source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from research_collector.config import Config
from research_collector.utils import retry_on_failure


class PapersWithCodeSource:
    """Papers With Code ML papers source."""
    
    def __init__(self, config: Config):
        """Initialize Papers With Code source."""
        self.config = config
        self.base_url = "https://paperswithcode.com/api/v1"
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    def search(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search Papers With Code for ML papers."""
        try:
            # Papers With Code API - use first keyword only if OR is present
            # Papers With Code API doesn't support complex OR queries
            search_query = topic.split(" OR ")[0].strip() if " OR " in topic else topic
            
            # Papers With Code API
            search_url = f"{self.base_url}/papers/"
            
            # Format dates for Papers With Code (YYYY-MM-DD)
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            params = {
                "q": search_query,
                "fields": "title,authors,publishedDate,repositoryUrl,stars,citationCount,abstract",
                "filter": f"published_date:{from_date_str}:{to_date_str}",
                "limit": 200  # Increased from 100 to 200 for better coverage
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Check if response is valid JSON (Papers With Code API might be down/changed)
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print(f"Papers With Code API returned HTML instead of JSON - API may be unavailable or changed")
                print(f"Status code: {response.status_code}")
                return []
                
            try:
                data = response.json()
            except ValueError as e:
                print(f"Error parsing Papers With Code JSON response: {e}")
                print(f"Response text: {response.text[:500]}")
                return []
            
            results = data.get("results", [])
            
            formatted_results = []
            for item in results:
                try:
                    # Extract authors
                    authors = item.get("authors", [])
                    author_list = ", ".join([a.get("name", "Unknown") for a in authors[:3]])
                    if len(authors) > 3:
                        author_list += " et al."
                    
                    # Extract publication date
                    pub_date = item.get("publishedDate", "Unknown")
                    
                    formatted_result = {
                        "id": f"pwc_{item.get('id', 'unknown')}",
                        "title": item.get("title", "No title"),
                        "url": item.get("url", ""),
                        "author": author_list,
                        "published_date": pub_date,
                        "citations": item.get("citationCount", 0),
                        "upvotes": 0,
                        "downloads": 0,
                        "comments": 0,
                        "content": self._extract_abstract(item),
                        "metadata": {
                            "stars": item.get("stars", 0),
                            "repositoryUrl": item.get("repositoryUrl", ""),
                            "framework": item.get("framework", ""),
                            "year": pub_date[:4] if pub_date != "Unknown" else "Unknown"
                        }
                    }
                    
                    formatted_results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Papers With Code data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Papers With Code data: {e}")
            return []
    
    def _extract_abstract(self, item: Dict) -> str:
        """Extract abstract from Papers With Code item."""
        abstract = item.get("abstract")
        if abstract:
            return abstract[:500] if abstract else ""
        return "Abstract not available in API response."