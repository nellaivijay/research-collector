# Dataset Cleanup Guide

Guide for managing and cleaning up Research-Collector datasets on Hugging Face.

## Overview

Research-Collector provides automated tools for managing dataset storage on Hugging Face. The cleanup system is designed to preserve dataset repositories while removing data records, allowing fresh data population without recreating repositories.

## Cleanup Behavior

### Truncate vs Delete

The cleanup system uses a **truncate approach** rather than deleting entire repositories:

**What is preserved:**
- Dataset repository structure
- README.md file
- .gitattributes file  
- dataset_card.json metadata file
- Repository settings and configuration

**What is removed:**
- All data files (parquet, json, csv, etc.)
- Data records from the dataset
- Cached data

**Benefits:**
- Maintains dataset repository identity
- Preserves dataset documentation
- Allows quick data refresh
- No need to recreate repositories
- Maintains dataset URLs and integration points

## Cleanup Scripts

### 1. Single Dataset Cleanup (`cleanup_hf_dataset.py`)

Cleans up a single Hugging Face dataset by removing data files while preserving repository structure.

**Usage:**

```bash
# Set environment variables
export HF_TOKEN="your_huggingface_token"
export DATASET_OWNER="your_username"

# Run cleanup for a single dataset
python cleanup_hf_dataset.py --dataset ml-research-daily

# Or run without arguments (uses default)
python cleanup_hf_dataset.py
```

**Environment Variables:**
- `HF_TOKEN`: Hugging Face API token (required)
- `DATASET_OWNER`: Hugging Face username (optional, defaults to environment or config)

**What it does:**
1. Connects to Hugging Face Hub
2. Lists all files in the dataset repository
3. Deletes data files (parquet, json, csv, etc.)
4. Preserves README.md, .gitattributes, dataset_card.json
5. Reports cleanup summary

**Example Output:**
```
Connecting to Hugging Face...
Dataset: nellaivijay/ml-research-daily
Files in dataset: 12
Preserving: README.md, .gitattributes, dataset_card.json
Deleting data files: 9
Cleanup complete.
```

### 2. Multiple Dataset Cleanup (`cleanup_all_datasets.py`)

Cleans up multiple datasets in batch, useful for periodic maintenance.

**Usage:**

```bash
# Set environment variables
export HF_TOKEN="your_huggingface_token"
export DATASET_OWNER="your_username"

# Clean up all datasets
python cleanup_all_datasets.py --dataset all

# Clean up specific datasets
python cleanup_all_datasets.py --dataset ml-research-daily,llm-research-daily

# Clean up datasets for specific topics
python cleanup_all_datasets.py --dataset ml,llm,agi
```

**Environment Variables:**
- `HF_TOKEN`: Hugging Face API token (required)
- `DATASET_OWNER`: Hugging Face username (optional, defaults to environment or config)

**Supported Datasets:**
- `ml-research-daily` (Machine Learning)
- `llm-research-daily` (Large Language Models)
- `agi-research-daily` (Artificial General Intelligence)
- `asi-research-daily` (Artificial Super Intelligence)
- `aci-research-daily` (Artificial Collective Intelligence)
- `ani-research-daily` (Artificial Narrow Intelligence)

**What it does:**
1. Validates Hugging Face token
2. Processes each specified dataset
3. For each dataset:
   - Lists all files
   - Preserves metadata files
   - Deletes data files
   - Reports cleanup status
4. Provides overall summary

**Example Output:**
```
Processing datasets: ml-research-daily, llm-research-daily
[1/2] Cleaning ml-research-daily...
  Preserving: README.md, .gitattributes, dataset_card.json
  Deleted: 9 data files
[2/2] Cleaning llm-research-daily...
  Preserving: README.md, .gitattributes, dataset_card.json
  Deleted: 8 data files
Cleanup complete. Total: 2 datasets, 17 data files deleted.
```

## GitHub Actions Workflow

### Automated Cleanup (`.github/workflows/cleanup-datasets.yml`)

Automated workflow for periodic dataset cleanup.

**Triggers:**
- Manual workflow dispatch
- Can be scheduled (commented out by default)

**Features:**
- Truncates records from multiple datasets
- Preserves repository structure and metadata
- Configurable dataset selection
- Detailed logging and reporting

**Usage:**

1. Go to: https://github.com/nellaivijay/research-collector/actions/workflows/cleanup-datasets.yml
2. Click "Run workflow"
3. Select datasets to clean (or choose "all")
4. Click "Run workflow"

