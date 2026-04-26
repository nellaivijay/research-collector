# Research-Collector

**Educational multi-source research aggregation tool for learning and teaching**

Research-Collector is an open source educational tool designed to help students and researchers aggregate information from diverse sources including academic databases, professional Q&A sites, news outlets, and social platforms. It provides comprehensive research insights with engagement-based ranking and flexible time windows.

## Educational Purpose

This tool serves educational purposes by helping students and researchers:
- Learn about research methodologies and data aggregation techniques
- Understand how different sources provide different perspectives on topics
- Explore engagement-based ranking algorithms versus SEO-based approaches
- Practice data analysis and visualization skills
- Study information retrieval and normalization techniques
- Gain hands-on experience with multi-source data integration

## Key Features

- **Multi-Source Integration**: 15+ data sources including academic (PubMed, Crossref, Papers With Code, INSPIRE-HEP), professional (Stack Overflow), social (Reddit), and news (GDELT)
- **Flexible Time Windows**: Research any time period from 3 days to 365 days, or custom ranges
- **Engagement-Based Ranking**: Results scored by citations, upvotes, answers, and downloads rather than SEO
- **Cross-Platform Clustering**: Merges duplicate stories across multiple sources into unified insights
- **Multiple Export Formats**: Markdown, JSON, CSV, HTML, BibTeX, and Hugging Face Datasets
- **Local-First Privacy**: All processing happens locally to maintain data privacy
- **Extensible Architecture**: Plugin system for custom sources and scoring algorithms
- **Comprehensive Documentation**: Educational examples and explanations

## Advanced Features

### Domain-Specific Scoring
Configure weighted keywords (1-6 scale) for research domains to improve result relevance:
```yaml
scoring:
  keyword_weights:
    # Core research terms (highest weight)
    "artificial general intelligence": 6
    "large language model": 6
    # Important concepts (medium weight)
    "world models": 5
    "reasoning": 5
    # Supporting concepts (lower weight)
    "meta-learning": 4
    "causal reasoning": 4
```

### Author/Researcher Boosting
Track preferred researchers to prioritize their publications:
```yaml
scoring:
  preferred_researchers:
    - "Researcher Name"
    - "Another Researcher"
```

### Seen Papers Cache
Prevent duplicate processing with automatic paper tracking and configurable time-to-live:
```yaml
advanced:
  enable_seen_papers_cache: true
  seen_papers_cache_ttl_days: 30
```

### Full-Text Extraction
Extract full text from academic papers for improved similarity scoring (resource-intensive):
```yaml
advanced:
  enable_fulltext_extraction: true
```

### Enhanced Topic Management
Organize research topics with priorities, descriptions, and comprehensive keywords:
```yaml
predefined_topics:
  research_topic:
    name: "Research Topic Name"
    priority: "high"
    description: "Description of research focus"
    keywords:
      - "keyword1"
      - "keyword2"
```

### GitHub Actions Optimization
Multi-layer caching strategy for faster automated runs and reduced computational costs

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/nellaivijay/research-collector.git
cd research-collector

# Install dependencies
pip install -r requirements.txt

# Run research with default settings
python -m research_collector research --query "machine learning"
```

### Basic Usage

```bash
# Research with default settings (7-day window)
python -m research_collector research --query "research topic"

# Use predefined topic
python -m research_collector research --topic ml

# List all available predefined topics
python -m research_collector topics

# Custom time range
python -m research_collector research --query "research topic" --days=15

# Specific sources only
python -m research_collector research --query "research topic" --sources=pubmed,crossref

# Export to different formats
python -m research_collector research --query "research topic" --export=json
python -m research_collector research --query "research topic" --export=csv

# Export to Hugging Face Datasets
python -m research_collector research --query "research topic" --export=huggingface --output username/dataset-name
```

## Predefined Research Topics

### Available Topics

- **agi**: Artificial General Intelligence (world models, frontier models, reasoning, cognitive architecture)
- **aci**: Artificial Collective Intelligence (multi-agent systems, swarm intelligence, agent coordination)
- **asi**: Artificial Super Intelligence (superintelligence, AI alignment, existential risk, governance)
- **physical_ai**: Physical & Embodied AI (robotics, embodied cognition, spatial intelligence, sim-to-real transfer)
- **compute_infra**: Next-Gen Compute & Accelerators (LPUs, AI accelerators, neuromorphic computing, hardware-software co-design)
- **ml**: Machine Learning (deep learning, state space models, diffusion models, federated learning)
- **llm**: Large Language Models & Context Scaling (long context window, RAG, mixture of experts, agents, tool use)

### Using Predefined Topics

```bash
# List all available topics
python -m research_collector topics

# Research using a predefined topic
python -m research_collector research --topic agi

# Combine with other options
python -m research_collector research --topic ml --days=30 --sources=academic
```

### Customizing Topics

Add custom predefined topics in the configuration file:

```yaml
predefined_topics:
  custom_topic:
    name: "Custom Research Topic"
    priority: "high"
    description: "Description of research interest"
    keywords:
      - "keyword1"
      - "keyword2"
      - "keyword3"
