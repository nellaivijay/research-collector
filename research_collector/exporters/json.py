"""JSON export format for Research-Collector."""

import json
from pathlib import Path
from typing import Dict, Any


class JSONExporter:
    """Export results to JSON format."""
    
    def export(self, results: Dict[str, Any], output_path: str) -> None:
        """Export results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)