**Workflow Configuration:**

```yaml
name: Truncate Dataset Records

on:
  workflow_dispatch:
    inputs:
      datasets:
        description: 'Datasets to clean (comma-separated or "all")'
        required: false
        default: 'all'
```

## Best Practices

### When to Clean Up

1. **Before Major Updates**: Clean datasets before significant data collection changes
2. **Periodic Maintenance**: Regular cleanup to manage storage (monthly/quarterly)
3. **Data Quality Issues**: Clean when data quality problems are detected
4. **Schema Changes**: Clean before making structural changes to data format

### Safety Considerations

1. **Backup Important Data**: Ensure you have backups if needed before cleanup
2. **Test First**: Test cleanup scripts on non-production datasets first
3. **Verify Token Permissions**: Ensure HF_TOKEN has write permissions
4. **Monitor Results**: Review cleanup logs to ensure expected behavior

### Data Preservation

The cleanup system is designed to be safe:

- **Never deletes repositories**: Only removes data files
- **Preserves documentation**: Keeps README.md and metadata
- **Maintains integration points**: Dataset URLs remain valid
- **Reversible**: Fresh data can be collected immediately after cleanup

## Troubleshooting

### Common Issues

#### Authentication Failed

**Error:** `HTTP 401: Unauthorized`

**Solution:**
- Verify HF_TOKEN is correct
- Check token has write permissions
- Ensure token hasn't expired

#### Dataset Not Found

**Error:** `HTTP 404: Not Found`

**Solution:**
- Verify dataset name is correct
- Check DATASET_OWNER is set properly
- Ensure dataset exists on Hugging Face

#### Permission Denied

**Error:** `HTTP 403: Forbidden`

**Solution:**
- Verify token has write permissions
- Check you are the dataset owner
- Ensure repository settings allow write access

#### File Deletion Failed

**Error:** `Failed to delete file: filename.parquet`

**Solution:**
- Check file is not locked by another process
- Verify token has delete permissions
- Ensure file exists in the dataset

### Recovery

If cleanup fails or deletes wrong files:

1. **Check Workflow Logs**: Review GitHub Actions logs for details
2. **Verify Dataset Status**: Check dataset on Hugging Face Hub
3. **Re-run Research**: Collect fresh data using research workflows
4. **Contact Support**: If issues persist, check Hugging Face status

## Integration with CI/CD

### Pre-deployment Cleanup

Add cleanup to your deployment pipeline:

```yaml
- name: Clean up datasets
  env:
    HF_TOKEN: ${{ secrets.HF_TOKEN }}
  run: |
    python cleanup_all_datasets.py --dataset all
```

### Post-collection Cleanup

Automatically clean after data collection:

```yaml
- name: Collect research data
  run: python -m research_collector research --topic ml

- name: Clean old data
  run: python cleanup_hf_dataset.py --dataset ml-research-daily
```

## Monitoring and Reporting

### Cleanup Metrics

Track cleanup operations:

- Number of datasets cleaned
- Files deleted per dataset
- Storage space freed
- Cleanup duration
- Error rates

### Logging

Cleanup scripts provide detailed logs:

- Files processed
- Files preserved vs deleted
- Error messages
- Operation timing
- Summary statistics

## Advanced Usage

### Custom Dataset Lists

Clean specific datasets:

```bash
python cleanup_all_datasets.py --dataset ml-research-daily,agi-research-daily
```

### Dry Run Mode

To see what would be deleted without actually deleting:

```python
# Add dry-run mode to scripts
# (This would require script modification)
```

### Selective File Preservation

Modify scripts to preserve additional file types:

```python
# In cleanup_hf_dataset.py
PRESERVED_FILES = ['README.md', '.gitattributes', 'dataset_card.json', 'custom_file.txt']
```

## Educational Purpose

This cleanup system is designed for educational purposes:

- **Learning Data Management**: Understand dataset lifecycle management
- **Storage Optimization**: Learn about efficient data storage practices
- **Automation Skills**: Practice automated maintenance workflows
- **API Integration**: Learn Hugging Face Hub API usage

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review GitHub Actions workflow logs
3. Open an issue on GitHub with cleanup logs attached
4. Consult Hugging Face documentation for API-specific issues

## Related Documentation

- [Hugging Face Integration Guide](HUGGINGFACE_INTEGRATION.md)
- [GitHub Actions Guide](GITHUB_ACTIONS.md)
- [Source Health Check](SOURCE_HEALTH_CHECK.md)
