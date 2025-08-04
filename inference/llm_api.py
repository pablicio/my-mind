import streamlit as st
from llama_cpp import Llama
import os

from typing import List
from langchain_core.documents import Document
from etl.load.vector_writer import VectorWriter
import warnings

warnings.filterwarnings("ignore", message=".*was not set")

MODEL_PATH = "./data/models/phi-2.Q2_K.gguf"

# 1. Função cacheada para carregar o modelo LLaMA
@st.cache_resource
def load_llm():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=os.cpu_count(),
        n_batch=256,
        use_mmap=True,
        use_mlock=True,
        verbose=False
    )

# 2. Função cacheada para carregar o VectorWriter
@st.cache_resource
def load_vector_writer() -> VectorWriter:
    return VectorWriter(persist_directory="./data/output/embeddings")

# 3. Função para chamar o LLaMA (recebe o modelo como argumento)
def call_llm(llm_model: Llama, prompt: str, max_tokens: int = 256) -> str:
    response = llm_model(
        prompt.strip(),
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.95,
        stop=["</s>", "Question:"]
    )
    return response["choices"][0]["text"].strip()

# 4. Monta prompt com contexto
def montar_prompt_com_contexto(vector_writer: VectorWriter, pergunta: str, k: int = 3) -> str:
    docs: List[Document] = vector_writer.query(pergunta, k=k)
    contexto = "\n\n".join(doc.page_content for doc in docs)
    return f"""Responda com base nos documentos abaixo.

{contexto}

Pergunta: {pergunta}
Resposta:"""

# 5. Função principal do app
def chat_app():
    st.set_page_config(page_title="RAG com LLaMA", page_icon="🧠")
    st.title("🧠 RAG com LLaMA Local + Chroma")

    # Carrega recursos cacheados
    llm = load_llm()
    vector_writer = load_vector_writer()

    user_prompt = st.text_area("Digite sua pergunta:", height=150)

    col1, col2 = st.columns(2)
    with col1:
        max_tokens = st.slider("Máx. Tokens", 50, 1024, 256)
    with col2:
        k = st.slider("Docs de contexto (top-k)", 1, 10, 3)

    if st.button("Responder"):
        if user_prompt.strip():
            with st.spinner("Buscando contexto e gerando resposta..."):
                prompt_com_contexto = montar_prompt_com_contexto(vector_writer, user_prompt, k=k)
                resposta = call_llm(llm, prompt_com_contexto, max_tokens=max_tokens)
                st.markdown("### 💡 Resposta:")
                st.write(resposta)
        else:
            st.warning("Digite uma pergunta primeiro.")


