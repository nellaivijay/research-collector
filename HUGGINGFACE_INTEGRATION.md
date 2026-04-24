# Hugging Face Datasets Integration

This document describes the Hugging Face Datasets integration for Research-Collector.

## Overview

Research-Collector can export research results directly to Hugging Face Datasets, enabling:
- Easy sharing with the ML community
- Version control for research datasets
- Integration with Hugging Face ecosystem
- Collaborative research workflows

## Installation

### Option 1: Install with pip extras

```bash
pip install -e ".[huggingface]"
```

### Option 2: Install manually

```bash
pip install huggingface_hub>=0.19.0
pip install datasets>=2.14.0
```

### Option 3: Install all optional features

```bash
pip install -e ".[all]"
```

## Setup

### 1. Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read/write access for datasets)
3. Copy the token

### 2. Set Token

**Option A: Environment Variable**
```bash
export HF_TOKEN=your_token_here
```

**Option B: Pass as Parameter**
```bash
--hf-token your_token_here
```

**Option C: Hugging Face CLI**
```bash
huggingface-cli login
```

## Usage

### Basic Export

```bash
python -m research_collector research \
  --query "machine learning" \
  --export=huggingface \
  --output username/dataset-name
```

### With Token Parameter

```bash
python -m research_collector research \
  --query "AI safety" \
  --export=huggingface \
  --output username/ai-safety-research \
  --hf-token $HF_TOKEN
```

### With Predefined Topic

```bash
python -m research_collector research \
  --topic ml \
  --export=huggingface \
  --output username/ml-research \
  --days 30
```

### With Specific Sources

```bash
python -m research_collector research \
  --query "climate change" \
  --sources pubmed,crossref,semantic_scholar \
  --export=huggingface \
  --output username/climate-research
```

## Dataset Structure

The exported dataset contains the following fields:

### Core Fields
- `id`: Unique identifier for the research item
- `title`: Title of the research item
- `source`: Source platform (e.g., pubmed, reddit, stackoverflow)
- `url`: URL to original content
- `author`: Author(s) of the research item
- `published_date`: Publication date
- `content`: Content or abstract
- `score`: Relevance score (0.0 to 1.0)

### Engagement Metrics
- `citations`: Number of citations
- `upvotes`: Number of upvotes
- `downloads`: Number of downloads
- `comments`: Number of comments

### Metadata Fields
Additional fields prefixed with `metadata_` containing source-specific metadata.

## Dataset Card

The integration automatically generates a dataset card (README.md) with:
- Dataset metadata (topic, time range, sources)
- Dataset structure description
- Usage examples
- License information
- Source attribution

## Accessing Your Dataset

### Using Python

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("username/dataset-name")
train_data = dataset["train"]

# View first item
print(train_data[0])

# Filter by source
pubmed_items = train_data.filter(lambda x: x["source"] == "pubmed")

# Sort by score
sorted_items = train_data.sort("score", reverse=True)

# Get high-scoring items
high_score = train_data.filter(lambda x: x["score"] > 0.8)

# Convert to pandas
df = train_data.to_pandas()
```

### Using Hugging Face Hub

Visit https://huggingface.co/datasets/username/dataset-name to:
- View dataset card
- Browse dataset files
- Use dataset viewer
- Download dataset
- View version history

## Version Control

Each export creates a new version on the Hub:

```bash
# First export creates v1.0.0
python -m research_collector research --query "ML" --export=huggingface --output user/ml-dataset

# Second export creates v1.0.1
python -m research_collector research --query "ML" --export=huggingface --output user/ml-dataset
```

## Privacy Considerations

- **Public Datasets**: By default, datasets are public on Hugging Face Hub
- **Private Datasets**: Upgrade to Hugging Face Pro for private datasets
- **Sensitive Data**: Review content before exporting to public Hub
- **API Keys**: Never include API keys in exported datasets

## Use Cases

### 1. Research Collaboration
Share research datasets with collaborators:
```bash
python -m research_collector research \
  --query "quantum computing" \
  --export=huggingface \
  --output research-group/quantum-computing
