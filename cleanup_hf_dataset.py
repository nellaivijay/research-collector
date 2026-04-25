"""Clean up Hugging Face dataset by deleting and recreating it."""

import os
from huggingface_hub import HfApi

# Your Hugging Face token
HF_TOKEN = os.environ.get("HF_TOKEN")  # Or paste your token directly

# Dataset repo ID
REPO_ID = "nellaivijay/ml-research-daily"

def cleanup_dataset():
    """Delete the existing dataset."""
    api = HfApi(token=HF_TOKEN)
    
    try:
        # Delete the repository
        api.delete_repo(repo_id=REPO_ID, repo_type="dataset")
        print(f"✓ Deleted dataset: {REPO_ID}")
    except Exception as e:
        print(f"✗ Error deleting dataset: {e}")
        return False
    
    return True

def recreate_dataset():
    """Create a fresh dataset using the research collector."""
    print("\nNow run the research command to create fresh data:")
    print(f"python -m research_collector research --topic ml --days 7 --export huggingface --output {REPO_ID}")

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set")
        print("Set it with: export HF_TOKEN=your_token_here")
        exit(1)
    
    print(f"Cleaning up dataset: {REPO_ID}")
    print("This will delete ALL data in the dataset.")
    
    # Confirm deletion
    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("Cleanup cancelled.")
        exit(0)
    
    if cleanup_dataset():
        recreate_dataset()
