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
@click.argument("topic")
@click.option("--days", default=30, help="Number of days to search back")
@click.option("--sources", help="Comma-separated list of sources")
@click.option("--export", default="markdown", help="Export format")
@click.option("--output", help="Output file path")
def research(topic, days, sources, export, output):
    """Research a topic across multiple sources."""
    config = Config()
    pipeline = Pipeline(config)
    
    from_date = datetime.now() - timedelta(days=days)
    to_date = datetime.now()
    
    source_list = sources.split(",") if sources else None
    
    results = pipeline.run(
        topic=topic,
        from_date=from_date,
        to_date=to_date,
        sources=source_list
    )
    
    # Output results
    if output:
        with open(output, 'w') as f:
            f.write(str(results))
        click.echo(f"Results saved to {output}")
    else:
        click.echo(f"Found {len(results['items'])} results")


@cli.command()
def interactive():
    """Start interactive research mode."""
    click.echo("Interactive mode coming soon!")


@cli.command()
@click.argument("topic")
@click.option("--days", default=7, help="Number of days to monitor")
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
@click.option("--days", default=90, help="Number of days to analyze")
def timeline(topic, days):
    """Analyze topic evolution over time."""
    click.echo(f"Timeline analysis for {topic} over {days} days - coming soon!")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()