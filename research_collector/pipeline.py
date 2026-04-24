"""Research pipeline orchestration for Research-Collector."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from research_collector.config import Config


class Pipeline:
    """Main research pipeline orchestrator."""
    
    def __init__(self, config: Config):
        """
        Initialize the research pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.sources = self._load_sources()
    
    def _load_sources(self) -> Dict[str, Any]:
        """Load available source modules."""
        sources = {}
        
        # Academic sources
        if self.config.is_source_enabled("pubmed"):
            from research_collector.sources.pubmed import PubMedSource
            sources["pubmed"] = PubMedSource(self.config)
        
        if self.config.is_source_enabled("crossref"):
            from research_collector.sources.crossref import CrossrefSource
            sources["crossref"] = CrossrefSource(self.config)
        
        if self.config.is_source_enabled("semantic_scholar"):
            from research_collector.sources.semantic_scholar import SemanticScholarSource
            sources["semantic_scholar"] = SemanticScholarSource(self.config)
        
        if self.config.is_source_enabled("paperswithcode"):
            from research_collector.sources.paperswithcode import PapersWithCodeSource
            sources["paperswithcode"] = PapersWithCodeSource(self.config)
        
        # Professional sources
        if self.config.is_source_enabled("stackoverflow"):
            from research_collector.sources.stackoverflow import StackOverflowSource
            sources["stackoverflow"] = StackOverflowSource(self.config)
        
        if self.config.is_source_enabled("github"):
            from research_collector.sources.github import GitHubSource
            sources["github"] = GitHubSource(self.config)
        
        # Social sources
        if self.config.is_source_enabled("reddit"):
            from research_collector.sources.reddit import RedditSource
            sources["reddit"] = RedditSource(self.config)
        
        if self.config.is_source_enabled("hackernews"):
            from research_collector.sources.hackernews import HackerNewsSource
            sources["hackernews"] = HackerNewsSource(self.config)
        
        # News sources
        if self.config.is_source_enabled("gdelt"):
            from research_collector.sources.news import GDELTSource
            sources["gdelt"] = GDELTSource(self.config)
        
        return sources
    
    def run(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        sources: Optional[List[str]] = None,
        depth: str = "default",
        include_urls: bool = False
    ) -> Dict[str, Any]:
        """
        Run research pipeline for a topic.
        
        Args:
            topic: Research topic
            from_date: Start date
            to_date: End date
            sources: List of sources to use (None = all enabled)
            depth: Search depth (quick, default, deep)
            include_urls: Whether to include source URLs in results
        
        Returns:
            Research results with metadata
        """
        # Filter sources
        if sources:
            active_sources = {k: v for k, v in self.sources.items() if k in sources}
        else:
            active_sources = self.sources
        
        if not active_sources:
            return {
                "topic": topic,
                "error": "No sources available",
                "items": []
            }
        
        # Run parallel searches
        all_results = {}
        with ThreadPoolExecutor(max_workers=len(active_sources)) as executor:
            futures = {
                executor.submit(
                    source.search,
                    topic,
                    from_date,
                    to_date,
                    depth
                ): name for name, source in active_sources.items()
            }
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    results = future.result()
                    all_results[source_name] = results
                except Exception as e:
                    print(f"Error in {source_name}: {e}")
                    all_results[source_name] = []
        
        # Normalize and score results
        normalized_results = self._normalize_results(all_results, topic)
        
        # Cluster and rank
        clustered_results = self._cluster_results(normalized_results)
        ranked_results = self._rank_results(clustered_results, topic)
        
        # Filter URLs if not requested
        if not include_urls:
            for result in ranked_results:
                result.pop("url", None)
        
        return {
            "topic": topic,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "sources_used": list(active_sources.keys()),
            "items": ranked_results,
            "metadata": {
                "total_items": len(ranked_results),
                "source_counts": {name: len(results) for name, results in all_results.items()}
            }
        }
    
    def _normalize_results(self, raw_results: Dict[str, List], topic: str) -> List[Dict]:
        """Normalize results from all sources."""
        from research_collector.normalization import normalize_results
        return normalize_results(raw_results, topic)
    
    def _cluster_results(self, results: List[Dict]) -> List[Dict]:
        """Cluster duplicate/similar results."""
        from research_collector.clustering import cluster_results
        return cluster_results(results)
    
    def _rank_results(self, results: List[Dict], topic: str) -> List[Dict]:
        """Rank results by relevance and engagement."""
        from research_collector.scoring import rank_results
        return rank_results(results, topic, self.config)