```

### Topic Configuration

Topics can be assigned priorities to influence research importance:
- **high**: Primary research focus areas
- **medium**: Secondary interest areas
- **low**: Supplementary areas

Keyword weights use a 1-6 relevance scale:
- **6**: Core topic terms (highest priority)
- **5**: Very important concepts and methodologies
- **4**: Important related concepts
- **3**: Supporting technologies and approaches
- **2**: Peripheral but relevant concepts

## Source Categories

### Academic Sources
- **PubMed**: Medical and life sciences literature
- **Crossref**: Academic metadata and citation tracking
- **Papers With Code**: ML papers with code implementations
- **Semantic Scholar**: Academic papers and citations
- **arXiv**: Preprint server for physics, CS, math, and related fields
- **INSPIRE-HEP**: High-energy physics literature database

### Professional Sources
- **Stack Overflow**: Technical Q&A and programming solutions
- **GitHub**: Code repositories and development activity
- **Kaggle**: Data science competitions and datasets

### Social Sources
- **Reddit**: Community discussions and opinions
- **Hacker News**: Technology news and discussions

### News Sources
- **GDELT**: Global news database
- **NewsAPI**: News articles (requires API key)

## Use Cases

### Academic Research
```bash
# Literature review with citation tracking
python -m research_collector research --query "research method" --sources=academic --min-citations=20

# Export bibliography
python -m research_collector research --query "research area" --export=bibliography --days=90

# Use predefined topic
python -m research_collector research --topic agi --sources=academic --days=90
```

### Technical Research
```bash
# Evaluate technology with community sentiment
python -m research_collector research --query "technology comparison" --sources=social,professional

# Check implementation approaches
python -m research_collector research --query "specific technique" --sources=stackoverflow,github
```

### Market Intelligence
```bash
# Industry trend analysis
python -m research_collector research --query "industry trend" --sources=news,academic --days=90

# Competitive landscape
python -m research_collector research --query "company comparison" --sources=all
```

## Configuration

Create a `research-collector.yaml` configuration file:

```yaml
sources:
  academic:
    pubmed: true
    crossref: true
    semantic_scholar: true
    paperswithcode: true
    arxiv: true
    inspire_hep: true
  professional:
    stackoverflow: true
    github: true
    kaggle: true
  social:
    reddit: true
    hackernews: true
  news:
    gdelt: true
    newsapi: false

time_ranges:
  default: 7
  quick: 3
  standard: 15
  deep: 30
  historical: 90
  extended: 365

exports:
  default: markdown
  directory: ~/research_outputs
  include_metadata: true

scoring:
  weights:
    relevance: 0.4
    recency: 0.3
    engagement: 0.3
  
  preferred_researchers:
    - "Researcher Name"
  
  keyword_weights:
    "research term": 6
    "important concept": 5

predefined_topics:
  research_topic:
    name: "Research Topic"
    priority: "high"
    description: "Research description"
    keywords:
      - "keyword1"
      - "keyword2"

advanced:
  max_results_per_source: 100
  clustering_similarity_threshold: 0.85
  enable_caching: true
  cache_ttl_hours: 24
  enable_seen_papers_cache: true
  seen_papers_cache_ttl_days: 30
  enable_fulltext_extraction: false

api_keys:
  # Optional: Add API keys for enhanced rate limits
  # pubmed: ${PUBMED_API_KEY}
  # crossref: ${CROSSREF_API_KEY}
  # semantic_scholar: ${SEMANTIC_SCHOLAR_API_KEY}
  # newsapi: ${NEWSAPI_API_KEY}
  # stackexchange: ${STACKEXCHANGE_API_KEY}
  # reddit: ${REDDIT_CLIENT_ID}
  # reddit_secret: ${REDDIT_CLIENT_SECRET}
  # reddit_user_agent: ${REDDIT_USER_AGENT}
  # kaggle_username: ${KAGGLE_USERNAME}
  # kaggle_key: ${KAGGLE_KEY}
```

## Hugging Face Integration

Research-Collector supports exporting results to Hugging Face Datasets for sharing and collaboration.

### Setup

1. Install Hugging Face dependencies:
```bash
pip install -e ".[huggingface]"
```

2. Get Hugging Face token from https://huggingface.co/settings/tokens

3. Set the token as environment variable:
```bash
export HF_TOKEN=your_hf_token_here
```

### Usage

```bash
# Export to Hugging Face Datasets
python -m research_collector research \
  --query "research topic" \
  --export=huggingface \
  --output username/dataset-name \
  --hf-token $HF_TOKEN
```

## Architecture

Research-Collector uses a modular pipeline architecture:

```
Query → Planning → Multi-Source Search → Normalization → Scoring → Ranking → Clustering → Export
```

### Core Components

- **Source Modules**: Each data source has its own module with search and parsing logic
- **Pipeline**: Orchestrates parallel searches and data processing
- **Normalizers**: Convert source-specific formats to unified schema
- **Scoring Engine**: Multi-dimensional scoring (relevance, recency, engagement)
- **Clustering**: Merge duplicate stories across sources
- **Cache System**: API response caching and seen papers tracking

## Project Structure

```
research-collector/
├── research_collector/          # Main package
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── pipeline.py             # Search orchestration
│   ├── scoring.py             # Scoring algorithms
│   ├── normalization.py       # Data normalization
│   ├── clustering.py          # Deduplication
│   ├── fulltext.py            # Full-text extraction
│   ├── seen_papers.py         # Paper deduplication cache
│   ├── sources/               # Source modules
│   └── exporters/             # Export formats
├── config/                    # Configuration files
│   └── research-collector.yaml.template
├── .github/workflows/         # GitHub Actions workflows
├── tests/                     # Test suite
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Adding New Sources

Create a new source module in `research_collector/sources/` following the existing pattern.

### Testing

Run the test suite:
```bash
pytest tests/
```

## License

MIT License - See LICENSE file for details.

## Educational Use

This tool is provided for educational purposes to help students and researchers learn about:
- Data aggregation from multiple sources
- Information retrieval and normalization techniques
- Engagement-based ranking algorithms
- Research methodologies and best practices