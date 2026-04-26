# Research-Collector Data Schemas

This document describes the data structures used throughout the Research-Collector system.

## Overview

Research-Collector aggregates data from 12+ sources, normalizes it, enriches it with metadata, and exports it in various formats. This document describes the schemas at each stage.

## Source Schemas

Each data source returns data in its own format, which is then normalized to a common structure.

### Common Normalized Structure

All sources are normalized to this common structure:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (source-specific prefix) |
| `title` | string | Yes | Title of the research item |
| `url` | string | Yes | URL to original content |
| `source` | string | Yes | Source platform name |
| `author` | string | Yes | Author(s) or creator |
| `published_date` | string | Yes | Publication date (ISO 8601 format) |
| `citations` | integer | No | Number of citations (if available) |
| `upvotes` | integer | No | Number of upvotes (if available) |
| `downloads` | integer | No | Number of downloads (if available) |
| `comments` | integer | No | Number of comments (if available) |
| `content` | string | Yes | Content/abstract/description |
| `metadata` | object | Yes | Source-specific and enriched metadata |

### Source-Specific Metadata

#### GitHub (`github`)

**Additional metadata fields:**
- `stars`: Star count
- `forks`: Fork count
- `language`: Primary programming language
- `topics`: Repository topics
- `license`: License name
- `has_readme`: Whether repository has README
- `has_license`: Whether repository has license
- `is_fork`: Whether repository is a fork
- `created_at`: Repository creation timestamp
- `updated_at`: Repository last update timestamp
- `days_since_creation`: Days since creation
- `days_since_update`: Days since last update

#### Reddit (`reddit`)

**Additional metadata fields:**
- `subreddit`: Subreddit name
- `score`: Post score
- `num_comments`: Number of comments
- `over_18`: NSFW flag (filtered out in educational context)
- `link_flair_text`: Post flair text
- `is_self`: Whether post is self-text (not link)
- `external_url`: External URL if link post
- `domain`: Domain of external link
- `upvote_ratio`: Upvote ratio (0-1)
- `total_awards`: Number of awards
- `gilded`: Gold awards count
- `stickied`: Whether post is stickied

#### PubMed (`pubmed`)

**Additional metadata fields:**
- `journal`: Journal name
- `pubmed_id`: PubMed ID
- `year`: Publication year
- `doi`: DOI if available
- `mesh_terms`: MeSH terms
- `publication_types`: Publication types
- `abstract_length`: Abstract character count
- `has_doi`: Whether DOI is available

#### arXiv (`arxiv`)

**Additional metadata fields:**
- `arxiv_id`: arXiv ID
- `primary_category`: Primary category
- `categories`: List of categories
- `category_count`: Number of categories
- `journal_ref`: Journal reference if published
- `doi`: DOI if available
- `has_doi`: Whether DOI is available
- `is_published`: Whether published in journal
- `days_since_submission`: Days since submission
- `comment`: arXiv comment
- `has_comment`: Whether comment exists

#### Semantic Scholar (`semantic_scholar`)

**Additional metadata fields:**
- `citation_count`: Citation count
- `influential_citation_count`: Influential citation count
- `fields_of_study`: Fields of study
- `has_open_access`: Whether open access

#### Crossref (`crossref`)

**Additional metadata fields:**
- `doi`: DOI
- `publisher`: Publisher name
- `type`: Publication type
- `member`: Member ID
- `deposited`: Deposit date

#### Papers with Code (`paperswithcode`)

**Additional metadata fields:**
- `pwc_id`: Papers with Code ID
- `methods`: Methods used
- `tasks`: Tasks addressed
- `datasets`: Datasets used
- `frameworks`: Frameworks used

#### Stack Overflow (`stackoverflow`)

**Additional metadata fields:**
- `tags`: Question tags
- `answer_count`: Number of answers
- `has_accepted_answer`: Whether accepted answer exists
- `view_count`: View count
- `owner_reputation`: Owner reputation
- `is_answered`: Whether question is answered

#### Kaggle (`kaggle`)

**Additional metadata fields:**
- `votes`: Vote count
- `usability_rating`: Usability rating
- `file_count`: Number of files
- `dataset_size`: Dataset size

#### Medium (`medium`)

**Additional metadata fields:**
- `publication`: Publication name
- `read_time`: Estimated read time (minutes)
- `claps`: Clap count
- `author`: Author name

#### Hacker News (`hackernews`)

**Additional metadata fields:**
- `hn_id`: Hacker News story ID
- `points`: Points count
- `comment_count`: Number of comments
- `time`: Post timestamp

#### GDELT (`gdelt`)

**Additional metadata fields:**
- `gdelt_id`: GDELT event ID
- `tone`: Sentiment tone
- `location`: Geographic location
- `event_type`: Event type

