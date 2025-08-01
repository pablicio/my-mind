from typing import List, Dict
import json
import random
import warnings

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
    
    @staticmethod
    def calculate_metrics_at_k(vw, chunks: List[Dict], k: int = 5, sample_size: int = 5000):
        """
        Calcula Precision@k, Recall@k e F1@k para uma lista de chunks.
        Se houver mais que sample_size chunks, amostra aleatoriamente sample_size deles.
        
        vw: seu objeto VectorWriter com método query_with_score
        chunks: lista de dicts com 'content' e 'metadata'
        k: top-k para avaliação
        sample_size: número máximo de chunks para avaliar (amostra aleatória se exceder)
        """
        total_original = len(chunks)
        
        if total_original > sample_size:
            chunks = random.sample(chunks, sample_size)
            print(f"Avaliando uma amostra aleatória de {sample_size} chunks (de {total_original} totais).")
        else:
            print(f"Avaliando todos os {total_original} chunks.")

        total = len(chunks)
        hits = 0  # quantos queries acertaram recuperar o doc esperado no top-k

        for i, chunk in enumerate(chunks):
            query_text = chunk["content"]
            meta = chunk.get("metadata", {})
            expected_id = f"{meta.get('source_file', '')}_{meta.get('chunk_index', '')}"

            results_with_score = vw.query_with_score(query_text, k=k)

            # ids recuperados nos top-k
            retrieved_ids = [
                doc.metadata.get("doc_id", f"{doc.metadata.get('source_file','')}_{doc.metadata.get('chunk_index','')}")
                for doc, _ in results_with_score
            ]

            if expected_id in retrieved_ids:
                hits += 1

            print(f"Query {i+1}/{total}: {'Hit' if expected_id in retrieved_ids else 'Miss'}")

        precision_at_k = hits / total if total > 0 else 0
        recall_at_k = hits / total if total > 0 else 0  # aqui recall = precision pois é 1 item esperado por consulta
        f1_at_k = (2 * precision_at_k * recall_at_k) / (precision_at_k + recall_at_k) if (precision_at_k + recall_at_k) > 0 else 0

        print("\n--- Métricas @", k, "---")
        print(f"Precision@{k}: {precision_at_k:.2%}")
        print(f"Recall@{k}: {recall_at_k:.2%}")
        print(f"F1@{k}: {f1_at_k:.2%}")

        return precision_at_k, recall_at_k, f1_at_k

if __name__ == "__main__":
    json_path = "./data/output/chunks/chunks_output.json"

    chunks = []
    max_chunks = 90000
    with open(json_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_chunks:
                break
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    vw = VectorWriter()
    vw.add_chunks(chunks)
    VectorWriter.calculate_metrics_at_k(vw, chunks, k=5, sample_size=5000)