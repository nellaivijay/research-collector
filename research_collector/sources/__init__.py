"""Source modules for Research-Collector."""

from research_collector.sources.pubmed import PubMedSource
from research_collector.sources.stackoverflow import StackOverflowSource
from research_collector.sources.crossref import CrossrefSource
from research_collector.sources.paperswithcode import PapersWithCodeSource
from research_collector.sources.semantic_scholar import SemanticScholarSource
from research_collector.sources.news import GDELTSource
from research_collector.sources.reddit import RedditSource
from research_collector.sources.hackernews import HackerNewsSource
from research_collector.sources.github import GitHubSource

__all__ = [
    "PubMedSource",
    "StackOverflowSource", 
    "CrossrefSource",
    "PapersWithCodeSource",
    "SemanticScholarSource",
    "GDELTSource",
    "RedditSource",
    "HackerNewsSource",
    "GitHubSource",
]