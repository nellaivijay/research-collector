# Research-Collector

**Educational multi-source research aggregation tool for learning and teaching**

Research-Collector is an open source educational tool that helps students and researchers aggregate information from diverse sources - academic databases, professional Q&A sites, news outlets, and social platforms - to provide comprehensive research insights with engagement-based ranking and flexible time windows.

## Educational Purpose

This tool is designed for educational purposes to help students and researchers:
- Learn about research methodologies and data aggregation
- Understand how different sources provide different perspectives on topics
- Explore engagement-based ranking algorithms
- Practice data analysis and visualization
- Study information retrieval and normalization techniques

## Key Features

- **15+ Data Sources**: Academic (PubMed, Crossref, Papers With Code, INSPIRE-HEP), Professional (Stack Overflow), Social (Reddit), News (GDELT)
- **Flexible Time Windows**: Research any time period - last 3 days, 7 days (default), 15 days, 30 days, 90 days, 365 days, or custom ranges
- **Engagement-Based Ranking**: Results scored by citations, upvotes, answers, downloads - not SEO
- **Cross-Platform Clustering**: Same story across multiple sources merged into unified insights
- **Multiple Export Formats**: Markdown, JSON, CSV, HTML, BibTeX, and Hugging Face Datasets for sharing and collaboration
- **Local-First Privacy**: All processing happens locally, your research stays private
- **Extensible Architecture**: Plugin system for custom sources and scoring algorithms
- **Educational Documentation**: Comprehensive examples and explanations for learning

## Recent Updates

### 🚀 Advanced Research Features (Latest)
- **Domain-Specific Scoring**: 120+ weighted keywords across 7 research topics with 1-6 relevance scale
- **Collaborator Boosting**: Track preferred researchers with automatic 2x score multiplier
- **Seen Papers Cache**: Prevent duplicate processing with configurable TTL and GitHub Actions persistence
- **Full-Text Extraction**: Extract arXiv paper content and figure captions for better similarity scoring
- **Enhanced Topics**: 7 modern AI research topics (AGI, ACI, ASI, Physical AI, Compute Infra, ML, LLM)
- **INSPIRE-HEP Integration**: New academic source for high-energy physics literature
- **Multi-Layer Caching**: GitHub Actions caching for seen papers, API responses, and models
- **Figure Caption Analysis**: Image-based relevance scoring from extracted captions

### 📊 Topic Restructuring
- **ACI**: Evolved from "Artificial Conscious Intelligence" to "Artificial Collective Intelligence" (multi-agent systems)
- **ANI**: Removed (covered by other topics)
- **Physical AI**: New topic for robotics and embodied AI
- **Compute Infra**: New topic for AI hardware and accelerators
- **Enhanced Coverage**: 163 unique keywords in predefined topics, 120 weighted keywords in scoring

## Advanced Features

### 🎯 Domain-Specific Scoring
Configure weighted keywords (1-6 scale) for your research domain to improve relevance:
```yaml
scoring:
  keyword_weights:
    # Core terms (weight 6)
    "artificial general intelligence": 6
    "large language model": 6
    # Very important (weight 5)
    "world models": 5
    "reasoning": 5
    # Important concepts (weight 4)
    "meta-learning": 4
    "causal reasoning": 4
```

**Features:**
- 120+ pre-configured weighted keywords across 7 topics
- Organized by research domain (AGI, ACI, ASI, Physical AI, Compute Infra, ML, LLM)
- Duplicate-free keyword set for optimal performance
- 70% weight to domain keywords, 30% to base topic matching

### 👥 Collaborator/Author Boosting
Boost papers from preferred researchers with automatic score multiplier:
```yaml
scoring:
  preferred_researchers:
    - "Geoffrey Hinton"
    - "Yann LeCun"
    - "Yoshua Bengio"
    - "Ilya Sutskever"
    - "Dario Amodei"
```

**Features:**
- Case-insensitive author name matching
- Automatic 2x score boost for preferred researchers
- Marks boosted papers for tracking
- Supports last name and full name variants

### 📄 Full-Text Extraction
Extract full text from arXiv papers for better similarity scoring (resource-intensive):
```yaml
advanced:
  enable_fulltext_extraction: true
```

**Features:**
- Extracts full text from arXiv HTML papers (up to 18,000 characters)
- Extracts figure and table captions for image-based relevance
- BeautifulSoup-based HTML parsing
- Configurable resource-intensive option

