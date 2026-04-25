"""Research pipeline orchestration for Research-Collector."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from research_collector.config import Config
from research_collector.cache import Cache
from research_collector.history import HistoryManager


class Pipeline:
    """Main research pipeline orchestrator."""
    
    def __init__(self, config: Config, use_cache: bool = True, save_history: bool = True):
        """
        Initialize the research pipeline.
        
        Args:
            config: Configuration object
            use_cache: Whether to use caching for API responses
            save_history: Whether to save search history
        """
        self.config = config
        self.sources = self._load_sources()
        self.use_cache = use_cache
        self.cache = Cache() if use_cache else None
        self.save_history = save_history
        self.history = HistoryManager() if save_history else None
    
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
        
        if self.config.is_source_enabled("arxiv"):
            from research_collector.sources.arxiv import ArxivSource
            sources["arxiv"] = ArxivSource(self.config)
        
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
        
        # Run parallel searches with caching
        all_results = {}
        from_date_str = from_date.isoformat()
        to_date_str = to_date.isoformat()
        
        with ThreadPoolExecutor(max_workers=len(active_sources)) as executor:
            futures = {}
            
            for source_name, source in active_sources.items():
                # Check cache first
                cached_data = None
                if self.use_cache and self.cache:
                    cached_data = self.cache.get(source_name, topic, from_date_str, to_date_str)
                
                if cached_data is not None:
                    all_results[source_name] = cached_data
                else:
                    # Submit API request
                    future = executor.submit(
                        source.search,
                        topic,
                        from_date,
                        to_date,
                        depth
                    )
                    futures[future] = source_name
            
            # Wait for API requests
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    results = future.result()
                    all_results[source_name] = results
                    
                    # Cache the results
                    if self.use_cache and self.cache:
                        self.cache.set(source_name, topic, from_date_str, to_date_str, results)
                        
                except Exception as e:
                    print(f"Error in {source_name}: {e}")
                    all_results[source_name] = []
        
        # Normalize and score results
        normalized_results = self._normalize_results(all_results, topic)
        
        # Enrich results with additional metadata
        from research_collector.enrichment import enrich_results
        enriched_results = enrich_results(normalized_results)
        
        # Cluster and rank
        clustered_results = self._cluster_results(enriched_results)
        ranked_results = self._rank_results(clustered_results, topic)
        
        # Filter URLs if not requested
        if not include_urls:
            for result in ranked_results:
                result.pop("url", None)
        
        results = {
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
        
        # Save to history
        self._save_to_history(topic, from_date, to_date, sources, depth, results)
        
        return results
    
    def _save_to_history(
        self,
        topic: str,
        from_date: datetime,
        to_date: datetime,
        sources: Optional[List[str]],
        depth: str,
        results: Dict[str, Any]
    ) -> Optional[int]:
        """Save search to history.
        
        Args:
            topic: Search topic
            from_date: Start date
            to_date: End date
            sources: Sources used
            depth: Search depth
            results: Research results
        
        Returns:
            Search ID or None if history disabled
        """
        if not self.save_history or not self.history:
            return None
        
        search_id = self.history.add_search(
            topic=topic,
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
            sources=sources,
            depth=depth,
            result_count=len(results['items']),
            metadata=results.get('metadata')
        )
        
        self.history.add_results(search_id, results['items'])
        
        return search_id
    
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