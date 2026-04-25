"""GitHub source for Research-Collector."""

from datetime import datetime
from typing import List, Dict, Any
import requests
from research_collector.config import Config


class GitHubSource:
    """GitHub repositories and development source."""
    
    def __init__(self, config: Config):
        """Initialize GitHub source."""
        self.config = config
        self.api_key = config.get_api_key("github")
        self.base_url = "https://api.github.com"
    
    def search(
        self, 
        topic: str, 
        from_date: datetime, 
        to_date: datetime, 
        depth: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search GitHub for repositories."""
        try:
            # Format date for GitHub search (YYYY-MM-DD)
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            # Build search query
            query = f'{topic} in:name,description,readme created:{from_date_str}..{to_date_str}'
            
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.api_key:
                headers["Authorization"] = f"token {self.api_key}"
            
            params = {
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": 100  # Increased from 20 to 100
            }
            
            response = requests.get(
                f"{self.base_url}/search/repositories",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            formatted_results = []
            for item in items:
                # Get detailed repository info
                owner = item.get("owner", {})
                repo_name = item.get("full_name", "")
                
                # Extract topics
                topics = item.get("topics", [])
                
                # Extract license
                license_info = item.get("license", {})
                license_name = license_info.get("name") if license_info else None
                
                # Calculate repository age in days
                created_at = item.get("created_at", "")
                updated_at = item.get("updated_at", "")
                
                # Parse dates
                try:
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    days_since_creation = (datetime.now(created_dt.tzinfo) - created_dt).days
                    days_since_update = (datetime.now(updated_dt.tzinfo) - updated_dt).days
                except:
                    days_since_creation = 0
                    days_since_update = 0
                
                # Get README content for description
                description = item.get("description", "")
                readme_content = self._get_readme(repo_name, headers)
                if readme_content:
                    content = f"{description}\n\n{readme_content[:500]}..."
                else:
                    content = description or "No description available"
                
                formatted_result = {
                    "id": f"github_{repo_name.replace('/', '_')}",
                    "title": item.get("name", "No title"),
                    "url": item.get("html_url", ""),
                    "author": owner.get("login", "Unknown"),
                    "published_date": created_at[:10] if created_at else "Unknown",
                    "citations": 0,
                    "upvotes": item.get("stargazers_count", 0),
                    "downloads": 0,  # GitHub doesn't provide download counts
                    "comments": item.get("open_issues_count", 0),
                    "content": content,
                    "metadata": {
                        "stars": item.get("stargazers_count", 0),
                        "forks": item.get("forks_count", 0),
                        "watchers": item.get("watchers_count", 0),
                        "open_issues": item.get("open_issues_count", 0),
                        "language": item.get("language", "Unknown"),
                        "topics": topics,
                        "license": license_name,
                        "has_license": bool(license_name),
                        "is_fork": item.get("fork", False),
                        "size_kb": item.get("size", 0),
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "days_since_creation": days_since_creation,
                        "days_since_update": days_since_update,
                        "has_readme": bool(readme_content),
                        "homepage": item.get("homepage") or "",
                        "has_wiki": item.get("has_wiki", False),
                        "has_pages": item.get("has_pages", False),
                        "has_projects": item.get("has_projects", False),
                        "has_downloads": item.get("has_downloads", False),
                        "archived": item.get("archived", False),
                        "disabled": item.get("disabled", False)
                    }
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub data: {e}")
            return []
        except Exception as e:
            print(f"Error processing GitHub data: {e}")
            return []
    
    def _get_readme(self, repo_name: str, headers: Dict) -> str:
        """Fetch README content for a repository."""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}/readme",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                import base64
                content = data.get("content", "")
                if content:
                    return base64.b64decode(content).decode('utf-8', errors='ignore')
        except:
            pass
        return ""