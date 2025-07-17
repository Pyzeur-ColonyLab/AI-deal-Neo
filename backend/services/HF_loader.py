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
# The eval_tokenizer is a text processor that:
# 1. Converts human text into numerical tokens the model can understand
# 2. Converts model output tokens back into readable text
# 3. Handles special tokens like <s>, </s>, [INST], [/INST], etc.
# Parameters explained:
# - add_bos_token=True: Automatically adds beginning-of-sequence token to inputs
# - trust_remote_code=True: Allows custom tokenizer code execution
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

# Set model to evaluation mode (disables dropout, batch norm updates)
ft_model.eval()

def generate_response(user_question):
    """
    Generate a response for a given user question.
    
    Args:
        user_question (str): The question to ask the model
        
    Returns:
        str: The model's response
    """
    # Format the prompt using Mistral's instruction format
    formatted_prompt = f"""<s>[INST] {user_question} [/INST]"""
    
    print(f"\n🤖 Generating response for: '{user_question}'")
    print("=" * 50)
    
    # Tokenize the input prompt and convert to PyTorch tensors
    # The tokenizer converts text into numerical tokens the model can process
    model_input = eval_tokenizer(formatted_prompt, return_tensors="pt").to("cpu")
    
    # Create a streamer for real-time output
    # This shows the response as it's being generated, token by token
    streamer = TextStreamer(eval_tokenizer, skip_prompt=True, skip_special_tokens=True)
    
    # Disable gradient computation for inference (saves memory and speeds up generation)
    with torch.no_grad():
        start_time = time.time()
        
        # Generate text response with optimized parameters
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
        
        # Decode and return the full response
        full_response = eval_tokenizer.decode(output[0], skip_special_tokens=True)
        return full_response

def main():
    """
    Main interactive function for asking questions to the model.
    """
    print("\n" + "=" * 60)
    print("🤖 French Labor Law AI Assistant")
    print("=" * 60)
    print("💡 This model is trained on French labor law (Code du Travail)")
    print("💡 Ask questions about employment contracts, rights, obligations, etc.")
    print("💡 Type 'quit' or 'exit' to stop the program")
    print("=" * 60)
    
    while True:
        try:
            # Get user input
            user_question = input("\n❓ Your question: ").strip()
            
            # Check for exit commands
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thank you for using the French Labor Law AI Assistant.")
                break
            
            # Check for empty input
            if not user_question:
                print("⚠️  Please enter a question.")
                continue
            
            # Generate and display response
            response = generate_response(user_question)
            
            # Ask if user wants to continue
            print("\n" + "-" * 40)
            continue_choice = input("🔄 Ask another question? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', 'oui', 'o']:
                print("👋 Goodbye! Thank you for using the French Labor Law AI Assistant.")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thank you for using the French Labor Law AI Assistant.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Please try again.")

if __name__ == "__main__":
    main()