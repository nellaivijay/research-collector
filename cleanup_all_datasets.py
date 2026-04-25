"""Clean up research collector datasets."""

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

def cleanup_datasets(datasets_to_clean):
    """Delete specified research datasets."""
    api = HfApi(token=HF_TOKEN)
    
    print("This will delete the following datasets:")
    for dataset in datasets_to_clean:
        print(f"  - {dataset}")
    
    # Only ask for confirmation if running interactively (not in GitHub Actions)
    if not os.environ.get("GITHUB_ACTIONS"):
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            print("Cleanup cancelled.")
            return False
    
    success_count = 0
    for repo_id in datasets_to_clean:
        try:
            api.delete_repo(repo_id=repo_id, repo_type="dataset")
            print(f"✓ Deleted: {repo_id}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error deleting {repo_id}: {e}")
    
    print(f"\n✓ Cleanup complete! Deleted {success_count}/{len(datasets_to_clean)} datasets")
    print("\nTo recreate the datasets, run the GitHub Actions workflow or use:")
    print("python -m research_collector research --topic <topic> --days 7 --export huggingface --output <repo_id>")
    
    return success_count == len(datasets_to_clean)

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set")
        print("Set it with: export HF_TOKEN=your_token_here")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Clean up research collector datasets")
    parser.add_argument("--dataset", choices=["all", "ml", "llm", "agi", "asi", "ani", "aci"],
                       default="all", help="Dataset to clean (default: all)")
    
    args = parser.parse_args()
    
    if args.dataset == "all":
        datasets_to_clean = list(ALL_DATASETS.values())
    else:
        datasets_to_clean = [ALL_DATASETS[args.dataset]]
    
    success = cleanup_datasets(datasets_to_clean)
    sys.exit(0 if success else 1)
