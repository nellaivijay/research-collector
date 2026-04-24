"""Markdown export format for Research-Collector."""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class MarkdownExporter:
    """Export results to Markdown format."""
    
    def export(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Export results to Markdown file.
        
        Args:
            results: Research results dictionary
            output_path: Path to output file
        """
        md_content = self._format_markdown(results)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(md_content)
    
    def _format_markdown(self, results: Dict[str, Any]) -> str:
        """Format results as Markdown."""
        lines = [
            f"# Research Results: {results['topic']}",
            f"",
            f"**Date Range:** {results['from_date']} to {results['to_date']}",
            f"**Sources:** {', '.join(results['sources_used'])}",
            f"**Total Items:** {results['metadata']['total_items']}",
            f"",
            f"## Results",
            f"",
        ]
        
        for item in results['items']:
            lines.append(f"### {item['title']}")
            lines.append(f"**Source:** {item['source']}")
            lines.append(f"**URL:** {item['url']}")
            lines.append(f"**Author:** {item['author']}")
            lines.append(f"**Date:** {item['published_date']}")
            lines.append(f"**Score:** {item.get('score', 0):.2f}")
            lines.append(f"")
            lines.append(f"{item['content']}")
            lines.append(f"")
        
        return '\n'.join(lines)