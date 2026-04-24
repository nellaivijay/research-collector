"""Hugging Face Datasets exporter for Research-Collector."""

from typing import Dict, List, Any, Optional
from datetime import datetime


class HuggingFaceExporter:
    """Export research results to Hugging Face Datasets."""
    
    def __init__(self, repo_id: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Hugging Face exporter.
        
        Args:
            repo_id: Hugging Face repository ID (username/dataset-name)
            token: Hugging Face authentication token
        """
        self.repo_id = repo_id
        self.token = token
        
        try:
            from datasets import Dataset, DatasetDict
            from huggingface_hub import HfApi
            self.Dataset = Dataset
            self.DatasetDict = DatasetDict
            self.HfApi = HfApi
            self.available = True
        except ImportError:
            self.available = False
    
    def export(self, results: Dict[str, Any], output_path: str = None) -> None:
        """
        Export results to Hugging Face Datasets.
        
        Args:
            results: Research results dictionary
            output_path: Repository ID (format: username/dataset-name)
        """
        if not self.available:
            raise ImportError(
                "huggingface_hub and datasets libraries not installed. "
                "Install with: pip install huggingface_hub datasets"
            )
        
        # Use output_path as repo_id if provided, otherwise use instance repo_id
        repo_id = output_path or self.repo_id
        
        if not repo_id:
            raise ValueError("Repository ID required (format: username/dataset-name)")
        
        # Validate token if provided
        if self.token and not self.token.strip():
            raise ValueError("Hugging Face token is empty. Please provide a valid token.")
        
        # Convert results to dataset format
        dataset = self._convert_to_dataset(results)
        
        # Create DatasetDict with train split
        dataset_dict = self.DatasetDict({
            "train": dataset
        })
        
        # Add metadata
        metadata = {
            "topic": results.get("topic", "unknown"),
            "from_date": results.get("from_date", ""),
            "to_date": results.get("to_date", ""),
            "sources_used": results.get("sources_used", []),
            "total_items": len(results.get("items", [])),
            "exported_at": datetime.now().isoformat()
        }
        
        # Push to Hub
        print(f"Pushing dataset to Hugging Face Hub: {repo_id}")
        try:
            dataset_dict.push_to_hub(
                repo_id=repo_id,
                token=self.token,
                commit_message=f"Research results for {metadata['topic']}"
            )
            
            # Update dataset card
            self._update_dataset_card(repo_id, metadata)
            
            print(f"Dataset successfully pushed to: https://huggingface.co/datasets/{repo_id}")
        except Exception as e:
            if "Bearer" in str(e) and "Illegal header value" in str(e):
                raise ValueError(
                    "Invalid Hugging Face token. Please check that HF_TOKEN is set correctly "
                    "in your environment or GitHub Secrets."
                ) from e
            raise
    
    def _convert_to_dataset(self, results: Dict[str, Any]) -> 'Dataset':
        """Convert research results to Hugging Face Dataset format.
        
        Args:
            results: Research results dictionary
        
        Returns:
            Hugging Face Dataset
        """
        items = results.get("items", [])
        
        # Flatten items into dataset rows
        dataset_rows = []
        for item in items:
            row = {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "author": item.get("author", ""),
                "published_date": item.get("published_date", ""),
                "citations": item.get("citations", 0),
                "upvotes": item.get("upvotes", 0),
                "downloads": item.get("downloads", 0),
                "comments": item.get("comments", 0),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0),
            }
            
            # Add metadata fields if present
            if "metadata" in item:
                for key, value in item["metadata"].items():
                    row[f"metadata_{key}"] = value
            
            dataset_rows.append(row)
        
        return self.Dataset.from_list(dataset_rows)
    
    def _update_dataset_card(self, repo_id: str, metadata: Dict) -> None:
        """Update the dataset card with research metadata.
        
        Args:
            repo_id: Repository ID
            metadata: Research metadata
        """
        api = self.HfApi(token=self.token)
        
        card_content = f"""---
license: mit
task_categories:
- text-retrieval
- information-retrieval
language:
- en
- multilingual
tags:
- research
- academic
- data-collection
- multi-source
pretty_name: Research Collector Dataset
size_categories:
- n<1K
---

# Research Collector Dataset

This dataset contains research results aggregated from multiple sources by the Research-Collector tool.

## Dataset Details

- **Topic**: {metadata['topic']}
- **Time Range**: {metadata['from_date']} to {metadata['to_date']}
- **Sources**: {', '.join(metadata['sources_used'])}
- **Total Items**: {metadata['total_items']}
- **Exported At**: {metadata['exported_at']}

## Dataset Structure

Each item contains:
- `id`: Unique identifier
- `title`: Title of the research item
- `source`: Source platform (e.g., pubmed, reddit, stackoverflow)
- `url`: URL to original content
- `author`: Author(s)
- `published_date`: Publication date
- `citations`: Number of citations (if available)
- `upvotes`: Number of upvotes (if available)
- `downloads`: Number of downloads (if available)
- `comments`: Number of comments (if available)
- `content`: Content/abstract
- `score`: Relevance score
- Additional metadata fields as `metadata_*`

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{repo_id}")
train_data = dataset["train"]

# Example: Filter by source
pubmed_items = train_data.filter(lambda x: x["source"] == "pubmed")

# Example: Sort by score
sorted_items = train_data.sort("score", reverse=True)
```

## Source

Generated by [Research-Collector](https://github.com/yourusername/research-collector), an educational multi-source research aggregation tool.

## License

MIT License
"""
        
        # Upload dataset card
        api.upload_file(
            path_or_fileobj=card_content.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            token=self.token
        )
