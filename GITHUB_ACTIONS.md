# GitHub Actions CI/CD Setup

This document describes the GitHub Actions workflows that have been added to Research-Collector.

**Note**: For GitLab CI/CD setup, see [GITLAB_CI.md](./GITLAB_CI.md).

## Workflows Created

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Purpose**: Continuous Integration for testing, linting, and security checks

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs**:
- **test**: Runs tests across Python 3.8, 3.9, 3.10, 3.11 with pytest and coverage reporting
- **lint**: Code quality checks with flake8, black, and isort
- **security**: Security scanning with bandit and safety

### 2. Publish Workflow (`.github/workflows/publish.yml`)

**Purpose**: Automatically publish to PyPI on version tags

**Triggers**:
- Push tags matching `v*` (e.g., v1.0.0)

**Jobs**:
- **build-and-publish**: Builds the package and publishes to PyPI

**Required Secrets**:
- `PYPI_API_TOKEN`: PyPI API token for publishing

### 3. Scheduled Research Workflow (`.github/workflows/scheduled-research.yml`)

**Purpose**: Run automated research on key topics and export to Hugging Face Datasets

**Triggers**:
- Daily cron job at midnight UTC
- Manual trigger via GitHub Actions UI

**Jobs**:
- **research-ml**: Daily ML research, exports to `nellaivijay/ml-research-daily`
- **research-llm**: Daily LLM research, exports to `nellaivijay/llm-research-daily`
- **research-agi**: Daily AGI research, exports to `nellaivijay/agi-research-daily`
- **research-asi**: Daily ASI research, exports to `nellaivijay/asi-research-daily`
- **research-ani**: Daily ANI research, exports to `nellaivijay/ani-research-daily`
- **research-aci**: Daily ACI research, exports to `nellaivijay/aci-research-daily`
- **custom-research**: Manual custom research with parameters, exports to `nellaivijay/custom-research`

**Required Secrets**:
- `HF_TOKEN`: Hugging Face authentication token for dataset export

**Manual Trigger Options**:
- `topic`: Choose ml, llm, agi, asi, ani, aci, or custom
- `days`: Number of days to research (3, 7, 14, or 30)
- `custom_query`: Custom search query (if topic=custom)
- `sources`: Specific sources (comma-separated, optional)

**Features**:
- ✅ Daily automated research for 6 topics (ML, LLM, AGI, ASI, ANI, ACI)
- ✅ Hugging Face dataset export
- ✅ Automatic dataset validation after export
- ✅ Timeout protection (30 minutes)
- ✅ Continue-on-error for resilience
- ✅ Pip and Hugging Face caching for speed
- ✅ Environment variables for better performance
- ✅ Dataset validation to ensure data quality
- ✅ Manual trigger for custom research

### 4. Code Quality Workflow (`.github/workflows/code-quality.yml`)

**Purpose**: Type checking and documentation building

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs**:
- **type-check**: Type checking with mypy
- **documentation**: Builds Sphinx documentation

## Development Dependencies

Created `requirements-dev.txt` with:
- Testing: pytest, pytest-cov
- Code quality: flake8, black, isort, mypy
- Security: bandit, safety
- Optional integrations: huggingface_hub, datasets
- Documentation: sphinx, sphinx-rtd-theme
- Build tools: build, twine

## Setup Instructions

### For CI/CD

1. **Add GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add `PYPI_API_TOKEN` for PyPI publishing (optional)
   - Add `HF_TOKEN` for Hugging Face dataset export (required for scheduled research)

2. **Enable Workflows**:
   - Workflows will automatically run on triggers
   - Can be manually triggered from Actions tab

## Workflow Features

### Caching
- Python pip caching where applicable

### Matrix Testing
- Tests run across multiple Python versions (3.8-3.11)
- Ensures compatibility

### Security
- Automated security scanning on every PR
- Dependency vulnerability checking
- Code security analysis with bandit

### Reporting
- Coverage reports uploaded to Codecov
- Test results visible in Actions UI
- Artifacts available for download

## Customization

### Adding New Topics to Scheduled Research

Edit `.github/workflows/scheduled-research.yml`:

```yaml
research-custom-topic:
  if: github.event_name == 'schedule' || (github.event_name == 'workflow_dispatch' && github.event.inputs.topic == 'custom-topic')
  runs-on: ubuntu-latest
  
  steps:
  - uses: actions/checkout@v4
  
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.10'
  
  - name: Install dependencies
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements-dev.txt
  
  - name: Run research and export to Hugging Face
    env:
      HF_TOKEN: ${{ secrets.HF_TOKEN }}
    run: |
      python -m research_collector research \
        --query "your custom topic" \
        --days 7 \
        --export=huggingface \
        --output ${{ github.repository_owner }}/custom-topic-daily \
        --no-cache
```

Add the topic to the workflow_dispatch inputs:

```yaml
workflow_dispatch:
  inputs:
    topic:
      description: 'Research topic (ml, llm, agi, custom-topic, or custom)'
      required: false
      default: 'ml'
```

### Manually Triggering Scheduled Research

1. Go to **Actions** tab in your repository
2. Select **Scheduled Research** workflow
3. Click **Run workflow**
4. Select branch (usually `main`)
5. Choose options:
   - **topic**: ml, llm, agi, or custom
   - **days**: Number of days (default: 7)
   - **custom_query**: If topic=custom, enter your search query
6. Click **Run workflow**

The workflow will:
- Run research on the specified topic
- Export results to Hugging Face Datasets
- Create dataset: `{owner}/{topic}-research-daily` (or custom-research for custom queries)

### Changing Python Versions

Edit `.github/workflows/ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']  # Add 3.12
```

### Modifying Schedule

Edit `.github/workflows/scheduled-research.yml`:

```yaml
schedule:
  # Run every 6 hours
  - cron: '0 */6 * * *'
```

## Best Practices

1. **Branch Protection**: Enable branch protection rules for `main` to require CI checks
2. **Secret Management**: Never commit secrets to repository
3. **Regular Updates**: Keep GitHub Actions dependencies updated
4. **Monitor Workflows**: Check workflow runs regularly for failures
5. **Artifact Cleanup**: Clean up old artifacts periodically

## Troubleshooting

### PyPI Publishing Fails
- Verify `PYPI_API_TOKEN` is correct
- Ensure version tag follows semantic versioning (v1.0.0)
- Check PyPI account has publishing permissions

### Tests Fail
- Check Python version compatibility
- Verify all dependencies are in requirements-dev.txt
- Run tests locally before pushing

### Scheduled Workflow Not Running
- Verify workflow file is in correct location
- Check cron syntax is valid
- Ensure GitHub Actions is enabled for repository

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
