# GitHub Actions Workflows

This document describes the GitHub Actions workflows configured for Research-Collector.

## Available Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Purpose**: Continuous integration testing and quality checks

**Triggers**:
- Push to main or develop branches
- Pull requests to main or develop branches

**Jobs**:
- **test**: Run tests across multiple Python versions (3.8, 3.9, 3.10, 3.11)
- **lint**: Code linting with flake8, black, and isort
- **security**: Security checks with bandit and safety

**Features**:
- ✅ Multi-version Python testing
- ✅ Code coverage reporting with Codecov
- ✅ Code formatting checks
- ✅ Security vulnerability scanning

### 2. CodeQL Workflow (`.github/workflows/codeql.yml`)

**Purpose**: Static code analysis for security vulnerabilities

**Triggers**:
- Push to main or develop branches
- Pull requests to main or develop branches
- Weekly schedule (Sundays at midnight UTC)

**Jobs**:
- **analyze**: CodeQL analysis with security-extended and security-and-quality queries

**Features**:
- ✅ Automated security vulnerability detection
- ✅ Code quality analysis
- ✅ Weekly scheduled scans
- ✅ Results uploaded to GitHub Security tab

### 3. Copilot Code Review (`.github/workflows/copilot-review.yml`)

**Purpose**: AI-powered code review using GitHub Copilot

**Triggers**:
- Pull requests (opened, synchronized, reopened)
- Manual workflow dispatch

**Jobs**:
- **copilot-review**: Automated code review with severity filtering

**Features**:
- ✅ AI-powered code analysis
- ✅ Security, performance, and correctness checks
- ✅ High-severity issue blocking
- ✅ Review summary generation

### 4. Dependabot Updates (`.github/dependabot.yml`)

**Purpose**: Automated dependency updates

**Schedule**:
- Weekly on Mondays at midnight UTC

**Updates**:
- **Python dependencies**: pip packages from requirements.txt
- **GitHub Actions**: Workflow action versions

**Features**:
- ✅ Automatic dependency updates
- ✅ Pull request creation with reviewers
- ✅ Dependency type filtering
- ✅ Automatic labeling

### 5. Nightly E2E Tests (`.github/workflows/nightly-e2e.yml`)

**Purpose**: End-to-end testing of critical workflows

**Triggers**:
- Daily at 2 AM UTC
- Manual workflow dispatch

**Jobs**:
- **e2e-tests**: Multiple E2E test suites
  - basic-research
  - multi-source
  - export-formats
  - huggingface-export
  - web-interface
- **e2e-summary**: Aggregate test results

**Features**:
- ✅ Comprehensive E2E testing
- ✅ Test result artifacts
- ✅ Timeout protection
- ✅ Failure summary

### 6. Publish to PyPI (`.github/workflows/publish-pypi.yml`)

**Purpose**: Publish package to PyPI

**Triggers**:
- Version tags (v*)
- Manual workflow dispatch

**Jobs**:
- **build**: Build distribution packages
- **publish**: Publish to PyPI with trusted publishing

**Required Secrets**:
- `PYPI_API_TOKEN`: PyPI authentication token

**Features**:
- ✅ Automated package building
- ✅ Distribution verification
- ✅ Trusted publishing with OIDC
- ✅ Artifact upload

### 7. Publish to TestPyPI (`.github/workflows/publish-testpypi.yml`)

**Purpose**: Publish package to TestPyPI for testing

**Triggers**:
- Test version tags (test-v*)
- Manual workflow dispatch

**Jobs**:
- **build**: Build distribution packages
- **publish**: Publish to TestPyPI

**Features**:
- ✅ Test environment deployment
- ✅ Skip existing packages
- ✅ Artifact preservation
- ✅ Pre-release validation

### 8. RPC Health Check (`.github/workflows/rpc-health-check.yml`)

**Purpose**: Monitor external API availability

**Triggers**:
- Every 15 minutes
- Manual workflow dispatch

**Jobs**:
- **health-check**: Check API endpoints
  - Crossref API
  - Semantic Scholar API
  - PubMed API
  - Papers With Code API

**Features**:
- ✅ Continuous API monitoring
- ✅ 15-minute check interval
- ✅ Timeout protection
- ✅ Failure notification

### 9. Management (`.github/workflows/management.yml`)

**Purpose**: Repository maintenance and management tasks

**Triggers**:
- Weekly on Mondays at 6 AM UTC
- Manual workflow dispatch

**Jobs**:
- **cleanup-artifacts**: Delete artifacts older than 30 days
- **generate-report**: Generate weekly management report
- **check-dependencies**: Check for outdated dependencies
- **audit-security**: Security audit with bandit and safety

**Features**:
- ✅ Automated artifact cleanup
- ✅ Dependency health checks
- ✅ Security auditing
- ✅ Weekly reporting

### 10. Verify Generated Artifacts (`.github/workflows/verify-artifacts.yml`)

**Purpose**: Verify generated export artifacts

