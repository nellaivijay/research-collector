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
@click.option("--export", default="markdown", type=click.Choice(['markdown', 'json', 'csv', 'bibliography', 'html', 'huggingface']), help="Export format")
@click.option("--output", help="Output file path (or HF repo ID for huggingface format)")
@click.option("--hf-token", help="Hugging Face authentication token (or set HF_TOKEN env var)")
@click.option("--depth", default="default", help="Search depth: quick, default, standard, deep, historical, extended")
@click.option("--include-urls", is_flag=True, help="Include source URLs in results (default: no)")
@click.option("--list-topics", is_flag=True, help="List all available predefined topics")
@click.option("--no-cache", is_flag=True, help="Disable caching")
@click.option("--no-history", is_flag=True, help="Disable search history")
def research(topic, query, days, sources, export, output, hf_token, depth, include_urls, list_topics, no_cache, no_history):
    """Research a topic across multiple sources."""
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False
    
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
    
    pipeline = Pipeline(config, use_cache=not no_cache, save_history=not no_history)
    
    # Use depth-based time range if depth is specified and not custom days
    if depth != "default" and days == 7:
        days = config.get(f"time_ranges.{depth}", days)
    
    from_date = datetime.now() - timedelta(days=days)
    to_date = datetime.now()
    
    source_list = sources.split(",") if sources else None
    
    click.echo(f"\nSearching for: {search_topic}")
    click.echo(f"Time range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    click.echo(f"Sources: {', '.join(source_list) if source_list else 'all enabled'}")
    click.echo()
    
    # Show progress
    if use_tqdm:
        with tqdm(total=100, desc="Researching", unit="%") as pbar:
            pbar.update(10)
            results = pipeline.run(
                topic=search_query,
                from_date=from_date,
                to_date=to_date,
                sources=source_list,
                depth=depth,
                include_urls=include_urls
            )
            pbar.update(90)
    else:
        click.echo("Running research...")
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
            BibliographyExporter,
            HTMLExporter,
            HuggingFaceExporter
        )
        
        # Get HF token from parameter or environment
        import os
        hf_token = hf_token or os.environ.get("HF_TOKEN")
        
        exporters = {
            "markdown": MarkdownExporter(),
            "json": JSONExporter(),
            "csv": CSVExporter(),
            "bibliography": BibliographyExporter(),
            "html": HTMLExporter(),
            "huggingface": HuggingFaceExporter(token=hf_token)
        }
        
        exporter = exporters.get(export.lower(), MarkdownExporter())
        
        if export.lower() == "huggingface":
            if not output:
                click.echo("Error: --output (HF repo ID) required for huggingface export")
                click.echo("Format: username/dataset-name")
                return
            exporter.export(results, output)
            click.echo(f"Results pushed to Hugging Face Hub: {output}")
        else:
            exporter.export(results, output)
            click.echo(f"Results saved to {output} in {export} format")
    else:
        click.echo(f"\nFound {len(results['items'])} results")


