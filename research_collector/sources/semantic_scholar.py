"""Semantic Scholar source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
from research_collector.config import Config
from research_collector.utils import retry_on_failure


class SemanticScholarSource:
    """Semantic Scholar academic papers source."""
    
    def __init__(self, config: Config):
        """Initialize Semantic Scholar source."""
        self.config = config
        self.api_key = config.get_api_key("semantic_scholar")
        self.base_url = "https://api.semanticscholar.org"
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for papers."""
        try:
            # Semantic Scholar Graph API
            search_url = f"{self.base_url}/graph/v1/paper/search"
            
            # Format dates for Semantic Scholar (YYYY-MM-DD)
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            params = {
                "query": topic,
                "fields": "title,authors,year,citationCount,url,abstract,publicationDate,publicationVenue,journal,fieldsOfStudy,influentialCitationCount,openAccessPdf,publicationTypes",
                "limit": 200,  # Increased from 100 to 200 for better coverage
                "minCitationDate": from_date_str,
                "maxCitationDate": to_date_str
            }
            
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get("data", [])
            
            results = []
            for paper in papers:
                try:
                    # Extract authors
                    authors = paper.get("authors", [])
                    author_list = ", ".join([a.get("name", "Unknown") for a in authors[:3]])
                    if len(authors) > 3:
                        author_list += " et al."
                    
                    # Extract publication date
                    pub_date = paper.get("publicationDate") or paper.get("year", "Unknown")
                    
                    # Extract additional citation metrics
                    citation_count = paper.get("citationCount", 0)
                    influential_citation_count = paper.get("influentialCitationCount", 0)
                    
                    # Extract fields of study
                    fields_of_study = paper.get("fieldsOfStudy", [])
                    
                    # Extract open access info
                    open_access_pdf = paper.get("openAccessPdf", {})
                    has_open_access = bool(open_access_pdf)
                    
                    # Extract publication types
                    publication_types = paper.get("publicationTypes", [])
                    
                    # Calculate temporal features
                    try:
                        year = paper.get("year")
                        if year:
                            days_since_publication = (datetime.now().year - year) * 365
                        else:
                            days_since_publication = 0
                    except:
                        days_since_publication = 0
                    
                    formatted_result = {
                        "id": f"semantic_{paper.get('paperId', 'unknown')}",
                        "title": paper.get("title", "No title"),
                        "url": paper.get("url", ""),
                        "author": author_list,
                        "published_date": pub_date,
                        "citations": citation_count,
                        "upvotes": 0,
                        "downloads": 0,
                        "comments": 0,
                        "content": self._extract_abstract(paper),
                        "metadata": {
                            "year": paper.get("year", "Unknown"),
                            "venue": paper.get("publicationVenue", ""),
                            "journal": paper.get("journal", {}).get("name", ""),
                            "paperId": paper.get("paperId", ""),
                            "citation_count": citation_count,
                            "influential_citation_count": influential_citation_count,
                            "citation_velocity": influential_citation_count / max(days_since_publication / 365, 1) if days_since_publication > 0 else 0,
                            "fields_of_study": fields_of_study,
                            "field_count": len(fields_of_study),
                            "has_open_access": has_open_access,
                            "open_access_pdf_url": open_access_pdf.get("url", "") if open_access_pdf else "",
                            "publication_types": publication_types,
                            "is_journal_article": "JournalArticle" in publication_types,
                            "is_conference_paper": "Conference" in publication_types,
                            "is_preprint": "Preprint" in publication_types,
                            "days_since_publication": days_since_publication,
                            "abstract_length": len(self._extract_abstract(paper))
                        }
                    }
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Semantic Scholar data: {e}")
            return []
        except Exception as e:
            print(f"Error processing Semantic Scholar data: {e}")
            return []
    
    def _extract_abstract(self, paper: Dict) -> str:
        """Extract abstract from Semantic Scholar paper."""
        abstract = paper.get("abstract")
        if abstract:
            return abstract[:1000] if abstract else ""
        return "Abstract not available in API response."