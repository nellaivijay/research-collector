"""PubMed source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
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
        depth: str = "default",
        max_results: Optional[int] = None
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
                "retmax": 200  # Increased from 100 to 200 for better coverage
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
            
            # Step 2: Fetch full details using efetch (includes abstracts)
            fetch_url = f"{self.base_url}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml",
                "retmax": 200  # Increased from 100 to 200 for better coverage
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            else:
                params["tool"] = "research-collector"
                params["email"] = self.email
            
            response = requests.get(fetch_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            # Convert to our format
            formatted_results = []
            for article in root.findall(".//PubmedArticle"):
                medline_citation = article.find("MedlineCitation")
                if medline_citation is None:
                    continue
                    
                pubmed_data = medline_citation.find("PubmedData")
                if pubmed_data is None:
                    continue
                    
                article_id = pubmed_data.find(".//PMID")
                if article_id is None:
                    continue
                    
                pubmed_id = article_id.text
                
                # Get article info
                article_info = medline_citation.find("Article")
                if article_info is None:
                    continue
                
                # Extract title
                article_title = article_info.find(".//ArticleTitle")
                title = article_title.text if article_title is not None else "No title"
                
                # Extract abstract
                abstract_text = article_info.find(".//AbstractText")
                abstract = abstract_text.text if abstract_text is not None else "No abstract available"
                
                # Extract authors
                authors = article_info.findall(".//Author")
                author_list = []
                for author in authors[:10]:
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None and fore_name is not None:
                        author_list.append(f"{fore_name.text} {last_name.text}")
                    elif last_name is not None:
                        author_list.append(last_name.text)
                
                author_str = ", ".join(author_list)
                if len(authors) > 10:
                    author_str += " et al."
                
                # Extract publication date
                pub_date_elem = article_info.find(".//PubDate")
                pub_date = "Unknown"
                if pub_date_elem is not None:
                    year = pub_date_elem.find("Year")
                    month = pub_date_elem.find("Month")
                    day = pub_date_elem.find("Day")
                    if year is not None and year.text:
                        pub_date = year.text
                        if month is not None and month.text:
                            month_text = month.text.zfill(2) if len(month.text) == 1 else month.text
                            pub_date += f"-{month_text}"
                            if day is not None and day.text:
                                day_text = day.text.zfill(2) if len(day.text) == 1 else day.text
                                pub_date += f"-{day_text}"
                
                # Extract journal
                journal_elem = article_info.find(".//Journal/Title")
                journal = journal_elem.text if journal_elem is not None else "Unknown"
                
                # Extract DOI if available
                doi = ""
                for article_id in pubmed_data.findall(".//ArticleId"):
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break
                
                # Extract MeSH terms
                mesh_terms = []
                mesh_heading_list = medline_citation.find(".//MeshHeadingList")
                if mesh_heading_list is not None:
                    for mesh in mesh_heading_list.findall("MeshHeading"):
                        descriptor = mesh.find("DescriptorName")
                        if descriptor is not None:
                            mesh_terms.append(descriptor.text)
                
                # Extract publication type
                pub_types = []
                pub_type_list = article_info.find(".//PublicationTypeList")
                if pub_type_list is not None:
                    for pub_type in pub_type_list.findall("PublicationType"):
                        if pub_type is not None:
                            pub_types.append(pub_type.text)
                
                formatted_result = {
                    "id": f"pubmed_{pubmed_id}",
                    "title": title,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                    "author": author_str or "Unknown",
                    "published_date": pub_date,
                    "citations": 0,  # PubMed doesn't provide citation counts
                    "upvotes": 0,
                    "downloads": 0,
                    "comments": 0,
                    "content": abstract,
                    "metadata": {
                        "journal": journal,
                        "pubmed_id": pubmed_id,
                        "year": pub_date[:4] if pub_date != "Unknown" else "Unknown",
                        "doi": doi,
                        "mesh_terms": mesh_terms,
                        "publication_types": pub_types,
                        "abstract_length": len(abstract),
                        "has_doi": bool(doi)
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
    