### 🔄 Seen Papers Cache
Prevent duplicate processing with automatic paper tracking:
```yaml
advanced:
  enable_seen_papers_cache: true
  seen_papers_cache_ttl_days: 30
  seen_papers_cache_path: /tmp/seen_papers.json
```

**Features:**
- Tracks papers by DOI, arXiv ID, URL, or title hash
- Configurable TTL (default 30 days)
- Automatic expired entry cleanup
- Batch operations for efficiency
- GitHub Actions caching for persistence

### 📊 Figure Caption Analysis
Extract and analyze figure/table captions for image-based relevance scoring:
- Automatic caption extraction from arXiv papers
- Figure and table caption analysis
- Integration with weighted keyword system
- 10% weight in final relevance score

### 🎨 Enhanced Topic Management
Organize research topics with priorities, descriptions, and comprehensive keywords:
```yaml
predefined_topics:
  llm:
    name: "Large Language Models & Context Scaling"
    priority: "high"
    description: "Research on LLMs, context handling, and generation strategies"
    keywords:
      - "large language model"
      - "LLM"
      - "long context window"
      - "RAG"
      - "mixture of experts"
```

**Features:**
- 7 predefined topics covering modern AI research
- Priority levels (high/medium/low)
- Detailed descriptions for each topic
- 20-32 keywords per topic
- Focus on frontier research areas

### 🚀 GitHub Actions Caching
Optimized CI/CD with multi-layer caching for faster runs and lower costs:
- Seen papers cache restoration/saving
- API response cache for reduced calls
- Hugging Face model caching
- Multi-layer caching strategy
- Applied to all workflow jobs

### 🔬 INSPIRE-HEP Integration
New academic source for high-energy physics literature:
- INSPIRE-HEP API integration
- Author, abstract, and citation count extraction
- arXiv eprint linking
- DOI extraction
- Configurable source option

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd research-collector

# Install dependencies
pip install -r requirements.txt

# Optional: Install Hugging Face integration for dataset export
pip install -e ".[huggingface]"

# Optional: Install all optional features
pip install -e ".[all]"

# Run your first research (default: last 7 days)
python -m research_collector "machine learning"
```

### Basic Usage

```bash
# Research with default settings (7-day window)
python -m research_collector research --query "AI safety"

# Use predefined topic
python -m research_collector research --topic agi

# List all available predefined topics
python -m research_collector topics
python -m research_collector research --list-topics

# Custom time range (15 days)
python -m research_collector research --query "transformer architecture" --days=15

# Quick search (3 days using depth)
python -m research_collector research --query "quantum computing" --depth=quick

# Standard search (15 days using depth)
python -m research_collector research --query "quantum computing" --depth=standard

# Deep search (30 days using depth)
python -m research_collector research --query "quantum computing" --depth=deep

# Historical search (90 days using depth)
python -m research_collector research --query "quantum computing" --depth=historical

# Extended search (365 days using depth)
python -m research_collector research --query "quantum computing" --depth=extended

# Specific sources only
python -m research_collector research --query "quantum computing" --sources=pubmed,crossref,semantic_scholar

# Export to different formats
python -m research_collector research --query "climate change" --export=json
python -m research_collector research --query "climate change" --export=csv
python -m research_collector research --query "climate change" --export=bibliography
python -m research_collector research --query "climate change" --export=html

# Export to Hugging Face Datasets
python -m research_collector research --query "machine learning" --export=huggingface --output username/dataset-name --hf-token YOUR_HF_TOKEN

# Academic research with citation filtering
python -m research_collector research --query "deep learning" --min-citations=50 --sources=academic

# Interactive mode
python -m research_collector interactive
```

## Predefined Research Topics

Research-Collector includes predefined research topics with corresponding keywords for modern AI and technology research areas:

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

You can add your own predefined topics in the configuration file with priorities and descriptions:

```yaml
predefined_topics:
  my_topic:
    name: "My Custom Research Topic"
    priority: "high"  # high, medium, low
    description: "Description of your research interest"
    keywords:
      - "keyword1"
      - "keyword2"
      - "keyword3"
