"""Command-line interface for Research-Collector."""

import click
from datetime import datetime, timedelta
from research_collector.config import Config
from research_collector.pipeline import Pipeline


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Research-Collector: Educational multi-source research aggregation tool."""
    pass


@cli.command()
@click.option("--topic", help="Predefined topic key (e.g., agi, ml, llm)")
@click.option("--query", help="Custom search query (alternative to --topic)")
@click.option("--days", default=7, help="Number of days to search back (default: 7)")
@click.option("--sources", help="Comma-separated list of sources")
@click.option("--export", default="markdown", help="Export format")
@click.option("--output", help="Output file path")
@click.option("--depth", default="default", help="Search depth: quick, default, standard, deep, historical, extended")
@click.option("--include-urls", is_flag=True, help="Include source URLs in results (default: no)")
@click.option("--list-topics", is_flag=True, help="List all available predefined topics")
def research(topic, query, days, sources, export, output, depth, include_urls, list_topics):
    """Research a topic across multiple sources."""
    config = Config()
    
    # List all predefined topics if requested
    if list_topics:
        topics = config.get_all_predefined_topics()
        click.echo("Available predefined topics:")
        click.echo("")
        for key, topic_info in topics.items():
            click.echo(f"  {key}: {topic_info['name']}")
            click.echo(f"    Keywords: {', '.join(topic_info['keywords'][:3])}...")
        click.echo("")
        click.echo("Usage: python -m research_collector research --topic <key>")
        return
    
    # Determine search query
    if topic:
        predefined = config.get_predefined_topic(topic)
        if predefined:
            search_topic = predefined['name']
            keywords = predefined['keywords']
            click.echo(f"Using predefined topic: {predefined['name']}")
            click.echo(f"Keywords: {', '.join(keywords)}")
            # Use the first keyword as the main search term
            search_query = keywords[0]
        else:
            click.echo(f"Unknown predefined topic: {topic}")
            click.echo("Use --list-topics to see available topics")
            return
    elif query:
        search_query = query
        search_topic = query
    else:
        click.echo("Error: Either --topic or --query must be specified")
        click.echo("Use --list-topics to see available predefined topics")
        return
    
    pipeline = Pipeline(config)
    
    # Use depth-based time range if depth is specified and not custom days
    if depth != "default" and days == 7:
        days = config.get(f"time_ranges.{depth}", days)
    
    from_date = datetime.now() - timedelta(days=days)
    to_date = datetime.now()
    
    source_list = sources.split(",") if sources else None
    
    results = pipeline.run(
        topic=search_query,
        from_date=from_date,
        to_date=to_date,
        sources=source_list,
        depth=depth,
        include_urls=include_urls
    )
    
    # Output results
    if output:
        # Use the specified export format
        from research_collector.exporters import (
            MarkdownExporter, 
            JSONExporter, 
            CSVExporter, 
            BibliographyExporter
        )
        
        exporters = {
            "markdown": MarkdownExporter(),
            "json": JSONExporter(),
            "csv": CSVExporter(),
            "bibliography": BibliographyExporter()
        }
        
        exporter = exporters.get(export.lower(), MarkdownExporter())
        exporter.export(results, output)
        click.echo(f"Results saved to {output} in {export} format")
    else:
        click.echo(f"Found {len(results['items'])} results")


@cli.command()
def interactive():
    """Start interactive research mode."""
    click.echo("Interactive mode coming soon!")


@cli.command()
def topics():
    """List all available predefined research topics."""
    config = Config()
    topics = config.get_all_predefined_topics()
    
    click.echo("Available predefined research topics:")
    click.echo("")
    for key, topic_info in topics.items():
        click.echo(f"  {key}: {topic_info['name']}")
        click.echo(f"    Keywords: {', '.join(topic_info['keywords'])}")
        click.echo("")


@cli.command()
@click.argument("topic")
@click.option("--days", default=7, help="Number of days to monitor (default: 7)")
def monitor(topic, days):
    """Monitor a topic for new research."""
    click.echo(f"Monitoring {topic} for {days} days - coming soon!")


@cli.command()
@click.argument("sessions", nargs=-1)
def compare(sessions):
    """Compare multiple research sessions."""
    click.echo("Compare feature coming soon!")


@cli.command()
@click.argument("topic")
@click.option("--days", default=30, help="Number of days to analyze (default: 30)")
def timeline(topic, days):
    """Analyze topic evolution over time."""
    click.echo(f"Timeline analysis for {topic} over {days} days - coming soon!")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()