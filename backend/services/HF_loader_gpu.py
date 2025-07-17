# GPU-Optimized version for nva2_a16_ram32_disk50_perf2: 16 CPU, 32GB RAM, 1 GPU (NVIDIA A2)
# This script uses CUDA for inference if available.
import time
import os
import sys
import threading
from datetime import datetime

# Third-Party Imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from huggingface_hub import login
from peft import PeftModel

# --- Performance Optimization Configuration ---
os.environ["TOKENIZERS_PARALLELISM"] = "true"
os.environ["OMP_NUM_THREADS"] = "16"
os.environ["MKL_NUM_THREADS"] = "16"
torch.set_num_threads(16)

# --- Device Selection ---
if torch.cuda.is_available():
    device = "cuda"
    print("✅ CUDA is available. Using GPU for inference.")
else:
    device = "cpu"
    print("⚠️  CUDA is not available. Using CPU for inference. (Performance will be lower)")

# --- Hugging Face Login ---
login()

# --- Model and Tokenizer Configuration ---
base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
finetuned_model_id = "Pyzeur/Code-du-Travail-mistral-finetune"

print(f"🔄 Loading base model: {base_model_id}")
start_time = time.time()

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map=device,
    trust_remote_code=True,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    low_cpu_mem_usage=True,
)

print(f"✅ Base model loaded in {time.time() - start_time:.2f} seconds")

print(f"🔄 Loading fine-tuned model: {finetuned_model_id}")
start_time = time.time()

eval_tokenizer = AutoTokenizer.from_pretrained(
    finetuned_model_id,
    add_bos_token=True,
    trust_remote_code=True,
)

ft_model = PeftModel.from_pretrained(base_model, finetuned_model_id)
print("🔄 Merging fine-tuned adapters with base model...")
ft_model = ft_model.merge_and_unload()

print(f"✅ Fine-tuned model loaded and merged in {time.time() - start_time:.2f} seconds")

ft_model.eval()
ft_model.to(device)

def generate_response(user_question):
    """
    Generate a response for a given user question with high-quality settings and a simple progress animation.
    """
    formatted_prompt = f"""<s>[INST] En tant qu'expert en droit du travail français, explique de façon précise et détaillée : {user_question} [/INST]"""
    print(f"\n🤖 Generating response for: '{user_question}' (high quality mode)")
    print("=" * 50)
    model_input = eval_tokenizer(formatted_prompt, return_tensors="pt").to(device)

    stop_spinner = False
    def spinner():
        symbols = ['|', '/', '-', '\\']
        idx = 0
        while not stop_spinner:
            sys.stdout.write(f"\r⏳ Génération en cours... {symbols[idx % len(symbols)]}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.15)
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    with torch.no_grad():
        start_time = time.time()
        try:
            output = ft_model.generate(
                **model_input,
                max_new_tokens=300,
                repetition_penalty=1.0,
                do_sample=False,
                num_beams=6,
                temperature=0.3,
                top_p=0.95,
                pad_token_id=eval_tokenizer.eos_token_id,
                num_return_sequences=1,
            )
        finally:
            stop_spinner = True
            spinner_thread.join()

        generation_time = time.time() - start_time
        print(f"\n" + "=" * 50)
        print(f"⏱️  Generation completed in {generation_time:.2f} seconds")
        print(f"📊 Generated {len(output[0]) - len(model_input['input_ids'][0])} new tokens")
        full_response = eval_tokenizer.decode(output[0], skip_special_tokens=True)
        return full_response

def main():
    print("\n" + "=" * 60)
    print("🤖 French Labor Law AI Assistant (GPU Optimized)")
    print("=" * 60)
    print("💡 This model is trained on French labor law (Code du Travail)")
    print("💡 Ask questions about employment contracts, rights, obligations, etc.")
    print("💡 Type 'quit' or 'exit' to stop the program")
    print("=" * 60)
    
    while True:
        try:
            user_question = input("\n❓ Your question: ").strip()
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thank you for using the French Labor Law AI Assistant.")
                break
            if not user_question:
                print("⚠️  Please enter a question.")
                continue
            response = generate_response(user_question)
            print("\n📝 Réponse :\n" + response.strip())
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