```

### Topic Priorities

Topics can be assigned priorities to influence their importance in research:
- **high**: Primary research focus areas (AGI, ACI, Physical AI, Compute Infra, ML, LLM)
- **medium**: Secondary interest areas (ASI)
- **low**: Nice-to-have areas

### Keyword Weights

Each topic has associated keyword weights (1-6 scale) for relevance scoring:
- **6**: Core topic terms (highest priority)
- **5**: Very important concepts and methodologies
- **4**: Important related concepts
- **3**: Supporting technologies and approaches
- **2**: Peripheral but relevant concepts

The configuration includes 120+ weighted keywords organized by topic for highly relevant research results.

## Source Categories

### Academic Sources
- **PubMed**: Medical and life sciences literature
- **Crossref**: Academic metadata and citation tracking
- **Papers With Code**: ML papers with code implementations
- **Semantic Scholar**: Academic papers and citations
- **arXiv**: Preprint server for physics, CS, math, etc.

### Professional Sources
- **Stack Overflow**: Technical Q&A and programming solutions
- **GitHub**: Code repositories and development activity
- **Dev.to**: Developer blog posts and tutorials

### Social Sources
- **Reddit**: Community discussions and opinions
- **Hacker News**: Technology news and discussions

### News Sources
- **GDELT**: Global news database (free)
- **NewsAPI**: News articles (requires API key)

### Prediction Markets
- **Polymarket**: Prediction markets with real-money odds

## Use Cases

### Academic Research
```bash
# Literature review with citation tracking
python -m research_collector research --query "transformer efficiency" --sources=academic --min-citations=20

# Export bibliography for paper
python -m research_collector research --query "attention mechanisms" --export=bibliography --days=365

# Use predefined topic for literature review
python -m research_collector research --topic agi --sources=academic --days=90
```

### Technical Due Diligence
```bash
# Evaluate technology with community sentiment
python -m research_collector research --query "kubernetes vs docker" --sources=social,professional

# Check implementation challenges
python -m research_collector research --query "react server components" --sources=stackoverflow,github
```

### Market Intelligence
```bash
# Industry trend analysis
python -m research_collector research --query "generative AI adoption" --sources=news,academic --days=90

# Competitive landscape
python -m research_collector research --query "openai vs anthropic" --sources=all

# Use predefined topic for market analysis
python -m research_collector research --topic llm --sources=news,academic --days=30
```

### Policy Research
```bash
# Regulation tracking
python -m research_collector research --query "AI regulation" --sources=news,academic,government

# Public sentiment analysis
python -m research_collector research --query "data privacy laws" --sources=social,news
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
    inspire_hep: true  # High-energy physics literature
  professional:
    stackoverflow: true
    github: true
    kaggle: true  # Requires KAGGLE_USERNAME and KAGGLE_KEY
  social:
    reddit: true  # Requires Reddit OAuth2 credentials
    hackernews: true
  news:
    gdelt: true
    newsapi: false  # Requires NEWSAPI_API_KEY

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
  
  # Preferred researchers for author boosting
  preferred_researchers:
    - "Geoffrey Hinton"
    - "Ilya Sutskever"
    # Add your key researchers
  
  # Domain-specific keyword weights (1-6 scale)
  keyword_weights:
    "artificial general intelligence": 6
    "AGI": 6
    "world models": 6
    "large language model": 6
    "LLM": 6
    "reasoning": 5
    "transformer": 5
    # ... 120+ pre-configured keywords

# Predefined topics with priorities and descriptions
predefined_topics:
  agi:
    name: "Artificial General Intelligence"
    priority: "high"
    description: "Research on human-level AI and general intelligence"
    keywords:
      - "artificial general intelligence"
      - "AGI"
      - "world models"
      - "reasoning"
      # ... 21 keywords

advanced:
  max_results_per_source: 100
  clustering_similarity_threshold: 0.85
  enable_caching: true
  cache_ttl_hours: 24
  enable_seen_papers_cache: true
  seen_papers_cache_ttl_days: 30
  enable_fulltext_extraction: false  # Resource-intensive

api_keys:
  # Optional: Add API keys for enhanced rate limits
  pubmed: ${PUBMED_API_KEY}
  crossref: ${CROSSREF_API_KEY}
  semantic_scholar: ${SEMANTIC_SCHOLAR_API_KEY}
  newsapi: ${NEWSAPI_API_KEY}
  stackexchange: ${STACKEXCHANGE_API_KEY}
  reddit: ${REDDIT_CLIENT_ID}
  reddit_secret: ${REDDIT_CLIENT_SECRET}
  reddit_user_agent: ${REDDIT_USER_AGENT}
  kaggle_username: ${KAGGLE_USERNAME}
  kaggle_key: ${KAGGLE_KEY}
