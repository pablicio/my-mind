from typing import List, Dict, Tuple
import random

def calculate_metrics_at_k(
    vw,
    chunks: List[Dict],
    k: int = 5,
    sample_size: int = 5000
) -> Tuple[float, float, float]:
    """
    Calculates Precision@k, Recall@k, and F1@k for a list of text chunks.

    Args:
        vw: Vector store object with a method `query_with_score(query_text, k)`
        chunks: List of dicts with 'content' and 'metadata' (including 'source_file' and 'chunk_index')
        k: Number of top documents to consider
        sample_size: Max number of chunks to evaluate; if more, a random sample is used

    Returns:
        Tuple: (precision@k, recall@k, f1@k)
    """

    total_chunks = len(chunks)
    if total_chunks > sample_size:
        chunks = random.sample(chunks, sample_size)
        print(f"Avaliando uma amostra aleatória de {sample_size} chunks (de {total_chunks} totais).")
    else:
        print(f"Avaliando todos os {total_chunks} chunks.")

    hits = 0  # Number of correct retrievals

    for i, chunk in enumerate(chunks, 1):
        query_text = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        expected_id = f"{metadata.get('source_file', '')}_{metadata.get('chunk_index', '')}"

        try:
            results = vw.query_with_score(query_text, k=k)
        except Exception as e:
            print(f"[Erro] Falha na consulta {i}: {e}")
            continue

        retrieved_ids = [
            doc.metadata.get("doc_id") or f"{doc.metadata.get('source_file', '')}_{doc.metadata.get('chunk_index', '')}"
            for doc, _ in results
        ]

        if expected_id in retrieved_ids:
            hits += 1
            result_status = "✔ HIT"
        else:
            result_status = "✘ MISS"

        print(f"[{i}/{len(chunks)}] {result_status} - Esperado: {expected_id}")

    total = len(chunks)
    precision = hits / total if total > 0 else 0.0
    recall = precision  # Para 1 ground truth por consulta
    f1 = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0.0

    print(f"\n🎯 Resultados para Top-{k}")
    print(f"Precision@{k}: {precision:.2%}")
    print(f"Recall@{k}:    {recall:.2%}")
    print(f"F1@{k}:        {f1:.2%}")

    return precision, recall, f1
