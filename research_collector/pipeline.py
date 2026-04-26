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
        
        if self.config.is_source_enabled("medium"):
            from research_collector.sources.medium import MediumSource
            sources["medium"] = MediumSource(self.config)
        
        if self.config.is_source_enabled("kaggle"):
            from research_collector.sources.kaggle import KaggleSource
            sources["kaggle"] = KaggleSource(self.config)
        
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
        include_urls: bool = False,
        max_results_per_source: Optional[int] = None
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
            max_results_per_source: Maximum results per source (None = use config default)

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
                        depth,
                        max_results_per_source
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
        
        # Validate results and log summary
        from research_collector.validation import validate_results, log_data_summary, filter_invalid_items
        
        # Log data summary for monitoring
        log_data_summary(ranked_results, topic)
        
        # Validate results
        validation_result = validate_results(ranked_results)
        
        # Filter out items with critical issues
        ranked_results = filter_invalid_items(ranked_results)
        
        # Ensure minimum arXiv items (guarantee at least 20 arXiv papers)
        ranked_results = self._ensure_arxiv_priority(ranked_results, all_results)
        
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
                "source_counts": {name: len(results) for name, results in all_results.items()},
                "validation": validation_result
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
    
    def _ensure_arxiv_priority(self, ranked_results: List[Dict], all_results: Dict[str, List]) -> List[Dict]:
        """
        Ensure minimum number of arXiv items in final results.
        
        Args:
            ranked_results: Current ranked and filtered results
            all_results: Original results by source before ranking/filtering
            
        Returns:
            Results with guaranteed minimum arXiv items
        """
        MIN_ARXIV_ITEMS = 20
        
        # Count current arXiv items in ranked results
        current_arxiv_count = sum(1 for item in ranked_results if item.get("source") == "arxiv")
        
        # If we already have enough arXiv items, return as-is
        if current_arxiv_count >= MIN_ARXIV_ITEMS:
            return ranked_results
        
        # Get original arXiv items before deduplication/filtering
        original_arxiv_items = all_results.get("arxiv", [])
        
        if not original_arxiv_items:
            return ranked_results  # No arXiv items available
        
        # Normalize original arXiv items to match ranked format
        from research_collector.normalization import normalize_results
        normalized_arxiv = normalize_results({"arxiv": original_arxiv_items}, "")
        
        # Add missing arXiv items (top ranked ones)
        needed = MIN_ARXIV_ITEMS - current_arxiv_count
        arxiv_to_add = normalized_arxiv[:needed]
        
        # Add scores to arXiv items for consistency
        for item in arxiv_to_add:
            item["score"] = item.get("score", 0.5)  # Default score for priority items
        
        # Combine results, maintaining ranking order
        # Insert arXiv items at the beginning to ensure they're included
        final_results = arxiv_to_add + [item for item in ranked_results if item.get("source") != "arxiv"]
        
        # Re-sort by score to maintain ranking while preserving arXiv priority
        final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)
        
        print(f"Added {needed} arXiv items to ensure minimum {MIN_ARXIV_ITEMS} arXiv papers")
        
        return final_results