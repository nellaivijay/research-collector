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
            
            # Check if any item has URLs
            has_urls = any('url' in item for item in results['items'])
            
            # Write header
            if has_urls:
                writer.writerow(['Title', 'URL', 'Source', 'Author', 'Date', 'Score'])
            else:
                writer.writerow(['Title', 'Source', 'Author', 'Date', 'Score'])
            
            # Write data
            for item in results['items']:
                if has_urls:
                    writer.writerow([
                        item['title'],
                        item.get('url', ''),
                        item['source'],
                        item['author'],
                        item['published_date'],
                        item.get('score', 0)
                    ])
                else:
                    writer.writerow([
                        item['title'],
                        item['source'],
                        item['author'],
                        item['published_date'],
                        item.get('score', 0)
                    ])