```

### 2. Educational Resources
Create datasets for teaching:
```bash
python -m research_collector research \
  --topic llm \
  --export=huggingface \
  --output education/llm-resources
```

### 3. Literature Review
Systematic literature review datasets:
```bash
python -m research_collector research \
  --query "transformer architecture" \
  --sources academic \
  --export=huggingface \
  --output user/transformer-review
```

### 4. Trend Analysis
Track trends over time:
```bash
# Create monthly datasets
for month in {1..12}; do
  python -m research_collector research \
    --query "AI ethics" \
    --days 30 \
    --export=huggingface \
    --output user/ai-ethics-$(date +%Y-%m)
done
```

## Troubleshooting

### Import Error
```
ImportError: huggingface_hub and datasets libraries not installed
```
**Solution**: Install with `pip install -e ".[huggingface]"`

### Authentication Error
```
OSError: Couldn't connect to the Hub
```
**Solution**: Check your HF_TOKEN is set correctly

### Repository Not Found
```
Repo not found or access denied
```
**Solution**: 
- Verify repo ID format (username/dataset-name)
- Check you have write access to the repository
- Create the repository first on Hugging Face Hub

### Rate Limiting
```
Rate limit exceeded
```
**Solution**: Wait a few minutes before exporting again

## Advanced Usage

### Custom Dataset Card

Modify the `_update_dataset_card` method in `huggingface.py` to customize the dataset card template.

### Metadata Enhancement

Add custom metadata fields by modifying the `_convert_to_dataset` method.

### Batch Export

Export multiple topics programmatically:

```python
from research_collector.pipeline import Pipeline
from research_collector.config import Config
from research_collector.exporters.huggingface import HuggingFaceExporter

config = Config()
pipeline = Pipeline(config)
exporter = HuggingFaceExporter(token="your_token")

topics = ["machine learning", "AI safety", "LLM"]
for topic in topics:
    results = pipeline.run(topic, ...)
    exporter.export(results, f"username/{topic.replace(' ', '-')}-dataset")
```

## Best Practices

1. **Descriptive Repository Names**: Use clear, descriptive names (e.g., `user/ml-survey-2024`)
2. **Regular Updates**: Update datasets periodically for fresh research
3. **Version Tags**: Use semantic versioning for major updates
4. **Documentation**: Add custom documentation to dataset cards
5. **Citation**: Include citation information in dataset card
6. **License**: Choose appropriate license for your dataset

## Integration with Other Tools

### Datasets Library
```python
from datasets import load_dataset
dataset = load_dataset("user/dataset")
```

### Transformers
```python
from transformers import AutoModel, AutoTokenizer
# Use your research dataset for training/fine-tuning
```

### Hub Integration
- Automatic dataset viewer
- Dataset cards with rich formatting
- Community discussions
- Citation tracking

## Resources

- [Hugging Face Datasets Documentation](https://huggingface.co/docs/datasets/)
- [Hugging Face Hub Guide](https://huggingface.co/docs/hub/)
- [Dataset Cards Guide](https://huggingface.co/docs/hub/datasets-cards)
- [Research-Collector Documentation](./README.md)
- [GitHub Actions Integration](./GITHUB_ACTIONS.md) - Automated daily research to Hugging Face

## GitHub Actions Integration

Research-Collector includes GitHub Actions workflows for automated daily research export to Hugging Face Datasets.

### Current Setup
- **Daily Schedule**: Midnight UTC
- **Topics**: ML, LLM, AGI, ASI, ANI, ACI (6 topics)
- **Datasets**:
  - `nellaivijay/ml-research-daily`
  - `nellaivijay/llm-research-daily`
  - `nellaivijay/agi-research-daily`
  - `nellaivijay/asi-research-daily`
  - `nellaivijay/ani-research-daily`
  - `nellaivijay/aci-research-daily`
- **Manual Triggers**: Available for custom research on any topic

See [GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md) for complete setup and usage instructions.
