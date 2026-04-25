# Source Health Check System

Comprehensive health monitoring for all data sources and targets in Research-Collector.

## Overview

The health check system provides real-time monitoring of:
- **API Availability**: Whether each source API is accessible
- **API Key Configuration**: Whether required API keys are configured
- **API Key Validity**: Whether API keys are working correctly
- **Rate Limiting**: Detection of rate limiting or blocking
- **Response Times**: Performance monitoring
- **Error Handling**: Detailed error reporting

## Components

### 1. Health Check Script (`scripts/source_health_check.py`)

Python script that performs comprehensive health checks on all data sources.

**Features:**
- Checks 12 data sources (academic, professional, social, news)
- Validates API key configuration
- Tests API endpoints with real requests
- Measures response times
- Detects rate limiting and blocking
- Generates detailed reports
- Exports results to JSON

**Supported Sources:**
- Academic: PubMed, Crossref, Semantic Scholar, Papers with Code, arXiv
- Professional: GitHub, Stack Overflow, Kaggle
- Social: Reddit, Hacker News
- News: GDELT, Medium

### 2. GitHub Actions Workflow (`.github/workflows/source-health-check.yml`)

Automated health checks running every 6 hours.

**Jobs:**
1. **Source Health Check**: Comprehensive monitoring of all sources
2. **Target Health Check**: Monitoring of Hugging Face datasets

**Features:**
- Scheduled execution (every 6 hours)
- Manual trigger support
- Artifact upload for results
- Automatic issue creation for failures
- PR comments for health check failures
- Critical failure detection

## Usage

### Local Testing

Run the health check script locally:

```bash
# Set environment variables for API keys
export PUBMED_API_KEY="your_key"
export CROSSREF_API_KEY="your_key"
export SEMANTIC_SCHOLAR_API_KEY="your_key"
# ... etc

# Run the health check
python scripts/source_health_check.py

# Export results to JSON
python scripts/source_health_check.py health-results.json
```

### GitHub Actions

#### Manual Trigger

1. Go to: https://github.com/nellaivijay/research-collector/actions/workflows/source-health-check.yml
2. Click "Run workflow"
3. Configure notification preference
4. Click "Run workflow"

#### Scheduled Execution

The workflow runs automatically every 6 hours via cron schedule.

## Health Check Results

### Status Categories

- **✓ Healthy**: API responding normally (< 1s response time)
- **⚠ Degraded**: API responding but with issues (slow, rate limited)
- **✗ Unhealthy**: API not responding or critical errors
- **? Unknown**: Unable to determine status

### Health Metrics

- **API Available**: Whether the API endpoint is accessible
- **API Key Configured**: Whether required API key is set
- **API Key Valid**: Whether API key works correctly
- **Response Time**: API response time in milliseconds
- **Error Message**: Detailed error information

### Output Format

The health check generates a JSON report with:

```json
{
  "summary": {
    "timestamp": "2026-04-23T15:00:00",
    "total_sources": 12,
    "healthy": 8,
    "degraded": 2,
    "unhealthy": 2,
    "health_percentage": 66.67,
    "api_keys_configured": 5,
    "api_keys_invalid": 1,
    "categories": {
      "academic": {"healthy": 4, "degraded": 1, "unhealthy": 0, "total": 5},
      "professional": {"healthy": 2, "degraded": 1, "unhealthy": 1, "total": 4},
      "social": {"healthy": 1, "degraded": 0, "unhealthy": 1, "total": 2},
      "news": {"healthy": 1, "degraded": 0, "unhealthy": 0, "total": 1}
    }
  },
  "sources": [
    {
      "name": "PubMed",
      "status": "healthy",
      "api_available": true,
      "api_key_configured": true,
      "api_key_valid": true,
      "response_time_ms": 245.5,
      "error_message": "",
      "details": {
        "response_time_ms": 245.5,
        "status_code": 200,
        "api_key_configured": true,
        "api_key_length": 36
      }
    }
  ]
}
```

## API Key Configuration

### Required API Keys

Some sources require API keys for optimal performance:

| Source | API Key Environment Variable | Required |
|--------|----------------------------|----------|
| PubMed | `PUBMED_API_KEY` | Optional |
| Crossref | `CROSSREF_API_KEY` | Optional |
| Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | Optional |
| Stack Overflow | `STACKEXCHANGE_API_KEY` | Optional |
| GitHub | `GITHUB_TOKEN` | Optional |
| Reddit | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | Required |
| Kaggle | `KAGGLE_USERNAME`, `KAGGLE_KEY` | Required |

### Setting API Keys

#### GitHub Secrets (for CI/CD)

1. Go to repository Settings → Secrets and variables → Actions
2. Add each API key as a new secret
3. Use the exact environment variable names

#### Local Environment

```bash
export PUBMED_API_KEY="your_key_here"
export CROSSREF_API_KEY="your_key_here"
export SEMANTIC_SCHOLAR_API_KEY="your_key_here"
# ... etc
```

#### Configuration File

Create `research-collector.yaml`:

```yaml
api_keys:
  pubmed: "your_key_here"
  crossref: "your_key_here"
  semantic_scholar: "your_key_here"
  # ... etc
```

## Troubleshooting

### Common Issues

#### API Key Not Configured

**Error:** `API key not configured: PUBMED_API_KEY`

**Solution:**
- Add the API key to GitHub Secrets or environment variables
- Verify the exact variable name matches

#### Authentication Failed

**Error:** `Authentication failed - API key invalid or expired`

**Solution:**
- Verify the API key is correct
- Check if the key has expired
- Ensure the key has proper permissions

#### Rate Limited

**Error:** `Rate limited - too many requests`

**Solution:**
- Wait for rate limit to reset
- Consider upgrading API plan
- Implement request throttling

#### Connection Timeout

**Error:** `Request timed out after 10 seconds`

**Solution:**
- Check network connectivity
- Verify API endpoint is accessible
- Check if API is experiencing downtime

#### Access Forbidden

**Error:** `Access forbidden - API key may be blocked or rate limited`

**Solution:**
- Check if API key has been blocked
- Verify API key permissions
- Contact API provider if needed

## Notifications

### Automatic Issue Creation

When health checks detect critical failures:
- Automatic GitHub issue creation
- Issue labeled with `health-check` and `automated`
- Issue updated on subsequent failures
- Issue closed when health is restored

### PR Comments

When health check fails during a PR:
- Automatic comment on the PR
- Summary of health check results
- List of unhealthy sources

### Critical Failure Detection

The workflow checks for:
- Less than 50% of sources healthy
- Authentication failures
- Access denied errors

## Integration with CI/CD

### Pre-commit Hook

Add a pre-commit hook to check sources before pushing:

```bash
#!/bin/bash
python scripts/source_health_check.py
if [ $? -ne 0 ]; then
    echo "Health check failed. Please fix issues before pushing."
    exit 1
fi
```

### Pipeline Integration

Add to your CI pipeline:

```yaml
- name: Source health check
  run: python scripts/source_health_check.py
```

## Monitoring Dashboard

You can create a monitoring dashboard using the health check results:

1. **GitHub Actions Artifacts**: Download JSON results from workflow runs
2. **External Monitoring**: Send results to external monitoring services
3. **Custom Dashboard**: Build a dashboard using the JSON output

## Best Practices

1. **Run Regularly**: Schedule health checks at least every 6 hours
2. **Monitor Trends**: Track health metrics over time
3. **Set Up Alerts**: Configure notifications for critical failures
4. **Keep Keys Updated**: Regularly rotate API keys
5. **Document Issues**: Track recurring issues and their resolutions
6. **Test Locally**: Run health checks locally before deploying changes
7. **Review Results**: Regularly review health check reports

## Extending the Health Check System

### Adding New Sources

Edit `scripts/source_health_check.py` and add to the `_get_sources_config()` method:

```python
{
    "name": "New Source",
    "api_url": "https://api.example.com/endpoint",
    "test_params": {"param": "value"},
    "api_key_env": "NEW_SOURCE_API_KEY",
    "requires_key": False,
    "category": "academic"
}
```

### Custom Health Checks

Add custom health check logic in the `check_source()` method.

### Additional Metrics

Add custom metrics to the `SourceHealth` dataclass.

## Support

For issues or questions:
1. Check the health check results in GitHub Actions
2. Review the troubleshooting section above
3. Open an issue on GitHub with health check results attached
