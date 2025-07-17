# Standard Library Imports
import time
from datetime import datetime

# Third-Party Imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from huggingface_hub import login
from peft import PeftModel

# --- Hugging Face Login ---
login()

# --- Model and Tokenizer Configuration ---
base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
finetuned_model_id = "Pyzeur/Code-du-Travail-mistral-finetune"

print(f"🔄 Loading base model: {base_model_id}")
start_time = time.time()

# Load the base model (CPU, no quantization)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="cpu",
    trust_remote_code=True,
)

print(f"✅ Base model loaded in {time.time() - start_time:.2f} seconds")

print(f"🔄 Loading fine-tuned model: {finetuned_model_id}")
start_time = time.time()

# Load the tokenizer from the fine-tuned model repository
eval_tokenizer = AutoTokenizer.from_pretrained(
    finetuned_model_id,
    add_bos_token=True,
    trust_remote_code=True,
)

# --- Load the Fine-Tuned Model from Hugging Face Hub ---
ft_model = PeftModel.from_pretrained(base_model, finetuned_model_id)

print(f"✅ Fine-tuned model loaded in {time.time() - start_time:.2f} seconds")

# --- Inference Example ---
eval_prompt = "Qu'est-ce qu'un CDD ?"
print(f"\n🤖 Generating response for: '{eval_prompt}'")
print("=" * 50)

model_input = eval_tokenizer(eval_prompt, return_tensors="pt").to("cpu")

# Create a streamer for real-time output
streamer = TextStreamer(eval_tokenizer, skip_prompt=True, skip_special_tokens=True)

ft_model.eval()
with torch.no_grad():
    start_time = time.time()
    
    # Generate with streaming
    output = ft_model.generate(
        **model_input, 
        max_new_tokens=100, 
        repetition_penalty=1.15,
        streamer=streamer,
        do_sample=True,
        temperature=0.7,
        pad_token_id=eval_tokenizer.eos_token_id
    )
    
    generation_time = time.time() - start_time
    print(f"\n" + "=" * 50)
    print(f"⏱️  Generation completed in {generation_time:.2f} seconds")
    print(f"📊 Generated {len(output[0]) - len(model_input['input_ids'][0])} new tokens")