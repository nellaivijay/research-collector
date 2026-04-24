# GitHub Actions Scheduled Research Configuration

This document describes the current GitHub Actions scheduled research workflow configuration for Research-Collector.

## Overview

The scheduled research workflow is configured for daily research on 6 topics (ML, LLM, AGI, ASI, ANI, ACI) with Hugging Face Datasets export.

## Current Configuration

### Scheduled Research
- **Schedule**: Daily at midnight UTC
- **Topics**: Machine Learning (ML), Large Language Models (LLM), Artificial General Intelligence (AGI), Artificial Super Intelligence (ASI), Artificial Narrow Intelligence (ANI), Artificial Collective Intelligence (ACI)
- **Time Range**: 7 days
- **Datasets**:
  - `{repository-owner}/ml-research-daily`
  - `{repository-owner}/llm-research-daily`
  - `{repository-owner}/agi-research-daily`
  - `{repository-owner}/asi-research-daily`
  - `{repository-owner}/ani-research-daily`
  - `{repository-owner}/aci-research-daily`
- **Platform**: Hugging Face Hub

### Manual Research
- **Topics Available**: ML, LLM, AGI, ASI, ANI, ACI, Custom
- **Time Ranges**: 3, 7, 14, or 30 days
- **Dataset**: `{repository-owner}/custom-research` (for custom queries)
- **Source Filtering**: Optional

## Dataset Information

### Primary Datasets
- **ML**: `{repository-owner}/ml-research-daily` - https://huggingface.co/datasets/{repository-owner}/ml-research-daily
- **LLM**: `{repository-owner}/llm-research-daily` - https://huggingface.co/datasets/{repository-owner}/llm-research-daily
- **AGI**: `{repository-owner}/agi-research-daily` - https://huggingface.co/datasets/{repository-owner}/agi-research-daily
- **ASI**: `{repository-owner}/asi-research-daily` - https://huggingface.co/datasets/{repository-owner}/asi-research-daily
- **ANI**: `{repository-owner}/ani-research-daily` - https://huggingface.co/datasets/{repository-owner}/ani-research-daily
- **ACI**: `{repository-owner}/aci-research-daily` - https://huggingface.co/datasets/{repository-owner}/aci-research-daily

**Update Frequency**: Daily
**Research Window**: 7 days
**Content**: Research results from multiple sources

### Custom Research Dataset
- **Name**: `{repository-owner}/custom-research`
- **URL**: https://huggingface.co/datasets/{repository-owner}/custom-research
- **Update Frequency**: On-demand (manual trigger)
- **Content**: Custom query research results

## Setup Requirements

### 1. Hugging Face Setup
1. Create Hugging Face account: https://huggingface.co/
2. Create datasets:
   - `ml-research-daily`
   - `llm-research-daily`
   - `agi-research-daily`
   - `asi-research-daily`
   - `ani-research-daily`
   - `aci-research-daily`
   - `custom-research` (optional, for manual research)
3. For each dataset:
   - Go to https://huggingface.co/new-dataset
   - Name: `{topic}-research-daily`
   - Public: Yes (for sharing)
   - License: MIT
4. Get authentication token: https://huggingface.co/settings/tokens
5. Token type: Write (required for dataset upload)

### 2. GitHub Secrets
1. Go to repository Settings → Secrets and variables → Actions
2. Add secret:
   - Name: `HF_TOKEN`
   - Value: Your Hugging Face token (starts with `hf_`)

### 3. Repository Owner
The workflow uses your GitHub username automatically via `github.repository_owner` context variable.
- GitHub repository: `{repository-owner}/research-collector`
- Repository owner: `{repository-owner}`
- Dataset namespace: `{repository-owner}`

## Workflow Structure

### Daily Schedule (Automatic)
```
research-ml → {repository-owner}/ml-research-daily
research-llm → {repository-owner}/llm-research-daily
research-agi → {repository-owner}/agi-research-daily
research-asi → {repository-owner}/asi-research-daily
research-ani → {repository-owner}/ani-research-daily
research-aci → {repository-owner}/aci-research-daily
```

All jobs run in parallel at midnight UTC.

### Manual Trigger
```
User selects topic:
  - ml → research-ml job → {repository-owner}/ml-research-daily
  - llm → research-llm job → {repository-owner}/llm-research-daily
  - agi → research-agi job → {repository-owner}/agi-research-daily
  - asi → research-asi job → {repository-owner}/asi-research-daily
  - ani → research-ani job → {repository-owner}/ani-research-daily
  - aci → research-aci job → {repository-owner}/aci-research-daily
  - custom → custom-research job → {repository-owner}/custom-research
```

## Usage

### Daily Research (Automatic)
- Runs automatically every day at midnight UTC
- No action required
- Updates all 6 topic datasets

### Manual ML Research
1. Go to Actions → Scheduled Research
2. Click "Run workflow"
3. Select:
   - topic: ml
   - days: 7 (or choose 3, 14, 30)
4. Click "Run workflow"

### Manual LLM Research
1. Go to Actions → Scheduled Research
2. Click "Run workflow"
3. Select:
   - topic: llm
   - days: 7 (or choose 3, 14, 30)
4. Click "Run workflow"

### Manual Custom Research
1. Go to Actions → Scheduled Research
2. Click "Run workflow"
3. Select:
   - topic: custom
   - custom_query: "your search query"
   - days: 7
   - sources: pubmed,reddit (optional)
4. Click "Run workflow"
5. Results go to `{repository-owner}/custom-research`

### Manual Research on Other Topics
1. Go to Actions → Scheduled Research
2. Click "Run workflow"
3. Select topic: agi, asi, ani, or aci
4. Choose days
5. Click "Run workflow"

## Features

- ✅ Daily automated research for 6 topics
- ✅ Hugging Face dataset export
- ✅ Automatic dataset validation
- ✅ Manual trigger for flexibility
- ✅ Custom research support
- ✅ Multiple topic options (ML, LLM, AGI, ASI, ANI, ACI, Custom)
- ✅ Time range selection
- ✅ Source filtering
- ✅ Error handling and resilience
- ✅ Performance caching
- ✅ Timeout protection
- ✅ Parallel job execution
- ✅ Dynamic repository owner detection

## Monitoring

### Check Datasets
- Visit each dataset URL to view:
  - Dataset card for metadata
  - Dataset versions
  - Update frequency
  - Data samples

### Check Workflow
- Go to Actions tab in GitHub
- View Scheduled Research workflow runs
- Check job logs for errors
- Monitor execution time

## Troubleshooting

### Dataset Not Updating
- Verify HF_TOKEN is valid
- Check dataset exists on Hugging Face
- Check workflow has run successfully
- Review job logs for errors

### Workflow Not Running
- Verify schedule is active
- Check workflow is enabled
- Verify GitHub Actions is enabled for repository

### Authentication Error
- Verify HF_TOKEN has write access
- Check token hasn't expired
- Regenerate token if needed

## Future Enhancements

Potential improvements:
- Add Slack/email notifications on failures
- Add dataset quality metrics
- Add research trend analysis
- Add more scheduled topics if needed
- Add weekly comprehensive research
- Add research summary job
