from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import warnings

warnings.filterwarnings("ignore", message="`add_prefix_space` was not set")
warnings.filterwarnings("ignore", message="`clean_up_tokenization_spaces` was not set")

# Inicializa embeddings e carrega base existente
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Consulta: busca os 5 documentos mais similares à query
query_text = "Como investir em ações?"
results = vectorstore.similarity_search(query_text, k=5)

for doc in results:
    print(f"Texto: {doc.page_content}")
    print(f"Metadados: {doc.metadata}")
    print("-" * 40)
