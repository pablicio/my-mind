from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import warnings

warnings.filterwarnings("ignore", message="`add_prefix_space` was not set")
warnings.filterwarnings("ignore", message="`clean_up_tokenization_spaces` was not set")

# Inicializa embeddings e carrega base existente
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = Chroma(persist_directory="./data/output/embeddings", embedding_function=embeddings)

def query(query_text: str, k: int = 5) -> List[Document]:
    return vectorstore.similarity_search(query_text, k=k)

# Consulta: busca os 5 documentos mais similares à query
query_text = "Como ler livros de fomra eficiente?"
results = query(query_text, k=5)

for doc in results:
    print(f"Texto: {doc.page_content}")
    print(f"Metadados: {doc.metadata}")
    print("-" * 40)
