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
                    # Handle nested dictionaries and lists
                    if isinstance(value, (dict, list)):
                        import json
                        row[f"metadata_{key}"] = json.dumps(value)
                    else:
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
        
        # Calculate size category based on total items
        total_items = metadata['total_items']
        if total_items < 1000:
            size_category = "n<1K"
        elif total_items < 10000:
            size_category = "1K<n<10K"
        elif total_items < 100000:
            size_category = "10K<n<100K"
        else:
            size_category = "100K<n"
        
        card_content = f"""---
license: mit
task_categories:
- text-retrieval
- information-retrieval
- text-classification
language:
- en
- multilingual
tags:
- research
- academic
- data-collection
- multi-source
- machine-learning
- ai
pretty_name: Research Collector Dataset
size_categories:
- {size_category}
---

# Research Collector Dataset

This dataset contains research results aggregated from multiple sources by the Research-Collector tool. Each item is enriched with comprehensive metadata, ML subfield classifications, quality scores, and temporal features.

## Dataset Details

- **Topic**: {metadata['topic']}
- **Time Range**: {metadata['from_date']} to {metadata['to_date']}
- **Sources**: {', '.join(metadata['sources_used'])}
- **Total Items**: {metadata['total_items']}
- **Exported At**: {metadata['exported_at']}

## Dataset Structure

### Core Fields
- `id`: Unique identifier
- `title`: Title of the research item
- `source`: Source platform (e.g., pubmed, arxiv, github, reddit, stackoverflow)
- `url`: URL to original content
- `author`: Author(s)
- `published_date`: Publication date (ISO 8601 format)
- `citations`: Number of citations (if available)
- `upvotes`: Number of upvotes (if available)
- `downloads`: Number of downloads (if available)
- `comments`: Number of comments (if available)
- `content`: Content/abstract/description
- `score`: Relevance score

### Enriched Metadata Fields
- `metadata_year`: Publication year
- `metadata_month`: Publication month
- `metadata_day`: Publication day
- `metadata_week`: Week of year
- `metadata_quarter`: Quarter of year
- `metadata_days_since`: Days since publication
- `metadata_ml_subfields`: ML subfield classifications (JSON array)
- `metadata_subfield_count`: Number of ML subfields
- `metadata_keywords`: Extracted keywords (JSON array)
- `metadata_keyword_count`: Number of keywords
- `metadata_quality_scores`: Quality score metrics (JSON dict)
- `metadata_content_type`: Content type (paper, preprint, repository, discussion, qa, news)
- `metadata_has_code`: Whether item contains code
- `metadata_has_doi`: Whether item has DOI

### Source-Specific Metadata
- **PubMed**: `metadata_journal`, `metadata_doi`, `metadata_mesh_terms`, `metadata_publication_types`, `metadata_abstract_length`
- **arXiv**: `metadata_arxiv_id`, `metadata_primary_category`, `metadata_categories`, `metadata_journal_ref`
- **GitHub**: `metadata_stars`, `metadata_forks`, `metadata_language`, `metadata_license`, `metadata_topics`, `metadata_has_readme`
- **Reddit**: `metadata_subreddit`, `metadata_link_flair_text`, `metadata_upvote_ratio`, `metadata_total_awards`, `metadata_is_gilded`
- **Stack Overflow**: `metadata_tags`, `metadata_answer_count`, `metadata_has_accepted_answer`, `metadata_view_count`, `metadata_owner_reputation`
- **Semantic Scholar**: `metadata_citation_count`, `metadata_influential_citation_count`, `metadata_fields_of_study`, `metadata_has_open_access`

## Usage Examples

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("{repo_id}")
train_data = dataset["train"]

# Filter by source
pubmed_items = train_data.filter(lambda x: x["source"] == "pubmed")
github_items = train_data.filter(lambda x: x["source"] == "github")

# Filter by content type
papers = train_data.filter(lambda x: x.get("metadata_content_type") == "paper")
repositories = train_data.filter(lambda x: x.get("metadata_content_type") == "repository")

# Filter by ML subfield
cv_papers = train_data.filter(lambda x: "computer-vision" in x.get("metadata_ml_subfields", []))

# Filter by quality
high_quality = train_data.filter(lambda x: x.get("metadata_quality_scores", {{}}).get("overall_quality_score", 0) > 0.7)

# Sort by score
sorted_items = train_data.sort("score", reverse=True)

# Filter by date
recent_items = train_data.filter(lambda x: x.get("metadata_days_since", 999) < 30)
```

## Data Quality Features

- **Standardized Dates**: All dates normalized to ISO 8601 format
- **ML Subfield Classification**: Automatic classification into 15+ ML subfields
- **Quality Scoring**: Multi-dimensional quality assessment (abstract length, code availability, DOI, engagement, recency)
- **Temporal Features**: Year, month, week, quarter, days since publication
- **Keyword Extraction**: Automatic extraction of technical keywords
- **Content Type Detection**: Automatic classification of item type

## Data Sources

This dataset aggregates research from:
- **Academic**: PubMed, arXiv, Semantic Scholar, Crossref, Papers with Code
- **Professional**: GitHub, Stack Overflow
- **Social**: Reddit, Hacker News
- **News**: GDELT

## Limitations

- Data is limited to the specified time range
- Some sources may have rate limits or API restrictions
- Citation counts may vary between sources
- ML subfield classification is based on keyword matching and may not be perfect

## Source

Generated by [Research-Collector](https://github.com/nellaivijay/research-collector), an educational multi-source research aggregation tool.

## License

MIT License

## Citation

If you use this dataset, please cite:
```bibtex
@dataset{{research_collector_{metadata['topic'].lower().replace(' ', '_')}_2026,
  author = {{Research-Collector}},
  title = {{{metadata['topic']} Research Dataset}},
  year = {{2026}},
  publisher = {{Hugging Face}},
  howpublished = {{https://huggingface.co/datasets/{repo_id}}}
}}
```
"""
        
        # Upload dataset card
        api.upload_file(
            path_or_fileobj=card_content.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            token=self.token
        )
