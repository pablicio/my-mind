from typing import List, Dict
import json
import warnings
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

warnings.filterwarnings("ignore", message="`add_prefix_space` was not set")
warnings.filterwarnings("ignore", message="`clean_up_tokenization_spaces` was not set")

class VectorWriter:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def _get_existing_contents(self) -> set:
        """Obtém conteúdos já persistidos para evitar duplicatas."""
        existing_docs = self.vectorstore.get(include=["documents"])
        return set(existing_docs["documents"]) if existing_docs else set()

    def add_chunks(self, chunks: List[Dict], batch_size: int = 500):
        existing_contents = self._get_existing_contents()
        print(f"[DEBUG] Conteúdos existentes na base: {len(existing_contents)}")

        new_chunks = [chunk for chunk in chunks if chunk["content"] not in existing_contents]
        print(f"[DEBUG] Novos chunks a adicionar: {len(new_chunks)}")

        total_new = len(new_chunks)
        total_batches = (total_new + batch_size - 1) // batch_size

        for i in range(0, total_new, batch_size):
            batch = new_chunks[i:i+batch_size]
            texts = [chunk["content"] for chunk in batch]
            metadatas = [chunk.get("metadata", {}) for chunk in batch]
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            print(f"[VectorWriter] Batch {i // batch_size + 1}/{total_batches} processado com {len(batch)} chunks.")

        print(f"[VectorWriter] Total de {total_new} chunks novos adicionados.")

    def query(self, query_text: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query_text, k=k)

    def query_with_score(self, query_text: str, k: int = 5):
        return self.vectorstore.similarity_search_with_score(query_text, k=k)
    
    def load_and_add_chunks(self, json_path: str, max_chunks: int = None):
        """
        Lê um arquivo JSONL de chunks, carrega até `max_chunks` entradas (ou todas se None)
        e adiciona ao vetor.
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {json_path}")

        chunks = []
        with open(json_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if max_chunks is not None and i >= max_chunks:
                    break
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))

        self.add_chunks(chunks)
        return chunks