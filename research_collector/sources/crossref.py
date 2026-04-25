"""Crossref source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
from research_collector.config import Config
from research_collector.utils import retry_on_failure


class CrossrefSource:
    """Crossref academic metadata source."""
    
    def __init__(self, config: Config):
        """Initialize Crossref source."""
        self.config = config
        self.api_key = config.get_api_key("crossref") or "mailto:education@example.com"
        self.base_url = "https://api.crossref.org"
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Crossref for academic papers."""
        try:
            # Crossref API for searching works
            search_url = f"{self.base_url}/works"
            
            # Format dates for Crossref (YYYY-MM-DD)
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            # Build query with date range
            query = f"{topic}"
            
            params = {
                "query": query,
                "filter": f"from-pub-date:{from_date_str},until-pub-date:{to_date_str}",
                "rows": 100,  # Increased from 20 to 100
                "sort": "published",
                "order": "desc",
                "mailto": self.api_key
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", {})
            
            results = []
            for item in items:
                try:
                    # Extract authors
                    authors = item.get("author", [])
                    author_list = ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in authors[:3]])
                    if len(authors) > 3:
                        author_list += " et al."
                    
                    # Extract publication date
                    pub_date = item.get("published", {}).get("date-parts", ["Unknown"])[0]
                    if isinstance(pub_date, list):
                        pub_date_str = f"{pub_date[0]}-{pub_date[1]:02d}-{pub_date[2]:02d}" if len(pub_date) >= 3 else str(pub_date[0])
                    else:
                        pub_date_str = str(pub_date)
                    
                    formatted_result = {
                        "id": f"crossref_{item.get('doi', 'unknown').replace('/', '_')}",
                        "title": item.get("title", "No title"),
                        "url": item.get("URL", ""),
                        "author": author_list,
                        "published_date": pub_date_str,
                        "citations": item.get("is-referenced-by-count", 0),
                        "upvotes": 0,
                        "downloads": 0,
                        "comments": 0,
                        "content": self._extract_abstract(item),
                        "metadata": {
                            "doi": item.get("DOI", ""),
                            "type": item.get("type", "journal-article"),
                            "publisher": item.get("publisher", ""),
                            "journal": item.get("container-title", ""),
                            "year": pub_date_str[:4] if pub_date_str != "Unknown" else "Unknown"
                        }
                    }
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Crossref data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Crossref data: {e}")
            return []
    
    def _extract_abstract(self, item: Dict) -> str:
        """Extract abstract from Crossref item."""
        abstract = item.get("abstract", "")
        if abstract:
            # Crossref sometimes returns abstract with HTML-like markup
            import re
            abstract = re.sub(r'<[^>]+>', '', abstract)
            return abstract[:500] if abstract else ""
        return "Abstract not available in API response."