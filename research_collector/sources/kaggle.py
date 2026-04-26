"""Kaggle source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from research_collector.config import Config


class KaggleSource:
    """Kaggle datasets and notebooks source."""
    
    def __init__(self, config: Config):
        """Initialize Kaggle source."""
        self.config = config
        self.username = config.get_api_key("kaggle_username")
        self.api_key = config.get_api_key("kaggle_key")
        self.base_url = "https://www.kaggle.com/api/v1"
    
    def search(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        depth: str = "default",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search Kaggle for datasets and notebooks."""
        try:
            import requests
            
            # Format dates for Kaggle API
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            results = []
            
            # Kaggle API doesn't support OR queries well
            # Use first keyword only if OR is present
            search_query = topic.split(" OR ")[0].strip() if " OR " in topic else topic
            
            # Search for datasets
            datasets_url = f"{self.base_url}/datasets/search"
            params = {
                "search": search_query,
                "size": 200,  # Increased limit
                "fileType": "csv"  # Focus on CSV datasets
            }
            
            headers = {}
            if self.username and self.api_key:
                # Kaggle uses basic authentication with username/key
                import base64
                credentials = f"{self.username}:{self.api_key}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_credentials}"
            
            response = requests.get(datasets_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            datasets_data = response.json()
            
            for dataset in datasets_data[:200]:  # Limit to 200
                try:
                    # Extract basic info
                    title = dataset.get('title', 'No title')
                    subtitle = dataset.get('subtitle', '')
                    url = f"https://www.kaggle.com/datasets/{dataset.get('ref', '')}"
                    
                    # Extract author
                    author = dataset.get('author', {}).get('name', 'Unknown')
                    
                    # Extract publication date
                    last_updated = dataset.get('lastUpdated')
                    if last_updated:
                        try:
                            pub_dt = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ")
                            pub_date = pub_dt.strftime("%Y-%m-%d")
                        except:
                            pub_date = last_updated[:10]
                    else:
                        pub_date = "Unknown"
                    
                    # Extract engagement metrics
                    total_downloads = dataset.get('totalDownloads', 0)
                    total_votes = dataset.get('totalVotes', 0)
                    usability_rating = dataset.get('usabilityRating', 0)
                    
                    # Extract tags
                    tags = dataset.get('tags', [])
                    
                    # Combine subtitle and tags for content
                    content = f"{subtitle} Tags: {', '.join(tags[:10])}"
                    content = content[:1000]
                    
                    formatted_result = {
                        "id": f"kaggle_dataset_{dataset.get('ref', '').replace('/', '_')}",
                        "title": title,
                        "url": url,
                        "author": author,
                        "published_date": pub_date,
                        "citations": 0,
                        "upvotes": total_votes,
                        "downloads": total_downloads,
                        "comments": 0,
                        "content": content,
                        "metadata": {
                            "kaggle_ref": dataset.get('ref', ''),
                            "subtitle": subtitle,
                            "total_downloads": total_downloads,
                            "total_votes": total_votes,
                            "usability_rating": usability_rating,
                            "usability_rating_badge": dataset.get('usabilityRatingBadge', ''),
                            "tags": tags,
                            "tag_count": len(tags),
                            "file_count": dataset.get('fileCount', 0),
                            "file_type": dataset.get('fileType', ''),
                            "size_kb": dataset.get('size', 0),
                            "has_data": dataset.get('hasData', False),
                            "is_private": dataset.get('isPrivate', False)
                        }
                    }
                    
                    results.append(formatted_result)
                    
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error fetching Kaggle data: {e}")
            return []
