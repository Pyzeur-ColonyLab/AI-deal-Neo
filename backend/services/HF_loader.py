# Standard Library Imports
# (None required for this script)

# Third-Party Imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from peft import PeftModel
print("Imports done")

# --- Hugging Face Login ---
login()
print("Login done")
# --- Model and Tokenizer Configuration ---
base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
finetuned_model_id = "Pyzeur/Code-du-Travail-mistral-finetune"
print("Model and Tokenizer Configuration done")
# Load the base model (CPU, no quantization)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="cpu",
    trust_remote_code=True,
)
print("Base model loaded")
# Load the tokenizer from the fine-tuned model repository
eval_tokenizer = AutoTokenizer.from_pretrained(
    finetuned_model_id,
    add_bos_token=True,
    trust_remote_code=True,
)
print("Tokenizer loaded")
# --- Load the Fine-Tuned Model from Hugging Face Hub ---
ft_model = PeftModel.from_pretrained(base_model, finetuned_model_id)
print("Fine-tuned model loaded")
# --- Inference Example ---
eval_prompt = "Qu'est-ce qu'un CDD ?"
model_input = eval_tokenizer(eval_prompt, return_tensors="pt").to("cpu")
print("Model input done")
ft_model.eval()
with torch.no_grad():
    output = ft_model.generate(**model_input, max_new_tokens=100, repetition_penalty=1.15)
    print(eval_tokenizer.decode(output[0], skip_special_tokens=True))