from llama_cpp import Llama
import os

MODEL_PATH = "./data/models/phi-2.Q2_K.gguf"  # quantização mais equilibrada

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=os.cpu_count(),
    n_batch=256,
    use_mlock=True,
    use_mmap=True,
    verbose=False
)

def call_llm(prompt: str, max_tokens: int = 256) -> str:
    response = llm(
        prompt.strip(),
        max_tokens=max_tokens,
        temperature=0.1,
        top_p=0.9,
        stop=["</s>", "Question:"]
    )
    return response["choices"][0]["text"].strip()
