from llama_cpp import Llama
import streamlit as st

MODEL_PATH = "./data/models/phi-2.Q2_K.gguf"

# Streamlit irá cachear a instância do modelo
@st.cache_resource
def get_llm():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4,
        n_batch=256,
        use_mmap=True,
        use_mlock=True,
        verbose=False
    )

def call_llm(prompt: str, max_tokens: int = 256) -> str:
    """
    Faz a chamada ao modelo local via llama-cpp-python.
    """
    llm = get_llm()
    response = llm(
        prompt.strip(),
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.95,
        stop=["</s>", "Question:"]
    )
    return response["choices"][0]["text"].strip()
