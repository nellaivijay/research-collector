"""CSV export format for Research-Collector."""

import csv
from pathlib import Path
from typing import Dict, Any


class CSVExporter:
    """Export results to CSV format."""
    
    def export(self, results: Dict[str, Any], output_path: str) -> None:
        """Export results to CSV file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Title', 'URL', 'Source', 'Author', 'Date', 'Score'])
            
            # Write data
            for item in results['items']:
                writer.writerow([
                    item['title'],
                    item['url'],
                    item['source'],
                    item['author'],
                    item['published_date'],
                    item.get('score', 0)
                ])