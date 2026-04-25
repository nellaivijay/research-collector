"""arXiv source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
import feedparser
from research_collector.config import Config


class ArxivSource:
    """arXiv preprint server source."""
    
    def __init__(self, config: Config):
        """Initialize arXiv source."""
        self.config = config
        self.base_url = "http://export.arxiv.org/api/query"
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search arXiv for preprints."""
        try:
            # Format dates for arXiv search (YYYYMMDD)
            from_date_str = from_date.strftime("%Y%m%d")
            to_date_str = to_date.strftime("%Y%m%d")
            
            # Build search query
            query = f'all:{topic} AND submittedDate:[{from_date_str}0000 TO {to_date_str}2359]'
            
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 100,  # Increased from 20 to 100
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response using feedparser
            feed = feedparser.parse(response.content)
            
            formatted_results = []
            for entry in feed.entries:
                # Extract arXiv ID from URL
                arxiv_id = entry.id.split("/")[-1]
                
                # Extract authors
                authors = []
                for author in entry.get("authors", []):
                    authors.append(author.get("name", "Unknown"))
                author_str = ", ".join(authors[:10])
                if len(authors) > 10:
                    author_str += " et al."
                
                # Extract publication date
                published_date = entry.get("published", "")
                if published_date:
                    try:
                        pub_dt = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
                        published_date = pub_dt.strftime("%Y-%m-%d")
                    except:
                        published_date = published_date[:10]
                
                # Extract categories
                categories = [tag.term for tag in entry.get("tags", []) if tag.term.startswith("cs.") or tag.term.startswith("stat.") or tag.term.startswith("math.")]
                
                # Extract primary category
                primary_category = entry.get("arxiv_primary_category", {}).get("term", "Unknown")
                
                # Extract abstract
                abstract = entry.get("summary", "").replace("\n", " ").strip()
                
                # Calculate temporal features
                try:
                    pub_dt = datetime.fromisoformat(entry.get("published", "").replace("Z", "+00:00"))
                    days_since_submission = (datetime.now(pub_dt.tzinfo) - pub_dt).days if pub_dt.tzinfo else 0
                except:
                    days_since_submission = 0
                
                formatted_result = {
                    "id": f"arxiv_{arxiv_id}",
                    "title": entry.get("title", "No title").replace("\n", " "),
                    "url": entry.get("link", ""),
                    "author": author_str or "Unknown",
                    "published_date": published_date or "Unknown",
                    "citations": 0,  # arXiv doesn't provide citation counts
                    "upvotes": 0,
                    "downloads": 0,
                    "comments": 0,
                    "content": abstract,
                    "metadata": {
                        "arxiv_id": arxiv_id,
                        "primary_category": primary_category,
                        "categories": categories,
                        "category_count": len(categories),
                        "year": published_date[:4] if published_date and len(published_date) >= 4 else "Unknown",
                        "abstract_length": len(abstract),
                        "doi": entry.get("arxiv_doi", ""),
                        "has_doi": bool(entry.get("arxiv_doi", "")),
                        "journal_ref": entry.get("arxiv_journal_ref", ""),
                        "is_published": bool(entry.get("arxiv_journal_ref", "")),
                        "days_since_submission": days_since_submission,
                        "comment": entry.get("arxiv_comment", ""),
                        "has_comment": bool(entry.get("arxiv_comment", ""))
                    }
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching arXiv data: {e}")
            return []
        except Exception as e:
            print(f"Error processing arXiv data: {e}")
            return []
