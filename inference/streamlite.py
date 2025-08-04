import streamlit as st
import warnings
from inference.rag_pipeline import RagPipeline

warnings.filterwarnings("ignore", message=".*was not set")

# 1. Função cacheada para carregar o RagPipeline
@st.cache_resource
def load_rag_pipeline():
    return RagPipeline(persist_directory="./data/output/embeddings")

# 2. Função principal do app
def chat_app():
    st.set_page_config(page_title="RAG com LLaMA", page_icon="🧠")
    st.title("🧠 My Mind")

    # Carrega pipeline RAG
    rag = load_rag_pipeline()

    user_prompt = st.text_area("Digite sua pergunta:", height=150)

    col1, col2 = st.columns(2)
    with col1:
        k = st.slider("Docs de contexto (top-k)", 1, 10, 5)
    with col2:
        max_tokens = st.slider("Máx. Tokens", 100, 1024, 512)

    if st.button("Responder"):
        if user_prompt.strip():
            with st.spinner("Buscando contexto e gerando resposta..."):
                resposta = rag.generate_answer(user_prompt, k=k, max_tokens=max_tokens)
                st.markdown("### 💡 Resposta:")
                st.write(resposta)
        else:
            st.warning("Digite uma pergunta primeiro.")

# 3. Executa o app
if __name__ == "__main__":
    chat_app()
