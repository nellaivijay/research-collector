"""Example usage of Research-Collector."""

from research_collector import Config, Pipeline
from datetime import datetime, timedelta


def basic_research_example():
    """Basic research example."""
    # Initialize configuration
    config = Config()
    
    # Initialize pipeline
    pipeline = Pipeline(config)
    
    # Define research parameters
    topic = "machine learning"
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    
    # Run research
    results = pipeline.run(
        topic=topic,
        from_date=from_date,
        to_date=to_date,
        sources=["pubmed", "stackoverflow", "crossref"]  # Specific sources
    )
    
    # Print summary
    print(f"Research Results for: {topic}")
    print(f"Total items: {len(results.get('items', []))}")
    print(f"Sources used: {results.get('sources_used', [])}")
    
    return results


def academic_research_example():
    """Academic research example with citation filtering."""
    config = Config()
    pipeline = Pipeline(config)
    
    topic = "transformer architecture"
    to_date = datetime.now()
    from_date = to_date - timedelta(days=90)
    
    # Use only academic sources
    results = pipeline.run(
        topic=topic,
        from_date=from_date,
        to_date=to_date,
        sources=["pubmed", "crossref", "semantic_scholar", "paperswithcode"]
    )
    
    return results


if __name__ == "__main__":
    # Run basic example
    results = basic_research_example()
    
    # Export to markdown
    from research_collector.exporters.markdown import MarkdownExporter
    exporter = MarkdownExporter()
    exporter.export(results, "machine_learning_research.md")