## Enriched Metadata

After normalization, items are enriched with additional metadata:

### Temporal Features
- `metadata_year`: Publication year
- `metadata_month`: Publication month
- `metadata_day`: Publication day
- `metadata_week`: Week of year
- `metadata_quarter`: Quarter of year
- `metadata_days_since`: Days since publication

### ML/AI Classification
- `metadata_ml_subfields`: ML subfield classifications (array)
- `metadata_subfield_count`: Number of ML subfields
- `metadata_keywords`: Extracted keywords (array)
- `metadata_keyword_count`: Number of keywords

### Content Analysis
- `metadata_content_type`: Content type (paper, preprint, repository, discussion, qa, news)
- `metadata_has_code`: Whether item contains code
- `metadata_has_doi`: Whether item has DOI
- `metadata_summary`: Automatic summary
- `metadata_summary_length`: Summary length

### Sentiment Analysis
- `metadata_sentiment_polarity`: Sentiment polarity (-1 to 1)
- `metadata_sentiment_subjectivity`: Sentiment subjectivity (0 to 1)
- `metadata_sentiment_category`: Sentiment category (positive, negative, neutral)

### Trending Metrics
- `metadata_trending_score`: Engagement velocity score
- `metadata_trending_category`: Trending category (hot, warm, cool, cold)
- `metadata_engagement_score`: Raw engagement score

### Cross-References
- `metadata_related_items`: Related items with similarity scores (array)
- `metadata_related_count`: Number of related items

### Data Quality Metrics
- `metadata_data_quality`: Object containing quality metrics
  - `completeness_score`: Field completeness (0-100)
  - `consistency_score`: Internal consistency (0-100)
  - `validity_score`: Data validity (0-100)
  - `overall_quality_score`: Overall quality (0-100)

## Output Schema

### Final Research Output

```python
{
    "topic": "artificial general intelligence",
    "from_date": "2024-04-16T00:00:00",
    "to_date": "2024-04-23T00:00:00",
    "sources_used": ["pubmed", "arxiv", "github", "reddit", ...],
    "items": [
        {
            "id": "arxiv_2404.12345",
            "title": "Paper title here",
            "url": "https://arxiv.org/abs/2404.12345",
            "source": "arxiv",
            "author": "Author Name",
            "published_date": "2024-04-20",
            "citations": 0,
            "upvotes": 0,
            "downloads": 0,
            "comments": 0,
            "content": "Abstract text here...",
            "score": 0.85,
            "metadata": {
                # All enriched metadata fields
            }
        },
        # ... more items
    ],
    "metadata": {
        "total_items": 150,
        "source_counts": {
            "arxiv": 30,
            "github": 25,
            "reddit": 20,
            # ... other sources
        }
    }
}
```

## Export Formats

### HuggingFace Dataset

Fields are flattened for HuggingFace:
- All core fields as top-level fields
- All metadata fields prefixed with `metadata_`
- Complex objects (arrays, dicts) serialized as JSON strings

### CSV Export

Core fields only:
- `id`, `title`, `url`, `source`, `author`, `published_date`
- Engagement metrics: `citations`, `upvotes`, `downloads`, `comments`
- `score`, `content` (truncated)
- Quality scores: `completeness_score`, `consistency_score`, `validity_score`, `overall_quality_score`

### JSON Export

Full structure with all metadata preserved.

### Markdown Export

Human-readable format with sections by source and quality ranking.

## Validation Rules

### Critical Issues (Must Pass)
- All required fields present: `id`, `title`, `url`, `source`
- Valid URL format (must start with http:// or https://)
- Valid source name
- No NSFW content (educational context)

### Warnings (Should Pass)
- Missing optional fields: `author`, `published_date`, `content`
- Unusually long titles (>2000 chars)
- Negative engagement metrics
- Missing or invalid dates

## Quality Thresholds

### Minimum Acceptable Quality
- Completeness score: ≥70%
- Consistency score: ≥80%
- Validity score: ≥90%
- Overall quality score: ≥75%

### Target Quality
- Completeness score: ≥85%
- Consistency score: ≥90%
- Validity score: ≥95%
- Overall quality score: ≥85%

## Data Freshness

- Scheduled updates: Daily at midnight UTC
- Default time range: 7 days
- Maximum data age: 7 days for default research
- Emergency updates: Within 4 hours for critical issues

## Notes

- All dates are in ISO 8601 format
- All scores are normalized to 0-1 range (except quality scores which are 0-100)
- Source-specific metadata is preserved in the `metadata` object
- Educational context filtering removes NSFW content
- Data is aggregated for educational purposes only

## Version

- Schema version: 1.0
- Last updated: 2024-04-23
- Maintained as part of Research-Collector project
