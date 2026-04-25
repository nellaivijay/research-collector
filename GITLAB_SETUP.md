# GitLab CI/CD Setup for Research-Collector

This document explains how to set up scheduled research jobs in GitLab CI/CD.

## Prerequisites

1. **GitLab Repository**: Push your code to a GitLab repository
2. **HF_TOKEN**: Add Hugging Face token to GitLab CI/CD variables
3. **GitLab Runner**: Ensure you have a GitLab runner with Docker executor

## Setting Up HF_TOKEN in GitLab

1. Go to your GitLab project
2. Navigate to **Settings** → **CI/CD** → **Variables**
3. Click **Add variable**
4. Add:
   - **Key**: `HF_TOKEN`
   - **Value**: Your Hugging Face token (get from https://huggingface.co/settings/tokens)
   - **Masked**: Check to hide the token
   - **Protected**: Uncheck (unless you want to restrict to protected branches)

## Setting Up Scheduled Jobs

### Option 1: Using GitLab UI (Recommended)

1. Go to your GitLab project
2. Navigate to **CI/CD** → **Schedules**
3. Click **New schedule**
4. Configure:
   - **Description**: "Daily ML Research"
   - **Interval pattern**: "Custom" or "Daily"
   - **Cron**: `0 0 * * *` (runs daily at midnight UTC)
   - **Target branch**: `main`
   - **Variables** (if needed):
     - `TOPIC`: `ml`
     - `DAYS`: `7`
5. Click **Save schedule**

Repeat for each topic (llm, agi, asi, ani, aci).

### Option 2: Using GitLab API

```bash
# Create schedule for ML research
curl --request POST \
  --header "PRIVATE-TOKEN: your_gitlab_token" \
  --header "Content-Type: application/json" \
  --data '{
    "description": "Daily ML Research",
    "cron": "0 0 * * *",
    "timezone": "UTC",
    "active": true
  }' \
  "https://gitlab.com/api/v4/projects/your_project_id/pipeline_schedules"
```

### Cron Schedule Examples

- **Daily at midnight UTC**: `0 0 * * *`
- **Daily at 9 AM UTC**: `0 9 * * *`
- **Every 6 hours**: `0 */6 * * *`
- **Every Monday at midnight**: `0 0 * * 1`
- **Weekdays at 9 AM UTC**: `0 9 * * 1-5`

## Manual Trigger

To manually trigger a research job:

1. Go to **CI/CD** → **Pipelines**
2. Click **Run pipeline**
3. Select branch: `main`
4. For manual job, add variables:
   - `TOPIC`: `ml` (or llm, agi, asi, ani, aci)
   - `DAYS`: `7` (or any number)
5. Click **Run pipeline**

## Cleanup Workflow

To clean up datasets, you can create a manual cleanup job:

```yaml
cleanup-datasets:
  stage: research
  image: python:3.10
  script:
    - pip install huggingface_hub
    - python cleanup_all_datasets.py --dataset all
  when: manual
  only:
    - main
  tags:
    - docker
```

## Monitoring

- **View pipelines**: Go to **CI/CD** → **Pipelines**
- **View schedules**: Go to **CI/CD** → **Schedules**
- **View job logs**: Click on any job in the pipeline view

## Troubleshooting

### Job Fails with HF_TOKEN Error

- Ensure `HF_TOKEN` is set in CI/CD variables
- Check that the token is not masked incorrectly
- Verify the token has write permissions to Hugging Face

### Runner Not Available

- Ensure you have a GitLab runner with Docker executor
- Check runner tags match job tags (`docker`)
- Verify runner is active

### Schedule Not Triggering

- Check that the schedule is **active**
- Verify the cron syntax is correct
- Ensure the target branch exists
- Check timezone settings

## Differences from GitHub Actions

| Feature | GitHub Actions | GitLab CI/CD |
|---------|--------------|--------------|
| Schedules | workflow_dispatch + cron | Pipeline Schedules |
| Manual Trigger | workflow_dispatch | Manual job trigger |
| Secrets | GitHub Secrets | CI/CD Variables |
| Runner | GitHub-hosted | Self-hosted or GitLab-hosted |
| UI | Actions tab | CI/CD tab |

## Migration from GitHub Actions

If you're migrating from GitHub Actions:

1. Copy environment variables from GitHub Secrets to GitLab CI/CD Variables
2. Replace GitHub Actions workflow with GitLab CI/CD configuration
3. Set up new schedules in GitLab
4. Disable GitHub Actions schedules (if keeping both)