**Triggers**:
- Push to main or develop branches
- Pull requests to main or develop branches
- Manual workflow dispatch

**Jobs**:
- **verify-html-exports**: Verify HTML export generation
- **verify-json-exports**: Verify JSON export generation
- **verify-templates**: Verify HTML template validity

**Features**:
- ✅ HTML export validation
- ✅ JSON export validation
- ✅ Template syntax checking
- ✅ Jinja2 template verification

### 11. Verify Package (`.github/workflows/verify-package.yml`)

**Purpose**: Verify package structure and installation

**Triggers**:
- Push to main or develop branches
- Pull requests to main or develop branches
- Manual workflow dispatch

**Jobs**:
- **verify-package**: Verify package structure and metadata
- **verify-imports**: Verify all module imports
- **verify-setup**: Verify setup.py configuration

**Features**:
- ✅ Package manifest verification
- ✅ Distribution checking
- ✅ Import validation
- ✅ Development installation test

### 12. Scheduled Research (`.github/workflows/scheduled-research.yml`)

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

### 13. Code Quality Workflow (`.github/workflows/code-quality.yml`)

**Purpose**: Type checking and documentation building

**Triggers**:
- Push to main or develop branches
- Pull requests to main or develop branches

**Jobs**:
- **type-check**: Run mypy type checking
- **docs-build**: Build documentation

**Features**:
- ✅ Static type checking
- ✅ Documentation validation
- ✅ Type coverage reporting

### 14. Docker Workflow (`.github/workflows/docker.yml`)

**Purpose**: Build and test Docker images

**Triggers**:
- Push to main branch
- Pull requests to main branch

**Jobs**:
- **docker-build**: Build Docker image
- **docker-test**: Test Docker image

**Features**:
- ✅ Automated Docker builds
- ✅ Docker image testing
- ✅ Multi-platform support

## Required Secrets

### PyPI Publishing
- `PYPI_API_TOKEN`: PyPI API token for package publishing

### Hugging Face Integration
- `HF_TOKEN`: Hugging Face authentication token for dataset export

### Other Services
- Add any additional service-specific tokens as needed

## Workflow Schedule Summary

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| CI | On push/PR | Testing and quality checks |
| CodeQL | Weekly (Sundays) | Security analysis |
| Dependabot | Weekly (Mondays) | Dependency updates |
| Nightly E2E | Daily (2 AM UTC) | End-to-end testing |
| RPC Health Check | Every 15 min | API monitoring |
| Management | Weekly (Mondays 6 AM) | Repository maintenance |
| Scheduled Research | Daily (midnight UTC) | Automated research |
| Verify Artifacts | On push/PR | Artifact validation |
| Verify Package | On push/PR | Package validation |
| Code Quality | On push/PR | Type checking |
| Docker | On push/PR | Docker builds |
| Publish PyPI | On version tags | Package publishing |
| Publish TestPyPI | On test tags | Test publishing |

## Usage

### Manual Workflow Triggers

Most workflows support manual triggering via GitHub Actions UI:

1. Go to Actions tab in repository
2. Select the workflow
3. Click "Run workflow"
4. Configure inputs if applicable
5. Click "Run workflow"

### Dependabot Setup

Dependabot is configured via `.github/dependabot.yml`:
- Automatically creates PRs for dependency updates
- Assigns reviewers and labels
- Runs weekly on Mondays

### CodeQL Setup

CodeQL is configured via `.github/workflows/codeql.yml`:
- Runs weekly and on push/PR
- Uses security-extended queries
- Results appear in Security tab

## Development Dependencies

Created `requirements-dev.txt` with:
- Testing: pytest, pytest-cov
- Code quality: flake8, black, isort, mypy
- Security: bandit, safety
- Optional integrations: huggingface_hub, datasets
- Documentation: sphinx, sphinx-rtd-theme
- Build tools: build, twine

## Troubleshooting

### Workflow Failures

1. Check the Actions tab for failed workflows
2. Review job logs for error details
3. Verify secrets are configured correctly
4. Check for rate limiting or API issues

### Dependabot Issues

- Verify Dependabot is enabled in repository settings
- Check `dependabot.yml` syntax
- Ensure reviewers have write access

### CodeQL Issues

- Verify CodeQL is enabled in repository settings
- Check query configuration
- Review security alerts in Security tab

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

## Best Practices

1. **Secrets Management**: Never commit secrets to repository
2. **Workflow Permissions**: Use minimal required permissions
3. **Rate Limiting**: Be aware of API rate limits
4. **Caching**: Use GitHub Actions cache for speed
5. **Artifact Cleanup**: Enable artifact cleanup to save storage
6. **Security**: Regular security audits and updates
7. **Testing**: Comprehensive test coverage before publishing
8. **Branch Protection**: Enable branch protection rules for `main` to require CI checks
9. **Regular Updates**: Keep GitHub Actions dependencies updated
10. **Monitor Workflows**: Check workflow runs regularly for failures

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Hugging Face Integration Guide](./HUGGINGFACE_INTEGRATION.md)
