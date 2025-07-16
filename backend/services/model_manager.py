import os
from typing import List, Dict, Optional
from backend.models.schemas import ModelInfo, ModelParameters
from backend.config import settings
from backend.services.hf_hub_client import HuggingFaceHubClient
import time
import json

class ModelManager:
    """
    Handles model listing, loading, unloading, downloading, and status tracking.
    Enforces only one model loaded in memory at a time.
    Integrates with Hugging Face Hub for downloads.
    """
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self.loaded_model_id: Optional[str] = None
        self.model_cache_dir = settings.MODEL_CACHE_DIR
        os.makedirs(self.model_cache_dir, exist_ok=True)
        self.hf_client = HuggingFaceHubClient()
        self._load_metadata()

    def _metadata_path(self):
        return os.path.join(self.model_cache_dir, "models.json")

    def _load_metadata(self):
        path = self._metadata_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                for m in data:
                    self.models[m["id"]] = ModelInfo(**m)

    def _save_metadata(self):
        path = self._metadata_path()
        with open(path, "w") as f:
            json.dump([m.dict() for m in self.models.values()], f, indent=2)

    def list_models(self) -> List[ModelInfo]:
        """Return all available models with status."""
        return list(self.models.values())

    def load_model(self, model_id: str, config: Optional[dict] = None) -> ModelInfo:
        """
        Load a model into memory, unloading any currently loaded model.
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        if self.loaded_model_id and self.loaded_model_id != model_id:
            self.unload_model(self.loaded_model_id)
        # Simulate loading (real logic in AIModelRunner)
        self.loaded_model_id = model_id
        self.models[model_id].status = "loaded"
        self._save_metadata()
        return self.models[model_id]

    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        """
        if self.loaded_model_id == model_id:
            self.models[model_id].status = "available"
            self.loaded_model_id = None
            self._save_metadata()
            return True
        return False

    def download_model(self, model_name: str, model_format: Optional[str] = None, auth_token: Optional[str] = None) -> str:
        """
        Download a model from Hugging Face Hub and add to model list.
        """
        local_path = self.hf_client.download_model(model_name, model_format, cache_dir=self.model_cache_dir)
        model_id = os.path.basename(local_path)
        info = ModelInfo(
            id=model_id,
            name=model_name,
            status="available",
            format=model_format or "unknown",
            size=os.path.getsize(local_path),
            source="huggingface",
            parameters=ModelParameters()
        )
        self.models[model_id] = info
        self._save_metadata()
        return model_id

    def get_loaded_model(self) -> Optional[ModelInfo]:
        if self.loaded_model_id:
            return self.models.get(self.loaded_model_id)
        return None 