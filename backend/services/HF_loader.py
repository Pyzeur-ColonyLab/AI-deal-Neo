# Standard Library Imports
import time
import os
from datetime import datetime

# Third-Party Imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from huggingface_hub import login
from peft import PeftModel

# --- Performance Optimization Configuration ---
# Set environment variables for better CPU performance
os.environ["TOKENIZERS_PARALLELISM"] = "true"  # Enable parallel tokenization
os.environ["OMP_NUM_THREADS"] = "16"  # Use all 16 VCPUs for OpenMP
os.environ["MKL_NUM_THREADS"] = "16"  # Use all 16 VCPUs for MKL
torch.set_num_threads(16)  # Set PyTorch to use all 16 threads

# --- Hugging Face Login ---
# This authenticates with Hugging Face Hub to access private models or models requiring authentication
# Required for downloading models from HF Hub
login()

# --- Model and Tokenizer Configuration ---
# Define the base model (original pre-trained model) and fine-tuned model identifiers
# These are Hugging Face Hub model repository IDs
base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"  # Original Mistral 7B model
finetuned_model_id = "Pyzeur/Code-du-Travail-mistral-finetune"  # Fine-tuned version for French labor law

print(f"🔄 Loading base model: {base_model_id}")
start_time = time.time()

# Load the base model with optimized settings for 16 VCPUs and 32GB RAM
# Parameters explained:
# - device_map="cpu": Forces model to run on CPU (slower but no GPU required)
# - trust_remote_code=True: Allows execution of custom code from the model repository
# - torch_dtype=torch.float16: Use half precision to reduce memory usage
# - low_cpu_mem_usage=True: Optimize memory usage during loading
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="cpu",
    trust_remote_code=True,
    torch_dtype=torch.float16,  # Use half precision to save memory
    low_cpu_mem_usage=True,  # Optimize memory usage
)

print(f"✅ Base model loaded in {time.time() - start_time:.2f} seconds")

print(f"🔄 Loading fine-tuned model: {finetuned_model_id}")
start_time = time.time()

# Load the tokenizer from the fine-tuned model repository
# Parameters explained:
# - add_bos_token=True: Automatically adds beginning-of-sequence token to inputs
# - trust_remote_code=True: Allows custom tokenizer code execution
# The tokenizer converts text to/from token IDs that the model can process
eval_tokenizer = AutoTokenizer.from_pretrained(
    finetuned_model_id,
    add_bos_token=True,
    trust_remote_code=True,
)

# --- Load the Fine-Tuned Model from Hugging Face Hub ---
# PeftModel combines the base model with fine-tuning adapters
# This allows using the fine-tuned weights without replacing the entire model
ft_model = PeftModel.from_pretrained(base_model, finetuned_model_id)

# --- CRITICAL: Merge the fine-tuned adapters with the base model ---
# This ensures the fine-tuned weights are properly applied
print("🔄 Merging fine-tuned adapters with base model...")
ft_model = ft_model.merge_and_unload()

print(f"✅ Fine-tuned model loaded and merged in {time.time() - start_time:.2f} seconds")

# --- Inference Example ---
# Test prompt in French asking about CDD (fixed-term contract)
# Use proper Mistral instruction format for better results
eval_prompt = """<s>[INST] Qu'est-ce qu'un CDD ? [/INST]"""
print(f"\n🤖 Generating response for: 'Qu'est-ce qu'un CDD ?'")
print("=" * 50)

# Tokenize the input prompt and convert to PyTorch tensors
# Parameters explained:
# - return_tensors="pt": Returns PyTorch tensors instead of Python lists
# - .to("cpu"): Ensures tensors are on CPU (matching model device)
model_input = eval_tokenizer(eval_prompt, return_tensors="pt").to("cpu")

# Create a streamer for real-time output
# Parameters explained:
# - skip_prompt=True: Only shows generated text, not the input prompt
# - skip_special_tokens=True: Removes special tokens like [PAD], [EOS] from output
streamer = TextStreamer(eval_tokenizer, skip_prompt=True, skip_special_tokens=True)

# Set model to evaluation mode (disables dropout, batch norm updates)
ft_model.eval()

# Disable gradient computation for inference (saves memory and speeds up generation)
with torch.no_grad():
    start_time = time.time()
    
    # Generate text response with optimized parameters
    # Parameters explained:
    # - max_new_tokens=150: Maximum number of new tokens to generate (increased for better responses)
    # - repetition_penalty=1.1: Penalizes repeated tokens (reduced for more natural flow)
    # - streamer=streamer: Enables real-time streaming of generated text
    # - do_sample=True: Uses sampling instead of greedy decoding (more diverse outputs)
    # - temperature=0.8: Controls randomness (slightly higher for more creative responses)
    # - top_p=0.9: Nucleus sampling - only consider tokens with top 90% probability mass
    # - pad_token_id: Token to use for padding (usually end-of-sequence token)
    output = ft_model.generate(
        **model_input,  # Unpacks the tokenized input (input_ids, attention_mask, etc.)
        max_new_tokens=150,  # Controls response length - increased for better responses
        repetition_penalty=1.1,  # Prevents repetitive text - reduced for more natural flow
        streamer=streamer,  # Enables real-time text streaming
        do_sample=True,  # Uses probabilistic sampling vs greedy decoding
        temperature=0.8,  # Controls randomness: slightly higher for more creative responses
        top_p=0.9,  # Nucleus sampling - only consider top 90% probability tokens
        pad_token_id=eval_tokenizer.eos_token_id,  # Uses EOS token for padding
        num_return_sequences=1,  # Generate only one sequence
        early_stopping=True,  # Stop when EOS token is generated
    )
    
    generation_time = time.time() - start_time
    print(f"\n" + "=" * 50)
    print(f"⏱️  Generation completed in {generation_time:.2f} seconds")
    print(f"📊 Generated {len(output[0]) - len(model_input['input_ids'][0])} new tokens")
    
    # Decode and display the full response for verification
    full_response = eval_tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\n📝 Full response:")
    print(full_response)