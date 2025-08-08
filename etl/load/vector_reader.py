from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typing import List, Tuple, Optional
from langchain_core.documents import Document
import warnings
import numpy as np

warnings.filterwarnings("ignore", message="`add_prefix_space` was not set")
warnings.filterwarnings("ignore", message="`clean_up_tokenization_spaces` was not set")

def initialize_embeddings(
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
) -> HuggingFaceEmbeddings:
    """
    Inicializa o objeto HuggingFaceEmbeddings.
    """
    return HuggingFaceEmbeddings(model_name=model_name)

def load_vectorstore(
    persist_directory: str,
    embeddings: HuggingFaceEmbeddings
) -> Chroma:
    """
    Carrega o vectorstore Chroma com o objeto embeddings.
    """
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)


class EmbeddingSearcher:
    """
    Classe para gerenciar embeddings, vectorstore e consultas.
    """

    def __init__(
        self,
        persist_directory: str = "./data/output/embeddings",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        self.embeddings = initialize_embeddings(model_name)
        self.vectorstore = load_vectorstore(persist_directory, self.embeddings)

    def query(self, query_text: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query_text, k=k)

    def load_embeddings_and_labels(
        self, label_key: Optional[str] = None, limit: int = 100
    ) -> Tuple[np.ndarray, List]:
        """
        Recupera embeddings e labels do vectorstore para validação.
        """
        data = self.vectorstore._collection.get(include=["metadatas", "documents", "embeddings"], ids=None)

        total = len(data['ids'])
        n = min(limit, total)

        embeddings_list = data['embeddings'][:n]
        embeddings_array = np.array(embeddings_list)

        if label_key:
            labels_list = [meta.get(label_key, None) for meta in data['metadatas'][:n]]
        else:
            labels_list = [None] * n

        return embeddings_array, labels_list
