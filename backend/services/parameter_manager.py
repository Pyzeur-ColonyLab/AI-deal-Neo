from typing import Dict, Optional
from backend.models.schemas import ModelParameters
import os, json, time
from backend.config import settings

class ParameterManager:
    """
    Handles retrieval, update, reset, and validation of model parameters.
    Tracks changes with timestamps.
    """
    def __init__(self):
        self.params_dir = settings.PARAMS_DIR
        os.makedirs(self.params_dir, exist_ok=True)

    def _param_path(self, model_id: str) -> str:
        return os.path.join(self.params_dir, f"{model_id}.json")

    def get_parameters(self, model_id: str) -> Optional[ModelParameters]:
        path = self._param_path(model_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            return ModelParameters(**data["parameters"])
        return ModelParameters()

    def update_parameters(self, model_id: str, updates: Dict) -> ModelParameters:
        params = self.get_parameters(model_id).dict()
        params.update(updates)
        # Validate ranges (basic example)
        if "temperature" in params:
            params["temperature"] = min(max(params["temperature"], 0.0), 2.0)
        if "top_k" in params:
            params["top_k"] = min(max(params["top_k"], 1), 100)
        # ... add more validation as needed
        data = {
            "parameters": params,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        with open(self._param_path(model_id), "w") as f:
            json.dump(data, f, indent=2)
        return ModelParameters(**params)

    def reset_parameters(self, model_id: str) -> ModelParameters:
        params = ModelParameters().dict()
        data = {
            "parameters": params,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        with open(self._param_path(model_id), "w") as f:
            json.dump(data, f, indent=2)
        return ModelParameters(**params) 