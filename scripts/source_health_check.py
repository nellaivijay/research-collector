#!/usr/bin/env python3
"""
Comprehensive source health check script for Research-Collector.

Checks:
- API availability
- API key configuration
- API key validity
- Rate limiting/blocking status
- Response times
- Error handling
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SourceHealth:
    """Health check result for a source."""
    name: str
    status: str  # healthy, degraded, unhealthy, unknown
    api_available: bool
    api_key_configured: bool
    api_key_valid: bool
    response_time_ms: float
    error_message: str
    details: Dict[str, Any]


class SourceHealthChecker:
    """Check health of all data sources."""
    
    def __init__(self):
        """Initialize health checker."""
        self.sources = self._get_sources_config()
        self.api_keys = self._load_api_keys()
    
    def _get_sources_config(self) -> List[Dict[str, Any]]:
        """Get source configuration."""
        return [
            {
                "name": "PubMed",
                "api_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                "test_params": {"db": "pubmed", "term": "machine learning", "retmax": "1"},
                "api_key_env": "PUBMED_API_KEY",
                "requires_key": False,
                "category": "academic"
            },
            {
                "name": "Crossref",
                "api_url": "https://api.crossref.org/works",
                "test_params": {"query": "machine learning", "rows": 1},
                "api_key_env": "CROSSREF_API_KEY",
                "requires_key": False,
                "category": "academic"
            },
            {
                "name": "Semantic Scholar",
                "api_url": "https://api.semanticscholar.org/graph/v1/paper/search",
                "test_params": {"query": "machine learning", "limit": 1},
                "api_key_env": "SEMANTIC_SCHOLAR_API_KEY",
                "requires_key": False,
                "category": "academic"
            },
            {
                "name": "Papers with Code",
                "api_url": "https://paperswithcode.com/api/v1/papers",
                "test_params": {},
                "api_key_env": None,
                "requires_key": False,
                "category": "academic"
            },
            {
                "name": "arXiv",
                "api_url": "http://export.arxiv.org/api/query",
                "test_params": {"search_query": "all:machine learning", "start": 0, "max_results": 1},
                "api_key_env": None,
                "requires_key": False,
                "category": "academic"
            },
            {
                "name": "GitHub",
                "api_url": "https://api.github.com/search/repositories",
                "test_params": {"q": "machine learning", "per_page": 1},
                "api_key_env": "GITHUB_TOKEN",
                "requires_key": False,
                "category": "professional"
            },
            {
                "name": "Stack Overflow",
                "api_url": "https://api.stackexchange.com/2.3/search/advanced",
                "test_params": {"order": "desc", "sort": "activity", "accepted": True, "answers": 1, "tagged": "machine-learning", "pagesize": 1},
                "api_key_env": "STACKEXCHANGE_API_KEY",
                "requires_key": False,
                "category": "professional"
            },
            {
                "name": "Kaggle",
                "api_url": "https://www.kaggle.com/api/v1/datasets/list",
                "test_params": {},
                "api_key_env": "KAGGLE_USERNAME",  # Kaggle uses username/key pair
                "requires_key": True,
                "category": "professional"
            },
            {
                "name": "Reddit",
                "api_url": "https://www.reddit.com/r/MachineLearning/hot.json",
                "test_params": {},
                "api_key_env": "REDDIT_CLIENT_ID",
                "requires_key": True,
                "category": "social"
            },
            {
                "name": "Hacker News",
                "api_url": "https://hacker-news.firebaseio.com/v0/topstories.json",
                "test_params": {},
                "api_key_env": None,
                "requires_key": False,
                "category": "social"
            },
            {
                "name": "GDELT",
                "api_url": "https://api.gdeltproject.org/api/v2/doc/doc",
                "test_params": {},
                "api_key_env": None,
                "requires_key": False,
                "category": "news"
            },
            {
                "name": "Medium",
                "api_url": "https://towardsdatascience.com/feed",
                "test_params": {},
                "api_key_env": None,
                "requires_key": False,
                "category": "news",
                "skip_health_check": True  # Skip due to inconsistent access
            }
        ]
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment."""
        keys = {
            "PUBMED_API_KEY": os.getenv("PUBMED_API_KEY"),
            "CROSSREF_API_KEY": os.getenv("CROSSREF_API_KEY"),
            "SEMANTIC_SCHOLAR_API_KEY": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
            "NEWSAPI_API_KEY": os.getenv("NEWSAPI_API_KEY"),
            "STACKEXCHANGE_API_KEY": os.getenv("STACKEXCHANGE_API_KEY"),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
            "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
            "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
            "REDDIT_USER_AGENT": os.getenv("REDDIT_USER_AGENT"),
            "KAGGLE_USERNAME": os.getenv("KAGGLE_USERNAME"),
            "KAGGLE_KEY": os.getenv("KAGGLE_KEY"),
        }
        return {k: v for k, v in keys.items() if v is not None}
    
    def check_source(self, source_config: Dict[str, Any]) -> SourceHealth:
        """Check health of a single source."""
        name = source_config["name"]
        api_url = source_config["api_url"]
        test_params = source_config["test_params"]
        api_key_env = source_config["api_key_env"]
        requires_key = source_config["requires_key"]
        skip_health_check = source_config.get("skip_health_check", False)
        
        # Initialize health result
        health = SourceHealth(
            name=name,
            status="unknown",
            api_available=False,
            api_key_configured=False,
            api_key_valid=False,
            response_time_ms=0.0,
            error_message="",
            details={"category": source_config.get("category", "unknown")}
        )
        
        # Skip health check if flagged
        if skip_health_check:
            health.status = "unknown"
            health.api_available = True  # Assume available
            health.api_key_valid = True
            health.error_message = "Health check skipped - source marked as unreliable"
            health.details["skipped"] = True
            health.details["reason"] = "Inconsistent access due to anti-scraping measures"
            return health
        
        # Check API key configuration
        if api_key_env:
            api_key = self.api_keys.get(api_key_env)
            health.api_key_configured = api_key is not None and len(api_key) > 0
            
            if requires_key and not health.api_key_configured:
                health.status = "unhealthy"
                health.error_message = f"API key not configured: {api_key_env}"
                health.details["api_key_env"] = api_key_env
                return health
            
            if health.api_key_configured:
                health.details["api_key_configured"] = True
                health.details["api_key_length"] = len(api_key)
        
        # Check API availability
        try:
            headers = {}
            if api_key_env and health.api_key_configured:
                if api_key_env == "GITHUB_TOKEN":
                    headers["Authorization"] = f"token {self.api_keys[api_key_env]}"
                elif api_key_env == "SEMANTIC_SCHOLAR_API_KEY":
                    headers["x-api-key"] = self.api_keys[api_key_env]
                elif "CROSSREF" in api_key_env:
                    headers["User-Agent"] = "Research-Collector/1.0"
            
            start_time = time.time()
            
            # Special handling for different APIs
            if name == "Reddit":
                # Reddit requires OAuth, so we'll just check if the endpoint is accessible
                response = requests.get(api_url, timeout=10, headers=headers)
            elif name == "Medium":
                # Medium RSS feeds require proper user agent
                headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                response = requests.get(api_url, timeout=10, headers=headers)
            elif name == "Kaggle":
                # Kaggle API requires authentication
                if not self.api_keys.get("KAGGLE_USERNAME") or not self.api_keys.get("KAGGLE_KEY"):
                    health.status = "unhealthy"
                    health.error_message = "Kaggle requires both KAGGLE_USERNAME and KAGGLE_KEY"
                    health.details["username_configured"] = self.api_keys.get("KAGGLE_USERNAME") is not None
                    health.details["key_configured"] = self.api_keys.get("KAGGLE_KEY") is not None
                    return health
                
                headers["Authorization"] = f"Bearer {self.api_keys.get('KAGGLE_KEY')}"
                response = requests.get(api_url, timeout=10, headers=headers)
            else:
                response = requests.get(api_url, params=test_params, timeout=10, headers=headers)
            
            response_time = (time.time() - start_time) * 1000
            health.response_time_ms = round(response_time, 2)
            health.details["response_time_ms"] = health.response_time_ms
            health.details["status_code"] = response.status_code
            
            # Check response status
            if response.status_code in [200, 201, 202, 204]:
                health.api_available = True
                health.api_key_valid = True
                
                # Determine status based on response time
                if response_time < 1000:
                    health.status = "healthy"
                elif response_time < 3000:
                    health.status = "degraded"
                    health.error_message = f"Slow response time: {response_time:.2f}ms"
                else:
                    health.status = "degraded"
                    health.error_message = f"Very slow response time: {response_time:.2f}ms"
                
                health.details["message"] = f"API responded successfully in {response_time:.2f}ms"
                
            elif response.status_code == 401:
                health.status = "unhealthy"
                health.api_available = True
                health.api_key_valid = False
                health.error_message = "Authentication failed - API key invalid or expired"
                health.details["auth_error"] = True
                
            elif response.status_code == 403:
                health.status = "unhealthy"
                health.api_available = True
                health.api_key_valid = False
                health.error_message = "Access forbidden - API key may be blocked or rate limited"
                health.details["access_error"] = True
                
            elif response.status_code == 429:
                health.status = "degraded"
                health.api_available = True
                health.api_key_valid = True
                health.error_message = "Rate limited - too many requests"
                health.details["rate_limited"] = True
                
            elif response.status_code >= 500:
                health.status = "unhealthy"
                health.api_available = False
                health.error_message = f"Server error: {response.status_code}"
                health.details["server_error"] = True
                
            else:
                health.status = "degraded"
                health.api_available = True
                health.error_message = f"Unexpected status code: {response.status_code}"
                health.details["unexpected_status"] = True
                
        except requests.exceptions.Timeout:
            health.status = "unhealthy"
            health.api_available = False
            health.error_message = "Request timed out after 10 seconds"
            health.details["timeout"] = True
            
        except requests.exceptions.ConnectionError:
            health.status = "unhealthy"
            health.api_available = False
            health.error_message = "Connection error - API may be down"
            health.details["connection_error"] = True
            
        except Exception as e:
            health.status = "unhealthy"
            health.api_available = False
            health.error_message = f"Unexpected error: {str(e)}"
            health.details["unexpected_error"] = True
        
        return health
    
    def check_all_sources(self) -> List[SourceHealth]:
        """Check health of all sources."""
        results = []
        for source_config in self.sources:
            health = self.check_source(source_config)
            results.append(health)
        return results
    
    def generate_summary(self, results: List[SourceHealth]) -> Dict[str, Any]:
        """Generate summary of health check results."""
        total = len(results)
        healthy = sum(1 for r in results if r.status == "healthy")
        degraded = sum(1 for r in results if r.status == "degraded")
        unhealthy = sum(1 for r in results if r.status == "unhealthy")
        unknown = sum(1 for r in results if r.status == "unknown")
        
        # API key status
        keys_configured = sum(1 for r in results if r.api_key_configured)
        keys_required = sum(1 for r in results if r.api_key_configured and not r.api_key_valid)
        
        # Category breakdown
        categories = {}
        for result in results:
            category = result.details.get("category", "unknown")
            if category not in categories:
                categories[category] = {"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0, "total": 0}
            categories[category][result.status] += 1
            categories[category]["total"] += 1
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_sources": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "unknown": unknown,
            "health_percentage": round((healthy / total) * 100, 2) if total > 0 else 0,
            "api_keys_configured": keys_configured,
            "api_keys_invalid": keys_required,
            "categories": categories
        }
    
    def print_results(self, results: List[SourceHealth], summary: Dict[str, Any]):
        """Print health check results."""
        print("\n" + "="*80)
        print("SOURCE HEALTH CHECK REPORT")
        print("="*80)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Total Sources: {summary['total_sources']}")
        print(f"Healthy: {summary['healthy']} ({summary['health_percentage']}%)")
        print(f"Degraded: {summary['degraded']}")
        print(f"Unhealthy: {summary['unhealthy']}")
        print(f"Unknown: {summary['unknown']}")
        print(f"API Keys Configured: {summary['api_keys_configured']}")
        print(f"API Keys Invalid: {summary['api_keys_invalid']}")
        print("="*80 + "\n")
        
        # Category breakdown
        print("CATEGORY BREAKDOWN:")
        for category, stats in summary['categories'].items():
            print(f"  {category.capitalize()}:")
            print(f"    Total: {stats['total']}")
            print(f"    Healthy: {stats['healthy']}")
            print(f"    Degraded: {stats['degraded']}")
            print(f"    Unhealthy: {stats['unhealthy']}")
        print()
        
        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 80)
        for result in results:
            status_icon = {
                "healthy": "✓",
                "degraded": "⚠",
                "unhealthy": "✗",
                "unknown": "?"
            }.get(result.status, "?")
            
            print(f"{status_icon} {result.name:20s} [{result.status.upper():10s}]")
            print(f"  API Available: {result.api_available}")
            print(f"  API Key Configured: {result.api_key_configured}")
            print(f"  API Key Valid: {result.api_key_valid}")
            print(f"  Response Time: {result.response_time_ms}ms")
            
            if result.error_message:
                print(f"  Error: {result.error_message}")
            
            if result.details:
                print(f"  Details: {json.dumps(result.details, indent=4)}")
            print()
        
        print("="*80 + "\n")
    
    def export_json(self, results: List[SourceHealth], summary: Dict[str, Any], output_file: str):
        """Export results to JSON file."""
        output = {
            "summary": summary,
            "sources": [asdict(r) for r in results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Results exported to {output_file}")


def main():
    """Main entry point."""
    checker = SourceHealthChecker()
    results = checker.check_all_sources()
    summary = checker.generate_summary(results)
    
    # Print results
    checker.print_results(results, summary)
    
    # Export to JSON if output file specified
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        checker.export_json(results, summary, output_file)
    
    # Always exit 0 - let the workflow handle failure logic
    sys.exit(0)


if __name__ == "__main__":
    main()
