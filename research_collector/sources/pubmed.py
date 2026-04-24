"""PubMed source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
import urllib.parse
from research_collector.config import Config


class PubMedSource:
    """PubMed medical literature source."""
    
    def __init__(self, config: Config):
        """
        Initialize PubMed source.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.api_key = config.get_api_key("pubmed")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = config.get_api_key("crossref") or "education@example.com"  # Using crossref field for email
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed for research articles.
        
        Args:
            topic: Research topic
            from_date: Start date
            to_date: End date
            depth: Search depth
        
        Returns:
            List of research articles
        """
        try:
            # Step 1: Search for article IDs
            search_url = f"{self.base_url}/esearch.fcgi"
            
            # Format dates for PubMed (YYYY/MM/DD)
            from_date_str = from_date.strftime("%Y/%m/%d")
            to_date_str = to_date.strftime("%Y/%m/%d")
            
            # Build search query with date range
            query = f'{topic} AND ("{from_date_str}"[Date - Publication] : "{to_date_str}"[Date - Publication])'
            
            params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": 20  # Limit results for educational purposes
            }
            
            # Add API key if available for higher rate limits
            if self.api_key:
                params["api_key"] = self.api_key
            
            # Add email for NCBI (required without API key)
            if not self.api_key:
                params["tool"] = "research-collector"
                params["email"] = self.email
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            search_data = response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Step 2: Fetch details for found articles
            summaries_url = f"{self.base_url}/esummary.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
                "retmax": 20
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            else:
                params["tool"] = "research-collector"
                params["email"] = self.email
            
            response = requests.get(summaries_url, params=params, timeout=10)
            response.raise_for_status()
            
            summaries_data = response.json()
            results = summaries_data.get("result", {})
            
            # Convert to our format
            formatted_results = []
            for pubmed_id in id_list:
                if pubmed_id == "uids":
                    continue
                    
                article = results.get(pubmed_id, {})
                if not article:
                    continue
                
                # Extract authors
                authors = article.get("authors", [])
                author_list = ", ".join([a.get("name", "Unknown") for a in authors[:3]])
                if len(authors) > 3:
                    author_list += " et al."
                
                # Extract publication date
                pub_date = article.get("pubdate", "Unknown")
                
                formatted_result = {
                    "id": f"pubmed_{pubmed_id}",
                    "title": article.get("title", "No title"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                    "author": author_list,
                    "published_date": pub_date,
                    "citations": 0,  # PubMed doesn't provide citation counts in basic API
                    "upvotes": 0,
                    "downloads": 0,
                    "comments": 0,
                    "content": self._extract_abstract(article),
                    "metadata": {
                        "journal": article.get("source", "Unknown"),
                        "pubmed_id": pubmed_id,
                        "year": pub_date[:4] if pub_date != "Unknown" else "Unknown"
                    }
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PubMed data: {e}")
            return []
        except Exception as e:
            print(f"Error processing PubMed data: {e}")
            return []
    
    def _extract_abstract(self, article: Dict) -> str:
        """Extract abstract from article data."""
        # Try to get abstract from article data
        # Note: Basic esummary doesn't include abstracts, would need efetch
        # For educational purposes, we'll return a placeholder
        return "Abstract not available in basic API view. Use PubMed link for full details."