@cli.command()
def interactive():
    """Start interactive research mode."""
    try:
        from rich.console import Console
        from rich.prompt import Prompt
        from rich.table import Table
        from rich import print as rprint
    except ImportError:
        print("Rich library not installed. Install with: pip install rich")
        return
    
    console = Console()
    rprint("[bold cyan]Research-Collector Interactive Mode[/bold cyan]")
    rprint("Type 'help' for commands or 'exit' to quit\n")
    
    config = Config()
    
    # Display available topics
    topics = config.get_all_predefined_topics()
    topic_table = Table(title="Available Topics")
    topic_table.add_column("Key", style="cyan")
    topic_table.add_column("Name", style="green")
    topic_table.add_column("Keywords", style="yellow")
    
    for key, topic_info in topics.items():
        keywords = ", ".join(topic_info["keywords"][:3])
        topic_table.add_row(key, topic_info["name"], f"{keywords}...")
    
    console.print(topic_table)
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold]research-collector[/bold]>", console=console)
            
            if not user_input.strip():
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                rprint("[bold green]Goodbye![/bold green]")
                break
            
            if user_input.lower() == 'help':
                rprint("[bold]Commands:[/bold]")
                rprint("  <topic>        - Research a predefined topic")
                rprint("  query <text>    - Custom search query")
                rprint("  days <number>   - Set time range (default: 7)")
                rprint("  sources <list>  - Set sources (comma-separated)")
                rprint("  export <format> - Set export format (markdown, json, csv, bibliography)")
                rprint("  topics          - List available topics")
                rprint("  exit            - Exit interactive mode")
                continue
            
            if user_input.lower() == 'topics':
                console.print(topic_table)
                continue
            
            # Parse command
            parts = user_input.split()
            
            # Default values
            topic = None
            query = None
            days = 7
            sources = None
            export_format = "markdown"
            
            i = 0
            while i < len(parts):
                if parts[i] == 'query' and i + 1 < len(parts):
                    query = ' '.join(parts[i+1:])
                    i = len(parts)
                elif parts[i] == 'days' and i + 1 < len(parts):
                    days = int(parts[i+1])
                    i += 2
                elif parts[i] == 'sources' and i + 1 < len(parts):
                    sources = parts[i+1].split(',')
                    i += 2
                elif parts[i] == 'export' and i + 1 < len(parts):
                    export_format = parts[i+1]
                    i += 2
                else:
                    # Assume it's a topic
                    topic = parts[i]
                    i += 1
            
            # Execute research
            if topic:
                rprint(f"\n[bold]Researching topic:[/bold] {topic}")
            elif query:
                rprint(f"\n[bold]Searching for:[/bold] {query}")
            
            rprint(f"[dim]Time range: {days} days[/dim]")
            if sources:
                rprint(f"[dim]Sources: {', '.join(sources)}[/dim]")
            
            pipeline = Pipeline(config)
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            if topic:
                predefined = config.get_predefined_topic(topic)
                if predefined:
                    search_query = predefined['keywords'][0]
                else:
                    rprint(f"[red]Unknown topic: {topic}[/red]")
                    continue
            elif query:
                search_query = query
            else:
                rprint("[red]Please specify a topic or query[/red]")
                continue
            
            # Show progress
            with console.status("[bold]Running research...[/bold]"):
                results = pipeline.run(
                    topic=search_query,
                    from_date=from_date,
                    to_date=to_date,
                    sources=sources
                )
            
            # Display results
            rprint(f"\n[bold green]Found {len(results['items'])} results[/bold green]")
            
            if len(results['items']) > 0:
                # Show top 5 results
                results_table = Table(title="Top Results")
                results_table.add_column("Title", style="cyan")
                results_table.add_column("Source", style="green")
                results_table.add_column("Score", style="yellow")
                results_table.add_column("Date", style="blue")
                
                for item in results['items'][:5]:
                    title = item['title'][:60] + "..." if len(item['title']) > 60 else item['title']
                    results_table.add_row(
                        title,
                        item['source'],
                        f"{item.get('score', 0):.2f}",
                        item['published_date'][:10]
                    )
                
                console.print(results_table)
            
        except KeyboardInterrupt:
            rprint("\n[bold yellow]Interrupted. Type 'exit' to quit.[/bold yellow]")
        except Exception as e:
            rprint(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--clear', is_flag=True, help='Clear all cache')
@click.option('--clear-expired', is_flag=True, help='Clear expired cache entries')
def cache(clear, clear_expired):
    """Manage API response cache."""
    from research_collector.cache import Cache
    
    cache_manager = Cache()
    
    if clear:
        cache_manager.clear()
        click.echo("Cache cleared successfully.")
    elif clear_expired:
        cleared = cache_manager.clear_expired()
        click.echo(f"Cleared {cleared} expired cache entries.")
    else:
        # Show cache status
        import os
        cache_files = list(cache_manager.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        click.echo(f"Cache directory: {cache_manager.cache_dir}")
        click.echo(f"Cache entries: {len(cache_files)}")
        click.echo(f"Total size: {total_size / 1024:.2f} KB")
        click.echo(f"TTL: {cache_manager.ttl}")
        click.echo("\nUse --clear to clear all cache or --clear-expired to clear expired entries.")


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
@click.option('--limit', default=20, help='Number of searches to show (default: 20)')
def history(limit):
    """View search history."""
    from research_collector.history import HistoryManager
    
    history_manager = HistoryManager()
    
    searches = history_manager.get_search_history(limit=limit)
    
    if not searches:
        click.echo("No search history found.")
        return
    
    click.echo(f"Search history (last {len(searches)} searches):")
    click.echo("")
    
    for search in searches:
        click.echo(f"  [{search['id']}] {search['topic']}")
        click.echo(f"    Date: {search['from_date']} to {search['to_date']}")
        click.echo(f"    Sources: {', '.join(search['sources']) if search['sources'] else 'all'}")
        click.echo(f"    Results: {search['result_count']}")
        click.echo(f"    Timestamp: {search['timestamp']}")
        click.echo("")


@cli.command()
@click.argument('search_id', type=int)
@click.option('--output', '-o', help='Output file path')
def history_results(search_id, output):
    """View results for a specific search."""
    from research_collector.history import HistoryManager
    
    history_manager = HistoryManager()
    
    results = history_manager.get_search_results(search_id)
    
    if not results:
        click.echo(f"No results found for search ID {search_id}")
        return
    
    click.echo(f"Results for search {search_id} ({len(results)} items):")
    click.echo("")
    
    for result in results:
        click.echo(f"  {result['title']}")
        click.echo(f"    Source: {result['source']}")
        click.echo(f"    Score: {result['score']:.2f}")
        click.echo(f"    Date: {result['published_date']}")
        click.echo("")


@cli.command()
def history_stats():
    """Show search history statistics."""
    from research_collector.history import HistoryManager
    
    history_manager = HistoryManager()
    
    stats = history_manager.get_stats()
    
    click.echo("Search History Statistics:")
    click.echo(f"  Total searches: {stats['total_searches']}")
    click.echo(f"  Total results: {stats['total_results']}")
    click.echo("")
    click.echo("Top topics:")
    for topic in stats['top_topics']:
        click.echo(f"  {topic['topic']}: {topic['count']}")
    click.echo("")
    click.echo("Top sources:")
    for source in stats['top_sources']:
        click.echo(f"  {source['source']}: {source['count']}")


@cli.command()
@click.argument('search_id', type=int)
@click.option('--confirm', is_flag=True, help='Confirm deletion without prompt')
def history_delete(search_id, confirm):
    """Delete a search from history."""
    from research_collector.history import HistoryManager
    
    history_manager = HistoryManager()
    
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete search {search_id}?"):
            click.echo("Deletion cancelled.")
            return
    
    if history_manager.delete_search(search_id):
        click.echo(f"Search {search_id} deleted successfully.")
    else:
        click.echo(f"Search {search_id} not found.")


@cli.command()
@click.option('--confirm', is_flag=True, help='Confirm deletion without prompt')
def history_clear(confirm):
    """Clear all search history."""
    from research_collector.history import HistoryManager
    
    history_manager = HistoryManager()
    
    if not confirm:
        if not click.confirm("Are you sure you want to clear ALL search history? This cannot be undone."):
            click.echo("Clear cancelled.")
            return
    
    count = history_manager.clear_history()
    click.echo(f"Cleared {count} searches from history.")


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def web(host, port, debug):
    """Start the web interface."""
    try:
        from research_collector.web import run_web
        click.echo(f"Starting web interface on http://{host}:{port}")
        run_web(host=host, port=port, debug=debug)
    except ImportError:
        click.echo("Flask not installed. Install with: pip install flask")
    except Exception as e:
        click.echo(f"Error starting web interface: {e}")


@cli.group()
def monitor():
    """Monitor topics for periodic research."""
    pass


@monitor.command()
@click.option('--name', required=True, help='Monitor name')
@click.option('--topic', required=True, help='Research topic')
@click.option('--interval', default=24, help='Check interval in hours (default: 24)')
@click.option('--sources', help='Comma-separated list of sources')
@click.option('--output-dir', help='Directory to save results')
def add(name, topic, interval, sources, output_dir):
    """Add a new monitor."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    source_list = sources.split(',') if sources else None
    
    monitor_id = monitor.add_monitor(
        name=name,
        topic=topic,
        interval_hours=interval,
        sources=source_list,
        output_dir=output_dir
    )
    
    click.echo(f"Monitor '{name}' added with ID: {monitor_id}")
    click.echo(f"Topic: {topic}")
    click.echo(f"Interval: {interval} hours")


@monitor.command()
def list():
    """List all monitors."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    monitors = monitor.list_monitors()
    
    if not monitors:
        click.echo("No monitors configured.")
        return
    
    click.echo("Configured monitors:")
    click.echo("")
    
    for m in monitors:
        status = "enabled" if m.get("enabled", True) else "disabled"
        last_run = m.get("last_run", "never")
        
        click.echo(f"  {m['name']} ({m['id']})")
        click.echo(f"    Topic: {m['topic']}")
        click.echo(f"    Interval: {m['interval_hours']} hours")
        click.echo(f"    Status: {status}")
        click.echo(f"    Last run: {last_run}")
        click.echo("")


@monitor.command()
@click.argument('monitor_id')
def remove(monitor_id):
    """Remove a monitor."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    if monitor.remove_monitor(monitor_id):
        click.echo(f"Monitor {monitor_id} removed successfully.")
    else:
        click.echo(f"Monitor {monitor_id} not found.")


@monitor.command()
@click.argument('monitor_id')
def enable(monitor_id):
    """Enable a monitor."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    if monitor.enable_monitor(monitor_id):
        click.echo(f"Monitor {monitor_id} enabled.")
    else:
        click.echo(f"Monitor {monitor_id} not found.")


@monitor.command()
@click.argument('monitor_id')
def disable(monitor_id):
    """Disable a monitor."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    if monitor.disable_monitor(monitor_id):
        click.echo(f"Monitor {monitor_id} disabled.")
    else:
        click.echo(f"Monitor {monitor_id} not found.")


@monitor.command()
@click.argument('monitor_id')
def run(monitor_id):
    """Run a monitor check immediately."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    results = monitor.run_monitor(monitor_id)
    
    if results is None:
        click.echo(f"Monitor {monitor_id} not found or disabled.")
    else:
        click.echo(f"Monitor {monitor_id} completed successfully.")


@monitor.command()
@click.option('--interval', default=60, help='Check interval in seconds (default: 60)')
def daemon(interval):
    """Start monitor daemon (runs in foreground)."""
    from research_collector.monitor import Monitor
    
    config = Config()
    monitor = Monitor(config)
    
    monitor.start_daemon(check_interval=interval)


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