```

## API Keys (Optional)

Most sources work without API keys, but adding keys provides higher rate limits:

```bash
# Set environment variables
export PUBMED_API_KEY=your_key_here
export CROSSREF_API_KEY=your_email@example.com
export SEMANTIC_SCHOLAR_API_KEY=your_key_here
export NEWSAPI_API_KEY=your_key_here
export STACKEXCHANGE_API_KEY=your_key_here

# Reddit OAuth2 (required for Reddit source)
export REDDIT_CLIENT_ID=your_client_id
export REDDIT_CLIENT_SECRET=your_client_secret
export REDDIT_USER_AGENT="research-collector/1.0 (by /u/your_reddit_username)"

# Kaggle API (required for Kaggle source)
export KAGGLE_USERNAME=your_kaggle_username
export KAGGLE_KEY=your_kaggle_api_key
```

## Hugging Face Integration

Research-Collector supports exporting results to Hugging Face Datasets for easy sharing and collaboration in the ML community.

### Setup

1. Install Hugging Face dependencies:
```bash
pip install -e ".[huggingface]"
```

2. Get your Hugging Face token from https://huggingface.co/settings/tokens

3. Set the token as environment variable or pass it as parameter:
```bash
export HF_TOKEN=your_hf_token_here
```

### Usage

```bash
# Export to Hugging Face Datasets
python -m research_collector research \
  --query "machine learning" \
  --export=huggingface \
  --output username/dataset-name \
  --hf-token $HF_TOKEN

# Or use environment variable for token
python -m research_collector research \
  --query "AI safety" \
  --export=huggingface \
  --output username/ai-safety-research
```

### Features

- **Automatic dataset card generation**: Creates a README.md with dataset metadata
- **Structured data**: Converts results to Hugging Face Dataset format
- **Version control**: Each export creates a new version on the Hub
- **Easy sharing**: Share datasets with the ML community
- **Integration**: Works seamlessly with other Hugging Face tools

### Dataset Structure

The exported dataset includes:
- Research items with all metadata
- Source information
- Engagement metrics
- Relevance scores
- Publication dates
- Content/abstracts

### Accessing Your Dataset

```python
from datasets import load_dataset

dataset = load_dataset("username/dataset-name")
train_data = dataset["train"]

# Filter by source
pubmed_items = train_data.filter(lambda x: x["source"] == "pubmed")

# Sort by score
sorted_items = train_data.sort("score", reverse=True)
```

## Architecture

ResearchCollector uses a modular pipeline architecture:

```
Query → Planning → Multi-Source Search → Normalization → Scoring → Ranking → Clustering → Synthesis → Export
```

### Core Components

- **Source Modules**: Each data source has its own module with search and parsing logic
- **Pipeline**: Orchestrates parallel searches and data processing
- **Normalizers**: Convert source-specific formats to unified schema
- **Scoring Engine**: Multi-dimensional scoring (relevance, recency, engagement)
- **Clustering**: Merge duplicate stories across sources
- **Synthesis**: AI-powered result synthesis and formatting

## Development

### Project Structure

```
research-collector/
├── research_collector/          # Main package
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── pipeline.py             # Search orchestration
│   ├── scoring.py             # Scoring algorithms with domain weights
│   ├── normalization.py       # Data normalization
│   ├── clustering.py          # Deduplication
│   ├── synthesis.py           # Result synthesis
│   ├── fulltext.py            # Full-text and figure extraction
│   ├── seen_papers.py         # Paper deduplication cache
│   ├── sources/               # Source modules
│   │   ├── __init__.py
│   │   ├── pubmed.py
│   │   ├── stackoverflow.py
│   │   ├── crossref.py
│   │   ├── paperswithcode.py
│   │   ├── semantic_scholar.py
│   │   ├── arxiv.py
│   │   ├── inspire_hep.py     # INSPIRE-HEP academic source
│   │   ├── reddit.py
│   │   ├── hackernews.py
│   │   ├── news.py
│   │   ├── github.py
│   │   ├── kaggle.py
│   │   ├── medium.py
│   │   └── ...
│   └── exporters/             # Export formats
│       ├── markdown.py
│       ├── json.py
│       ├── csv.py
│       ├── bibliography.py
│       └── ...
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── config/                    # Configuration files
│   └── research-collector.yaml.template
├── .github/workflows/         # GitHub Actions workflows
│   ├── scheduled-research.yml  # Daily automated research
│   └── ...
├── requirements.txt
├── setup.py
└── README.md
```

### Adding New Sources

Create a new source module in `research_collector/sources/`:

```python
"""Your Source Name via API (free/paid, auth requirements)."""

