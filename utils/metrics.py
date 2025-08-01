
from typing import List, Dict
import random

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