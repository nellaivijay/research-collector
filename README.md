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

- **15+ Data Sources**: Academic (PubMed, Crossref, Papers With Code), Professional (Stack Overflow), Social (Reddit), News (GDELT)
- **Flexible Time Windows**: Research any time period - last 3 days, 7 days (default), 15 days, 30 days, 90 days, 365 days, or custom ranges
- **Engagement-Based Ranking**: Results scored by citations, upvotes, answers, downloads - not SEO
- **Cross-Platform Clustering**: Same story across multiple sources merged into unified insights
- **Multiple Export Formats**: Markdown, JSON, CSV, HTML, BibTeX for academic workflows
- **Local-First Privacy**: All processing happens locally, your research stays private
- **Extensible Architecture**: Plugin system for custom sources and scoring algorithms
- **Educational Documentation**: Comprehensive examples and explanations for learning

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd research-collector

# Install dependencies
pip install -r requirements.txt

# Run your first research (default: last 7 days)
python -m research_collector "machine learning"
```

### Basic Usage

```bash
# Research with default settings (7-day window)
python -m research_collector "AI safety"

# Custom time range (15 days)
python -m research_collector "transformer architecture" --days=15

# Quick search (3 days using depth)
python -m research_collector "quantum computing" --depth=quick

# Standard search (15 days using depth)
python -m research_collector "quantum computing" --depth=standard

# Deep search (30 days using depth)
python -m research_collector "quantum computing" --depth=deep

# Historical search (90 days using depth)
python -m research_collector "quantum computing" --depth=historical

# Extended search (365 days using depth)
python -m research_collector "quantum computing" --depth=extended

# Specific sources only
python -m research_collector "quantum computing" --sources=pubmed,crossref,semantic_scholar

# Export to different formats
python -m research_collector "climate change" --export=json
python -m research_collector "climate change" --export=csv
python -m research_collector "climate change" --export=bibliography

# Academic research with citation filtering
python -m research_collector "deep learning" --min-citations=50 --sources=academic

# Interactive mode
python -m research_collector interactive
```

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
python -m research_collector "transformer efficiency" --sources=academic --min-citations=20

# Export bibliography for paper
python -m research_collector "attention mechanisms" --export=bibliography --days=365
```

### Technical Due Diligence
```bash
# Evaluate technology with community sentiment
python -m research_collector "kubernetes vs docker" --sources=social,professional

# Check implementation challenges
python -m research_collector "react server components" --sources=stackoverflow,github
```

### Market Intelligence
```bash
# Industry trend analysis
python -m research_collector "generative AI adoption" --sources=news,academic --days=90

# Competitive landscape
python -m research_collector "openai vs anthropic" --sources=all
```

### Policy Research
```bash
# Regulation tracking
python -m research_collector "AI regulation" --sources=news,academic,government

# Public sentiment analysis
python -m research_collector "data privacy laws" --sources=social,news
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
  professional:
    stackoverflow: true
    github: true
  social:
    reddit: true
    hackernews: true
  news:
    gdelt: true
    newsapi: false  # Requires API key

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

api_keys:
  # Optional: Add API keys for enhanced rate limits
  pubmed: ${PUBMED_API_KEY}
  crossref: ${CROSSREF_API_KEY}
  semantic_scholar: ${SEMANTIC_SCHOLAR_API_KEY}
  newsapi: ${NEWSAPI_API_KEY}
  stackexchange: ${STACKEXCHANGE_API_KEY}
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
│   ├── sources/               # Source modules
│   │   ├── __init__.py
│   │   ├── pubmed.py
│   │   ├── stackoverflow.py
│   │   ├── crossref.py
│   │   ├── paperswithcode.py
│   │   ├── semantic_scholar.py
│   │   ├── reddit.py
│   │   ├── hackernews.py
│   │   ├── news.py
│   │   └── github.py
│   ├── pipeline.py             # Search orchestration
│   ├── normalization.py       # Data normalization
│   ├── scoring.py             # Scoring algorithms
│   ├── clustering.py          # Deduplication
│   ├── synthesis.py           # Result synthesis
│   └── exporters/             # Export formats
│       ├── markdown.py
│       ├── json.py
│       ├── csv.py
│       └── bibliography.py
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── config/                    # Configuration files
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