def search_source(query, from_date, to_date, depth, config):
    """Search the source and return raw results."""
    # Implementation
    pass

def parse_source_response(raw_results, query):
    """Parse raw results into normalized format."""
    # Implementation
    pass
```

Then register it in `research_collector/__init__.py` and the pipeline.

## Comparison to Alternatives

| Feature | Research-Collector | Google Scholar | Traditional Search |
|---------|-------------------|----------------|-------------------|
| Multi-source | ✅ 15+ sources | ❌ Academic only | ❌ Web only |
| Real-time | ✅ Social signals | ❌ Slow indexing | ✅ Real-time |
| Engagement-based | ✅ Multiple metrics | ❌ Citations only | ❌ SEO-based |
| Time-flexible | ✅ Any range | ❌ Historical | ❌ Mixed |
| Local-privacy | ✅ Local processing | ❌ Cloud-based | ❌ Cloud-based |
| Extensible | ✅ Plugin system | ❌ Fixed | ❌ Fixed |

## CI/CD and GitHub Actions

This project includes comprehensive GitHub Actions workflows for continuous integration and deployment.

### Workflows

See `.github/workflows/` for:
- **CI** (`.github/workflows/ci.yml`): Testing, linting, security checks
- **Publish** (`.github/workflows/publish.yml`): PyPI publishing on version tags
- **Scheduled Research** (`.github/workflows/scheduled-research.yml`): Daily automated research with Hugging Face export
- **Code Quality** (`.github/workflows/code-quality.yml`): Type checking and documentation

### Scheduled Research with Hugging Face

The scheduled research workflow automatically:
- Runs daily research on 7 topics (ML, LLM, AGI, ASI, ACI, Physical AI, Compute Infra)
- Exports results to Hugging Face Datasets:
  - `{repository-owner}/ml-research-daily`
  - `{repository-owner}/llm-research-daily`
  - `{repository-owner}/agi-research-daily`
  - `{repository-owner}/asi-research-daily`
  - `{repository-owner}/aci-research-daily`
  - `{repository-owner}/physical-ai-research-daily`
  - `{repository-owner}/compute-infra-research-daily`
- Includes automatic dataset validation and error handling
- Supports manual triggers for custom research (exports to `{repository-owner}/custom-research`)
- Uses advanced features: seen papers cache, domain-specific scoring, author boosting

**Setup**: See [GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md) for detailed setup instructions.

### GitHub Actions Setup

1. Add secrets to your GitHub repository:
   - `HF_TOKEN`: Hugging Face authentication token (required for scheduled research)
   - `PYPI_API_TOKEN`: For publishing to PyPI (optional)

2. The workflows will automatically run on:
   - Push to main/develop branches
   - Pull requests
   - Version tags (for publishing)
   - Daily schedule (for research)

### Manual Triggers

All workflows support manual triggering via the GitHub Actions UI. The scheduled research workflow supports custom topics and time ranges.

## Contributing

Contributions are welcome! Areas for contribution:

- New source integrations
- Export format improvements
- Scoring algorithm enhancements
- Documentation improvements
- Bug fixes and performance improvements

## License

MIT License - See LICENSE file for details

## Acknowledgments

Research-Collector is inspired by and builds upon concepts from the excellent [last30days](https://github.com/mvanhorn/last30days-skill) project, with significant enhancements for educational and academic research use cases.

## Educational Use

This tool is provided for educational purposes to help students and researchers learn about:
- Data aggregation from multiple sources
- Information retrieval and normalization techniques
- Engagement-based ranking algorithms
- Research methodologies and best practices

---

**Research-Collector**: Educational research intelligence from diverse sources, scored by real engagement.