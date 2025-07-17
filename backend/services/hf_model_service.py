import time
import os
from datetime import datetime
import threading
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from peft import PeftModel

class HFModelService:
    """
    HFModelService provides a unified interface for loading, unloading, and running inference on Hugging Face models,
    including support for PEFT/LoRA adapters. This class is designed to be used as a singleton service by the API layer.
    """
    def __init__(self):
        # Model and tokenizer objects
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.base_model_id = None
        self.finetuned_model_id = None
        self.device = "cpu"  # Change to "cuda" if GPU is available
        # Default generation parameters (can be updated per request)
        self.parameters = {
            "max_new_tokens": 300,
            "repetition_penalty": 1.0,
            "do_sample": False,
            "num_beams": 6,
            "temperature": 0.3,
            "top_p": 0.95,
            "pad_token_id": None,
            "num_return_sequences": 1
        }
        self.last_loaded = None
        self.last_unloaded = None
        self.last_parameters_update = None
        # Performance optimization for multi-core CPUs
        os.environ["TOKENIZERS_PARALLELISM"] = "true"
        os.environ["OMP_NUM_THREADS"] = "16"
        os.environ["MKL_NUM_THREADS"] = "16"
        torch.set_num_threads(16)
        # Login to Hugging Face Hub (token should be set in env or config)
        login(token=os.getenv("HF_TOKEN"))

    def load_model(self, base_model_id: str, finetuned_model_id: str = None, config: dict = None):
        """
        Load a base model and optionally a fine-tuned adapter (PEFT/LoRA) from Hugging Face Hub.
        This logic exactly matches the working @HF_loader.py script:
        - Always load the base model from Hugging Face Hub
        - Always load the tokenizer from the finetuned model if present
        - Always merge the adapter with the base model
        """
        self.unload_model()  # Always unload previous model
        self.base_model_id = base_model_id
        self.finetuned_model_id = finetuned_model_id
        # Always load base model from Hugging Face Hub
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            device_map=self.device,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        )
        # Always load tokenizer from finetuned model if present, else from base
        tokenizer_id = finetuned_model_id if finetuned_model_id else base_model_id
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_id,
            add_bos_token=True,
            trust_remote_code=True,
        )
        # If finetuned model, load adapter and merge with base model
        if finetuned_model_id:
            adapter = PeftModel.from_pretrained(self.model, finetuned_model_id)
            self.model = adapter.merge_and_unload()
        self.model.eval()
        self.model_id = finetuned_model_id or base_model_id
        self.last_loaded = datetime.utcnow().isoformat() + "Z"
        # Ensure pad_token_id is set for generation
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.parameters["pad_token_id"] = self.tokenizer.pad_token_id

    def unload_model(self):
        """
        Unload the current model and tokenizer from memory. Frees up resources.
        """
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.base_model_id = None
        self.finetuned_model_id = None
        self.last_unloaded = datetime.utcnow().isoformat() + "Z"

    def is_model_loaded(self) -> bool:
        """
        Check if a model is currently loaded.
        Returns:
            bool: True if model is loaded, False otherwise.
        """
        return self.model is not None and self.tokenizer is not None

    def generate_response(self, message: str, parameters: dict = None) -> str:
        """
        Generate a response for a given message using the loaded model and tokenizer.
        Args:
            message (str): The input prompt or user message.
            parameters (dict, optional): Generation parameters to override defaults.
        Returns:
            str: The generated response text.
        Raises:
            RuntimeError: If no model is loaded.
        """
        if not self.is_model_loaded():
            raise RuntimeError("No model loaded. Please ensure the model is loaded before making inference requests.")
        
        prompt = message
        # Tokenize input and move to correct device
        model_input = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        # Merge provided parameters with defaults
        params = self.parameters.copy()
        if parameters:
            params.update(parameters)
        # Remove None values (required by HF generate)
        params = {k: v for k, v in params.items() if v is not None}
        with torch.no_grad():
            output = self.model.generate(
                **model_input,
                **params
            )
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return response

    def get_parameters(self) -> dict:
        """
        Get the current generation parameters used by the model.
        Returns:
            dict: Current generation parameters.
        """
        return self.parameters.copy()

    def update_parameters(self, updates: dict) -> dict:
        """
        Update generation parameters (with basic validation).
        Args:
            updates (dict): Parameters to update.
        Returns:
            dict: Updated parameters.
        """
        for k, v in updates.items():
            if k in self.parameters:
                self.parameters[k] = v
        self.last_parameters_update = datetime.utcnow().isoformat() + "Z"
        return self.get_parameters()

    def reset_parameters(self) -> dict:
        """
        Reset generation parameters to default values.
        Returns:
            dict: Default parameters after reset.
        """
        self.parameters = {
            "max_new_tokens": 300,
            "repetition_penalty": 1.0,
            "do_sample": False,
            "num_beams": 6,
            "temperature": 0.3,
            "top_p": 0.95,
            "pad_token_id": self.tokenizer.pad_token_id if self.tokenizer else None,
            "num_return_sequences": 1
        }
        self.last_parameters_update = datetime.utcnow().isoformat() + "Z"
        return self.get_parameters() 