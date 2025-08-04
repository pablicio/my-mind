from llama_cpp import Llama

# Instância cacheada (pode usar decorators do seu framework, se quiser)
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path="./data/models/phi-2.Q2_K.gguf",
            n_ctx=2048,
            n_threads=4,
            n_batch=256,
            use_mmap=True,
            use_mlock=True,
            verbose=False
        )
    return _llm

def call_llm(prompt: str, max_tokens: int = 256) -> str:
    llm = get_llm()
    response = llm(
        prompt.strip(),
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.95,
        stop=["</s>", "Question:"]
    )
    return response["choices"][0]["text"].strip()
