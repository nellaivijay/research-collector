"""INSPIRE-HEP source for academic papers."""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from research_collector.config import Config


class INSPIREHEPSource:
    """Source for INSPIRE-HEP high-energy physics literature database."""
    
    def __init__(self, config: Config):
        """
        Initialize INSPIRE-HEP source.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.base_url = "https://inspirehep.net/api/literature"
        self.headers = {
            "User-Agent": "research-collector/1.0 (mailto:education@example.com)",
            "Accept": "application/json"
        }
        self.timeout = 30
    
    def search(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Search INSPIRE-HEP for papers on a topic.
        
        Args:
            topic: Research topic
            from_date: Start date
            to_date: End date
            depth: Search depth (quick, default, deep)
            max_results: Maximum number of results to return
            
        Returns:
            List of paper dictionaries
        """
        try:
            # Calculate days for date filter
            days = (to_date - from_date).days
            
            # Build query
            query = f'("{topic}") AND date>{days}d'
            
            # Determine size based on depth
            size = self._get_size_for_depth(depth, max_results)
            
            # Build API parameters
            params = {
                "q": query,
                "sort": "mostrecent",
                "size": size,
                "page": 1,
                "fields": "titles,abstracts,authors,arxiv_eprints,publication_info,citation_count,doi"
            }
            
            # Make API request
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse results
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])
            
            # Format results
            formatted_results = []
            for hit in hits[:size]:
                formatted = self._format_hit(hit)
                if formatted:
                    formatted_results.append(formatted)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching INSPIRE-HEP: {e}")
            return []
    
    def _get_size_for_depth(self, depth: str, max_results: Optional[int] = None) -> int:
        """Determine result size based on search depth."""
        if max_results:
            return min(max_results, 100)
        
        depth_sizes = {
            "quick": 10,
            "default": 20,
            "deep": 50
        }
        return depth_sizes.get(depth, 20)
    
    def _format_hit(self, hit: Dict) -> Optional[Dict]:
        """Format INSPIRE-HEP hit into standard format."""
        try:
            # Extract title
            titles = hit.get("titles", [])
            title = titles[0].get("title", "") if titles else ""
            
            # Extract abstract
            abstracts = hit.get("abstracts", [])
            abstract = abstracts[0].get("value", "") if abstracts else ""
            
            # Extract authors
            authors = hit.get("authors", [])
            author_names = []
            for author in authors[:10]:  # Limit to first 10 authors
                full_name = author.get("full_name", "")
                if full_name:
                    author_names.append(full_name)
            authors_str = ", ".join(author_names)
            
            # Extract arXiv ID
            arxiv_eprints = hit.get("arxiv_eprints", [])
            arxiv_id = ""
            arxiv_url = ""
            if arxiv_eprints:
                arxiv_id = arxiv_eprints[0].get("value", "")
                if arxiv_id:
                    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            
            # Extract DOI
            dois = hit.get("dois", [])
            doi = dois[0].get("value", "") if dois else ""
            
            # Extract citation count
            citation_count = hit.get("citation_count", 0)
            
            # Extract publication info for date
            pub_info = hit.get("publication_info", [])
            pub_date = ""
            if pub_info:
                year = pub_info[0].get("year", "")
                if year:
                    pub_date = f"{year}-01-01"
            
            return {
                "title": title,
                "content": abstract,
                "authors": authors_str,
                "url": arxiv_url or f"https://inspirehep.net/literature/{hit.get('id', '')}",
                "published_date": pub_date,
                "source": "inspire_hep",
                "citations": citation_count,
                "metadata": {
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                    "inspire_id": str(hit.get("id", "")),
                    "content_type": "preprint" if arxiv_id else "article"
                }
            }
            
        except Exception as e:
            print(f"Error formatting INSPIRE-HEP hit: {e}")
            return None