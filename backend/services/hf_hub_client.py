from typing import Optional
from huggingface_hub import hf_hub_download, HfApi, HfFolder
import os

class HuggingFaceHubClient:
    """
    Handles downloading models from Hugging Face Hub, supports authentication and progress tracking.
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("HF_TOKEN", "")
        self.api = HfApi(token=self.token) if self.token else HfApi()

    def download_model(self, model_name: str, model_format: Optional[str] = None, cache_dir: Optional[str] = None) -> str:
        """
        Download all files for a model from Hugging Face Hub into a dedicated subdirectory. Returns the local model directory path.
        """
        # Create a subdirectory for this model
        model_dir_name = model_name.replace('/', '-')
        model_dir = os.path.join(cache_dir or './models/cache', model_dir_name)
        os.makedirs(model_dir, exist_ok=True)
        files = self.api.list_repo_files(model_name, token=self.token)
        # Download all files in the repo
        for f in files:
            hf_hub_download(
                repo_id=model_name,
                filename=f,
                cache_dir=model_dir,
                token=self.token if self.token else None
            )
        return model_dir 