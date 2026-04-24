"""HTML exporter for Research-Collector."""

from typing import Dict, List, Any
from datetime import datetime


class HTMLExporter:
    """Export research results to HTML format."""
    
    def export(self, results: Dict[str, Any], output_path: str = None) -> None:
        """
        Export results to HTML.
        
        Args:
            results: Research results dictionary
            output_path: Path to output file (None for stdout)
        """
        html = self._generate_html(results)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        else:
            print(html)
    
    def _generate_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML from results.
        
        Args:
            results: Research results dictionary
        
        Returns:
            HTML string
        """
        topic = results.get('topic', 'Unknown')
        from_date = results.get('from_date', '')
        to_date = results.get('to_date', '')
        items = results.get('items', [])
        metadata = results.get('metadata', {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Results: {topic}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .meta {{
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.9em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .results {{
            display: grid;
            gap: 20px;
        }}
        .result-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .result-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }}
        .result-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #333;
        }}
        .result-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .meta-tag {{
            background: #f0f0f0;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            color: #666;
        }}
        .source-tag {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }}
        .result-content {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        .result-metrics {{
            display: flex;
            gap: 20px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        .metric {{
            display: flex;
            align-items: center;
            gap: 5px;
            color: #666;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-weight: bold;
            color: #667eea;
        }}
        .score-badge {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .result-card {{
            position: relative;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .header {{
                padding: 20px;
            }}
            .stats {{
                grid-template-columns: 1fr;
            }}
            .result-meta {{
                flex-direction: column;
                gap: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Research Results: {topic}</h1>
        <div class="meta">
            <span>📅 {from_date} to {to_date}</span>
            <span>•</span>
            <span>📊 {len(items)} results found</span>
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Total Results</h3>
            <div class="value">{len(items)}</div>
        </div>
        <div class="stat-card">
            <h3>Sources Used</h3>
            <div class="value">{len(metadata.get('source_counts', {}))}</div>
        </div>
        <div class="stat-card">
            <h3>Average Score</h3>
            <div class="value">{self._calculate_average_score(items):.2f}</div>
        </div>
    </div>
    
    <div class="results">
"""
        
        for item in items:
            html += self._generate_result_card(item)
        
        html += """    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #999; font-size: 0.9em;">
        <p>Generated by Research-Collector • """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </footer>
</body>
</html>"""
        
        return html
    
    def _generate_result_card(self, item: Dict) -> str:
        """Generate HTML for a single result card.
        
        Args:
            item: Result item dictionary
        
        Returns:
            HTML string
        """
        title = item.get('title', 'No title')
        source = item.get('source', 'Unknown')
        author = item.get('author', 'Unknown author')
        published_date = item.get('published_date', 'Unknown date')
        content = item.get('content', '')[:300] + '...' if len(item.get('content', '')) > 300 else item.get('content', '')
        score = item.get('score', 0)
        citations = item.get('citations', 0)
        upvotes = item.get('upvotes', 0)
        
        html = f"""
        <div class="result-card">
            <div class="score-badge">{score:.2f}</div>
            <h2 class="result-title">{title}</h2>
            <div class="result-meta">
                <span class="source-tag">{source}</span>
                <span class="meta-tag">👤 {author}</span>
                <span class="meta-tag">📅 {published_date}</span>
            </div>
            <div class="result-content">
                {content}
            </div>
            <div class="result-metrics">
                <div class="metric">
                    <span>📚</span>
                    <span class="metric-value">{citations}</span>
                    <span>citations</span>
                </div>
                <div class="metric">
                    <span>👍</span>
                    <span class="metric-value">{upvotes}</span>
                    <span>upvotes</span>
                </div>
            </div>
        </div>
"""
        return html
    
    def _calculate_average_score(self, items: List[Dict]) -> float:
        """Calculate average score across items.
        
        Args:
            items: List of result items
        
        Returns:
            Average score
        """
        if not items:
            return 0.0
        
        scores = [item.get('score', 0) for item in items]
        return sum(scores) / len(scores)
