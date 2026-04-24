"""Bibliography export format for Research-Collector."""

from pathlib import Path
from typing import Dict, Any


class BibliographyExporter:
    """Export results to BibTeX format."""
    
    def export(self, results: Dict[str, Any], output_path: str) -> None:
        """Export results to BibTeX file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        bibtex_content = self._format_bibtex(results)
        
        with open(output_file, 'w') as f:
            f.write(bibtex_content)
    
    def _format_bibtex(self, results: Dict[str, Any]) -> str:
        """Format results as BibTeX."""
        lines = []
        
        for i, item in enumerate(results['items']):
            entry_id = f"ref{i}"
            lines.append(f"@article{{{entry_id},")
            lines.append(f"  title = {{{item['title']}}},")
            lines.append(f"  author = {{{item['author']}}},")
            lines.append(f"  year = {{{item['published_date'][:4]}}},")
            lines.append(f"  url = {{{item['url']}}}")
            lines.append(f"}}")
            lines.append("")
        
        return '\n'.join(lines)