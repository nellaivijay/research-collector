"""Basic web interface for Research-Collector."""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import Flask, render_template, request, jsonify
from research_collector.config import Config
from research_collector.pipeline import Pipeline
from research_collector.history import HistoryManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'research-collector-secret-key-change-in-production'


@app.route('/')
def index():
    """Render home page."""
    config = Config()
    topics = config.get_all_predefined_topics()
    return render_template('index.html', topics=topics)


@app.route('/search', methods=['POST'])
def search():
    """Run research search."""
    data = request.json
    
    topic = data.get('topic') or data.get('query')
    days = data.get('days', 7)
    sources = data.get('sources')
    depth = data.get('depth', 'default')
    
    if not topic:
        return jsonify({'error': 'Topic or query is required'}), 400
    
    config = Config()
    pipeline = Pipeline(config)
    
    from_date = datetime.now() - timedelta(days=days)
    to_date = datetime.now()
    
    source_list = sources.split(',') if sources else None
    
    results = pipeline.run(
        topic=topic,
        from_date=from_date,
        to_date=to_date,
        sources=source_list,
        depth=depth
    )
    
    return jsonify(results)


@app.route('/history')
def history():
    """Get search history."""
    history_manager = HistoryManager()
    searches = history_manager.get_search_history(limit=50)
    return jsonify(searches)


@app.route('/history/<int:search_id>')
def history_results(search_id):
    """Get results for a specific search."""
    history_manager = HistoryManager()
    results = history_manager.get_search_results(search_id)
    return jsonify(results)


@app.route('/stats')
def stats():
    """Get statistics."""
    history_manager = HistoryManager()
    stats = history_manager.get_stats()
    return jsonify(stats)


def run_web(host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
    """Run the web server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web(debug=True)
