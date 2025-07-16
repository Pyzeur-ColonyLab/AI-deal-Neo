from typing import Dict, Any

# Add imports for real model loading
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import os

class AIModelRunner:
    """
    Handles AI model inference, supports multiple formats (safetensors, gguf, pytorch, onnx).
    Integrates with Hugging Face Transformers and custom runners.
    Now supports loading adapters (PEFT/LoRA) on top of base models.
    """
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.model_format = None
        self.device = "cpu"  # Change to "cuda" if GPU is available

    def load(self, model_path: str, model_format: str, config: Dict[str, Any] = None):
        """
        Load a Hugging Face model, with optional adapter (PEFT/LoRA) support.
        model_path: path to the main model file (e.g., adapter_model.safetensors or base model)
        model_format: format string (e.g., 'safetensors')
        config: dict with extra info, e.g., base_model_name for adapters
        """
        # Determine if this is an adapter (LoRA/PEFT) or a base model
        model_dir = os.path.dirname(model_path)
        adapter_file = os.path.join(model_dir, "adapter_model.safetensors")
        adapter_config_file = os.path.join(model_dir, "adapter_config.json")
        is_adapter = os.path.exists(adapter_file) and os.path.exists(adapter_config_file)

        if is_adapter:
            # Load base model first
            if not config or "base_model_name" not in config:
                raise ValueError("Adapter model requires 'base_model_name' in config.")
            base_model_name = config["base_model_name"]
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            base_model = AutoModelForCausalLM.from_pretrained(base_model_name, device_map=None)
            # Load adapter using PEFT
            self.model = PeftModel.from_pretrained(base_model, model_dir)
            self.model_id = f"{base_model_name}+adapter"
            self.model_format = model_format
        else:
            # Load as a standard Hugging Face model
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path, device_map=None)
            self.model_id = model_path
            self.model_format = model_format

    def unload(self):
        """
        Unload the model from memory.
        """
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.model_format = None

    def generate_response(self, message: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a response using the loaded model. Uses Hugging Face Transformers pipeline.
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("No model loaded")
        # Example inference (simplified)
        inputs = self.tokenizer(message, return_tensors="pt")
        outputs = self.model.generate(**inputs, **parameters)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response 