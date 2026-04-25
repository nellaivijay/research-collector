"""Clean up research collector datasets by truncating records (not deleting datasets)."""

import os
import sys
import argparse
from huggingface_hub import HfApi

# Your Hugging Face token
HF_TOKEN = os.environ.get("HF_TOKEN")

# All dataset repo IDs
ALL_DATASETS = {
    "ml": "nellaivijay/ml-research-daily",
    "llm": "nellaivijay/llm-research-daily",
    "agi": "nellaivijay/agi-research-daily",
    "asi": "nellaivijay/asi-research-daily",
    "ani": "nellaivijay/ani-research-daily",
    "aci": "nellaivijay/aci-research-daily",
}

# Files to preserve (not deleted)
PRESERVE_FILES = ["README.md", ".gitattributes", "dataset_card.json"]

def truncate_datasets(datasets_to_truncate):
    """Truncate records from specified research datasets while preserving repositories."""
    api = HfApi(token=HF_TOKEN)
    
    print("This will truncate records from the following datasets:")
    for dataset in datasets_to_truncate:
        print(f"  - {dataset}")
    print(f"\nPreserved files: {', '.join(PRESERVE_FILES)}")
    
    # Only ask for confirmation if running interactively (not in CI/CD)
    is_ci = os.environ.get("GITHUB_ACTIONS") or os.environ.get("GITLAB_CI")
    if not is_ci:
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            print("Truncation cancelled.")
            return False
    else:
        print("Running in CI/CD mode - skipping confirmation")
    
    success_count = 0
    total_deleted = 0
    
    for repo_id in datasets_to_truncate:
        try:
            # List all files in the dataset
            repo_files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
            
            # Filter out files to preserve
            files_to_delete = [f for f in repo_files if f not in PRESERVE_FILES]
            
            if not files_to_delete:
                print(f"  - {repo_id}: No data files to delete (already empty)")
                success_count += 1
                continue
            
            # Delete each data file
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    api.delete_file(
                        path_in_repo=file_path,
                        repo_id=repo_id,
                        repo_type="dataset",
                        token=HF_TOKEN
                    )
                    deleted_count += 1
                except Exception as e:
                    print(f"    ✗ Error deleting {file_path}: {e}")
            
            if deleted_count == len(files_to_delete):
                print(f"  ✓ {repo_id}: Deleted {deleted_count} data files")
                success_count += 1
                total_deleted += deleted_count
            else:
                print(f"  ⚠ {repo_id}: Partially deleted {deleted_count}/{len(files_to_delete)} files")
                total_deleted += deleted_count
                
        except Exception as e:
            print(f"  ✗ Error truncating {repo_id}: {e}")
    
    print(f"\n✓ Truncation complete! Successfully truncated {success_count}/{len(datasets_to_truncate)} datasets")
    print(f"✓ Total data files deleted: {total_deleted}")
    print("\nTo repopulate the datasets, run the GitHub Actions workflow or use:")
    print("python -m research_collector research --topic <topic> --days 7 --export huggingface --output <repo_id>")
    
    return success_count == len(datasets_to_truncate)

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set")
        print("Set it with: export HF_TOKEN=your_token_here")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Truncate records from research collector datasets")
    parser.add_argument("--dataset", choices=["all", "ml", "llm", "agi", "asi", "ani", "aci"],
                       default="all", help="Dataset to truncate (default: all)")
    
    args = parser.parse_args()
    
    if args.dataset == "all":
        datasets_to_truncate = list(ALL_DATASETS.values())
    else:
        datasets_to_truncate = [ALL_DATASETS[args.dataset]]
    
    success = truncate_datasets(datasets_to_truncate)
    sys.exit(0 if success else 1)
