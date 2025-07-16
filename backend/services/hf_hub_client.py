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
        Download a model from Hugging Face Hub. Returns the local path to the model file.
        For adapter models, always prefer 'adapter_model.safetensors' if present.
        Optionally, also download 'adapter_config.json' if present.
        """
        # Determine file extension by format
        format_ext = {
            "safetensors": ".safetensors",
            "gguf": ".gguf",
            "pytorch": ".bin",
            "onnx": ".onnx"
        }
        ext = format_ext.get(model_format, None)
        files = self.api.list_repo_files(model_name, token=self.token)
        target_file = None

        # 1. Prefer 'adapter_model.safetensors' for adapter models
        if 'adapter_model.safetensors' in files:
            target_file = 'adapter_model.safetensors'
        # 2. Otherwise, prefer any .safetensors file
        elif ext == '.safetensors' or not ext:
            safetensors_files = [f for f in files if f.endswith('.safetensors')]
            if safetensors_files:
                target_file = safetensors_files[0]
        # 3. Otherwise, use extension-based search
        elif ext:
            for f in files:
                if f.endswith(ext):
                    target_file = f
                    break
        # 4. Fallback: pick first file
        if not target_file and files:
            target_file = files[0]
        if not target_file:
            raise RuntimeError(f"No suitable model file found for {model_name}")
        # Download main model file
        local_path = hf_hub_download(
            repo_id=model_name,
            filename=target_file,
            cache_dir=cache_dir,
            token=self.token if self.token else None
        )
        # Optionally, download adapter_config.json if present
        if 'adapter_config.json' in files:
            hf_hub_download(
                repo_id=model_name,
                filename='adapter_config.json',
                cache_dir=cache_dir,
                token=self.token if self.token else None
            )
        return local_path 