"""Clean up Hugging Face dataset by truncating records (not deleting the dataset)."""

import os
from huggingface_hub import HfApi, HfFileSystem
from huggingface_hub.utils import hf_hub_url

# Your Hugging Face token
HF_TOKEN = os.environ.get("HF_TOKEN")  # Or paste your token directly

# Dataset repo ID
REPO_ID = "nellaivijay/ml-research-daily"

# Files to preserve (not deleted)
PRESERVE_FILES = ["README.md", ".gitattributes", "dataset_card.json"]

def truncate_dataset():
    """Truncate all records from the dataset while keeping the repository."""
    api = HfApi(token=HF_TOKEN)
    fs = HfFileSystem(token=HF_TOKEN)
    
    try:
        # List all files in the dataset
        repo_files = api.list_repo_files(repo_id=REPO_ID, repo_type="dataset")
        print(f"Found {len(repo_files)} files in dataset")
        
        # Filter out files to preserve
        files_to_delete = [f for f in repo_files if f not in PRESERVE_FILES]
        
        if not files_to_delete:
            print("No data files to delete (dataset is already empty)")
            return True
        
        print(f"Deleting {len(files_to_delete)} data files (preserving: {', '.join(PRESERVE_FILES)})")
        
        # Delete each data file
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                api.delete_file(
                    path_in_repo=file_path,
                    repo_id=REPO_ID,
                    repo_type="dataset",
                    token=HF_TOKEN
                )
                deleted_count += 1
                print(f"  ✓ Deleted: {file_path}")
            except Exception as e:
                print(f"  ✗ Error deleting {file_path}: {e}")
        
        print(f"\n✓ Successfully deleted {deleted_count}/{len(files_to_delete)} data files")
        print(f"✓ Dataset repository preserved: {REPO_ID}")
        print(f"✓ Preserved files: {', '.join(PRESERVE_FILES)}")
        
        return deleted_count == len(files_to_delete)
        
    except Exception as e:
        print(f"✗ Error truncating dataset: {e}")
        return False

def refresh_dataset():
    """Refresh the dataset with fresh data using the research collector."""
    print("\nNow run the research command to populate with fresh data:")
    print(f"python -m research_collector research --topic ml --days 7 --export huggingface --output {REPO_ID}")

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set")
        print("Set it with: export HF_TOKEN=your_token_here")
        exit(1)
    
    print(f"Truncating dataset records: {REPO_ID}")
    print("This will DELETE ALL DATA FILES while preserving the dataset repository.")
    print(f"Preserved files: {', '.join(PRESERVE_FILES)}")
    
    # Confirm truncation
    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("Truncation cancelled.")
        exit(0)
    
    if truncate_dataset():
        refresh_dataset()
