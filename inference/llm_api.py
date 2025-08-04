from llama_cpp import Llama

# Caminho do modelo GGUF baixado
MODEL_PATH = "./data/models/phi-2.Q2_K.gguf"

# Inicializa o modelo com 2K tokens de contexto (ou aumente conforme necessário)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    verbose=False
)

def call_llm(prompt: str, max_tokens: int = 256) -> str:
    """
    Faz a chamada ao modelo local via llama-cpp-python.
    """
    response = llm(
        prompt.strip(),
        max_tokens=max_tokens,
        temperature=0.1,
        top_p=0.95,
        stop=["</s>", "Question:"]
    )
    return response["choices"][0]["text"].strip()
