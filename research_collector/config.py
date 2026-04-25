"""Configuration management for Research-Collector."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class Config:
    """Configuration management for Research-Collector."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML config file (optional)
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self.api_keys = self._load_api_keys()
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_locations = [
            "research-collector.yaml",
            "~/.research-collector/config.yaml",
            "~/.config/research-collector/config.yaml",
        ]
        
        for location in possible_locations:
            path = Path(location).expanduser()
            if path.exists():
                return str(path)
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults."""
        defaults = {
            "sources": {
                "academic": {
                    "pubmed": True,
                    "crossref": True,
                    "semantic_scholar": True,
                    "paperswithcode": True,
                    "arxiv": True,
                },
                "professional": {
                    "stackoverflow": True,
                    "github": True,
                    "kaggle": True,
                },
                "social": {
                    "reddit": True,
                    "hackernews": True,
                },
                "news": {
                    "gdelt": True,
                    "newsapi": False,
                    "medium": True,
                }
            },
            "time_ranges": {
                "default": 7,
                "quick": 3,
                "standard": 15,
                "deep": 30,
                "historical": 90,
                "extended": 365,
            },
            "exports": {
                "default": "markdown",
                "directory": "~/research_outputs",
                "include_metadata": True,
            },
            "scoring": {
                "weights": {
                    "relevance": 0.4,
                    "recency": 0.3,
                    "engagement": 0.3,
                }
            },
            "predefined_topics": {
                "agi": {
                    "name": "Artificial General Intelligence",
                    "keywords": [
                        "artificial general intelligence",
                        "AGI",
                        "general AI",
                        "human-level AI",
                        "strong AI",
                        "universal AI"
                    ]
                },
                "aci": {
                    "name": "Artificial Conscious Intelligence",
                    "keywords": [
                        "artificial consciousness",
                        "machine consciousness",
                        "AI consciousness",
                        "sentient AI",
                        "conscious AI",
                        "ACI"
                    ]
                },
                "asi": {
                    "name": "Artificial Super Intelligence",
                    "keywords": [
                        "artificial super intelligence",
                        "superintelligent AI",
                        "ASI",
                        "superintelligence",
                        "beyond human AI"
                    ]
                },
                "ani": {
                    "name": "Artificial Narrow Intelligence",
                    "keywords": [
                        "artificial narrow intelligence",
                        "weak AI",
                        "ANI",
                        "specialized AI",
                        "task-specific AI",
                        "narrow AI"
                    ]
                },
                "ml": {
                    "name": "Machine Learning",
                    "keywords": [
                        "machine learning",
                        "ML",
                        "deep learning",
                        "neural networks",
                        "supervised learning",
                        "unsupervised learning",
                        "reinforcement learning"
                    ]
                },
                "llm": {
                    "name": "Large Language Models",
                    "keywords": [
                        "large language models",
                        "LLM",
                        "language models",
                        "GPT",
                        "transformer models",
                        "foundation models"
                    ]
                },
                "rl": {
                    "name": "Reinforcement Learning",
                    "keywords": [
                        "reinforcement learning",
                        "RL",
                        "Q-learning",
                        "policy gradient",
                        "reward learning",
                        "agent-based learning"
                    ]
                },
                "cv": {
                    "name": "Computer Vision",
                    "keywords": [
                        "computer vision",
                        "CV",
                        "image recognition",
                        "object detection",
                        "visual AI",
                        "image processing"
                    ]
                },
                "nlp": {
                    "name": "Natural Language Processing",
                    "keywords": [
                        "natural language processing",
                        "NLP",
                        "text analysis",
                        "language understanding",
                        "computational linguistics",
                        "text mining"
                    ]
                },
                "robotics": {
                    "name": "Robotics and Automation",
                    "keywords": [
                        "robotics",
                        "automation",
                        "robotic systems",
                        "autonomous systems",
                        "robot control",
                        "mechatronics"
                    ]
                }
            }
        }
        
        if self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    return self._merge_configs(defaults, user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return defaults
        
        return defaults
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables."""
        keys = {
            "PUBMED_API_KEY": os.getenv("PUBMED_API_KEY"),
            "CROSSREF_API_KEY": os.getenv("CROSSREF_API_KEY"),
            "SEMANTIC_SCHOLAR_API_KEY": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
            "NEWSAPI_API_KEY": os.getenv("NEWSAPI_API_KEY"),
            "STACKEXCHANGE_API_KEY": os.getenv("STACKEXCHANGE_API_KEY"),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        }
        
        # Filter out None values
        return {k: v for k, v in keys.items() if v is not None}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        return self.api_keys.get(f"{service.upper()}_API_KEY")
    
    def is_source_enabled(self, source: str) -> bool:
        """Check if a source is enabled in configuration."""
        # Check each category
        for category in self.config.get("sources", {}).values():
            if isinstance(category, dict) and source in category:
                return category[source]
        return False
    
    def get_enabled_sources(self) -> list:
        """Get list of all enabled sources."""
        enabled = []
        for category in self.config.get("sources", {}).values():
            if isinstance(category, dict):
                for source, is_enabled in category.items():
                    if is_enabled:
                        enabled.append(source)
        return enabled
    
    def get_predefined_topic(self, topic_key: str) -> Optional[Dict[str, Any]]:
        """
        Get predefined topic by key.
        
        Args:
            topic_key: Key of the predefined topic (e.g., 'agi', 'ml')
        
        Returns:
            Dictionary with topic name and keywords, or None if not found
        """
        topics = self.config.get("predefined_topics", {})
        return topics.get(topic_key)
    
    def get_all_predefined_topics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all predefined topics.
        
        Returns:
            Dictionary of all predefined topics
        """
        return self.config.get("predefined_topics", {})
    
    def get_predefined_topic_keywords(self, topic_key: str) -> Optional[List[str]]:
        """
        Get keywords for a predefined topic.
        
        Args:
            topic_key: Key of the predefined topic
        
        Returns:
            List of keywords, or None if topic not found
        """
        topic = self.get_predefined_topic(topic_key)
        return topic["keywords"] if topic else None