"""Full-text extraction from research papers."""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict


class FullTextExtractor:
    """Extract full text from research paper URLs."""
    
    def __init__(self, timeout: int = 25, user_agent: str = "research-collector/1.0"):
        """
        Initialize the full-text extractor.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: User-Agent string for requests
        """
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
    
    def extract_arxiv_text(self, arxiv_url: str) -> str:
        """
        Extract full text from arXiv paper.
        
        Args:
            arxiv_url: arXiv paper URL (e.g., https://arxiv.org/abs/2301.00001)
            
        Returns:
            Extracted text content (max 18000 characters)
        """
        try:
            # Convert abs URL to HTML URL
            html_url = arxiv_url.replace("/abs/", "/html/")
            
            response = requests.get(html_url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return ""
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Remove script, style, nav, header, footer elements
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            
            # Try to find main content
            main = soup.find("article") or soup.find("main") or soup.body or soup
            
            if main:
                text = main.get_text(separator=" ", strip=True)
                # Clean up extra whitespace
                text = re.sub(r"\s+", " ", text)
                # Limit length to avoid memory issues
                return text[:18000]
            
            return ""
            
        except Exception as e:
            print(f"Error extracting arXiv text from {arxiv_url}: {e}")
            return ""
    
    def extract_figure_captions(self, arxiv_url: str, max_figures: int = 20) -> list:
        """
        Extract figure and table captions from arXiv paper.
        
        Args:
            arxiv_url: arXiv paper URL
            max_figures: Maximum number of captions to extract
            
        Returns:
            List of tuples (type, caption) where type is "Figure" or "Table"
        """
        captions = []
        
        try:
            html_url = arxiv_url.replace("/abs/", "/html/")
            response = requests.get(html_url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return captions
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extract figure captions
            for fig in soup.find_all("figure")[:max_figures]:
                cap = fig.find("figcaption")
                if cap:
                    text = cap.get_text(" ", strip=True)
                    text = re.sub(r"\s+", " ", text)
                    if len(text) > 20:
                        captions.append(("Figure", text[:350]))
            
            # Extract table captions
            for cap_tag in soup.find_all("caption")[:max_figures // 2]:
                text = cap_tag.get_text(" ", strip=True)
                text = re.sub(r"\s+", " ", text)
                if len(text) > 20:
                    captions.append(("Table", text[:350]))
            
        except Exception as e:
            print(f"Error extracting captions from {arxiv_url}: {e}")
        
        return captions[:max_figures]
    
    def enhance_paper_content(self, paper: Dict) -> Dict:
        """
        Enhance paper dictionary with full-text and captions.
        
        Args:
            paper: Paper dictionary with at least a URL
            
        Returns:
            Enhanced paper dictionary with additional fields
        """
        url = paper.get("url", "")
        
        # Only extract from arXiv URLs for now
        if "arxiv.org" in url:
            # Extract full text
            full_text = self.extract_arxiv_text(url)
            if full_text:
                paper["full_text"] = full_text
            
            # Extract figure captions
            captions = self.extract_figure_captions(url)
            if captions:
                paper["figure_captions"] = captions
        
        return paper


def enhance_results_with_fulltext(results: list, enable_fulltext: bool = True) -> list:
    """
    Enhance multiple results with full-text extraction.
    
    Args:
        results: List of paper dictionaries
        enable_fulltext: Whether to extract full text (resource-intensive)
        
    Returns:
        Enhanced results list
    """
    if not enable_fulltext:
        return results
    
    extractor = FullTextExtractor()
    enhanced_results = []
    
    for paper in results:
        try:
            enhanced = extractor.enhance_paper_content(paper)
            enhanced_results.append(enhanced)
        except Exception as e:
            print(f"Error enhancing paper: {e}")
            enhanced_results.append(paper)  # Keep original if enhancement fails
    
    return enhanced_results