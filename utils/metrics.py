from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from sklearn.neighbors import NearestNeighbors
import random

def evaluate_hits(
    vw,
    chunks: List[Dict],
    k: int
) -> Tuple[int, List[str]]:
    """
    Realiza consultas no vector store e contabiliza hits.

    Args:
        vw: objeto vector store com método query_with_score(query, k)
        chunks: lista de chunks com 'content' e 'metadata'
        k: número de documentos top-k para recuperar

    Returns:
        hits: número de queries com documento esperado recuperado
        logs: lista de mensagens para debug
    """
    hits = 0
    logs = []

    for i, chunk in enumerate(chunks, 1):
        query_text = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        expected_id = f"{metadata.get('source_file', '')}_{metadata.get('chunk_index', '')}"

        try:
            results = vw.query_with_score(query_text, k=k)
        except Exception as e:
            logs.append(f"[Erro] Consulta {i} falhou: {e}")
            continue

        retrieved_ids = [
            doc.metadata.get("doc_id") or f"{doc.metadata.get('source_file', '')}_{doc.metadata.get('chunk_index', '')}"
            for doc, _ in results
        ]

        if expected_id in retrieved_ids:
            hits += 1
            status = "✔ HIT"
        else:
            status = "✘ MISS"

        logs.append(f"[{i}/{len(chunks)}] {status} - Esperado: {expected_id}")

    return hits, logs

def calculate_chunk_metrics(
    vw,
    chunks: List[Dict],
    k: int = 5,
    sample_size: Optional[int] = 5000,
    verbose: bool = True,
) -> Tuple[float, float, float]:
    """
    Calcula Precision@k, Recall@k e F1@k para chunks.

    Args:
        vw: vector store com método query_with_score(query, k)
        chunks: lista de chunks com 'content' e 'metadata'
        k: top-k documentos para recuperar
        sample_size: tamanho máximo da amostra para avaliação
        verbose: imprime logs detalhados

    Returns:
        precision, recall, f1
    """
    total_chunks = len(chunks)
    if sample_size and total_chunks > sample_size:
        chunks = random.sample(chunks, sample_size)
        if verbose:
            print(f"Avaliando amostra aleatória de {sample_size} chunks (de {total_chunks})")
    else:
        if verbose:
            print(f"Avaliando todos os {total_chunks} chunks")

    hits, logs = evaluate_hits(vw, chunks, k)

    if verbose:
        for log in logs:
            print(log)

    precision = precision_at_k(hits, len(chunks))
    recall = recall_at_k(hits, len(chunks))
    f1 = f1_score(precision, recall)

    if verbose:
        print(f"\n🎯 Resultados Top-{k}")
        print(f"Precision@{k}: {precision:.2%}")
        print(f"Recall@{k}:    {recall:.2%}")
        print(f"F1@{k}:        {f1:.2%}")

    return precision, recall, f1

def calculate_embedding_metrics(
    embeddings: np.ndarray,
    labels_true: np.ndarray,
    labels_pred: Optional[np.ndarray] = None,
    verbose: bool = True
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Calcula várias métricas para avaliação de embeddings.

    Retorna tuple com:
    - Silhouette Score (float ou None)
    - Nearest Neighbor Accuracy (float ou None)
    - Adjusted Rand Index (float ou None)
    - Normalized Mutual Information (float ou None)
    - Mean Pairwise Cosine Similarity (float)
    - Mean Pairwise Euclidean Distance (float)
    """

    # Silhouette com proteção para poucas classes
    try:
        score_sil = silhouette(embeddings, labels_true)
    except ValueError:
        if verbose:
            print("⚠️ Silhouette Score requer pelo menos 2 classes diferentes. Pulando essa métrica.")
        score_sil = None

    nn_acc = nearest_neighbor_accuracy(embeddings, labels_true)

    ari = None
    nmi = None
    if labels_pred is not None:
        ari = adjusted_rand_index(labels_true, labels_pred)
        nmi = normalized_mutual_info(labels_true, labels_pred)

    # Métricas gerais de similaridade/distância (média dos pares)
    cosine_sim_matrix = pairwise_cosine_similarities(embeddings)
    # só média dos valores acima da diagonal para evitar redundância
    triu_indices = np.triu_indices_from(cosine_sim_matrix, k=1)
    mean_cosine_sim = cosine_sim_matrix[triu_indices].mean()

    # Distâncias euclidianas
    # Para eficiência, calculamos só pares acima da diagonal também
    from scipy.spatial.distance import pdist
    euclid_dists = pdist(embeddings, metric='euclidean')
    mean_euclid_dist = euclid_dists.mean()

    if verbose:
        if score_sil is not None:
            print(f"Silhouette Score: {score_sil:.3f}")
        print(f"Nearest Neighbor Accuracy: {nn_acc:.3f}")
        if ari is not None:
            print(f"Adjusted Rand Index: {ari:.3f}")
        if nmi is not None:
            print(f"Normalized Mutual Information: {nmi:.3f}")
        print(f"Mean Pairwise Cosine Similarity: {mean_cosine_sim:.3f}")
        print(f"Mean Pairwise Euclidean Distance: {mean_euclid_dist:.3f}")

    return score_sil, nn_acc, ari, nmi, mean_cosine_sim, mean_euclid_dist


# ------------------------
# Métricas para Avaliação de Chunks (Recuperação)
# ------------------------

def precision_at_k(hits: int, total: int) -> float:
    """Calcula Precision@k."""
    return hits / total if total > 0 else 0.0

def recall_at_k(hits: int, total: int) -> float:
    """Calcula Recall@k (igual a precision se 1 item relevante por consulta)."""
    return precision_at_k(hits, total)

def f1_score(precision: float, recall: float) -> float:
    """Calcula F1 score a partir de precision e recall."""
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

# ------------------------
# Métricas para Avaliação de Embeddings
# ------------------------

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula similaridade coseno entre dois vetores."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def pairwise_cosine_similarities(embeddings: np.ndarray) -> np.ndarray:
    """Calcula matriz de similaridade coseno entre todos os embeddings."""
    normed = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return np.dot(normed, normed.T)

def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula distância Euclidiana entre dois vetores."""
    return np.linalg.norm(vec1 - vec2)

def silhouette(embeddings: np.ndarray, labels: np.ndarray) -> float:
    """
    Calcula o Silhouette Score para os embeddings com labels verdadeiros.
    
    Requer pelo menos 2 classes diferentes.
    """
    if len(set(labels)) < 2:
        raise ValueError("Silhouette Score requer ao menos 2 classes diferentes")
    return silhouette_score(embeddings, labels)

def nearest_neighbor_accuracy(embeddings: np.ndarray, labels: np.ndarray, n_neighbors: int = 2) -> float:
    """
    Acurácia do vizinho mais próximo (ignorando o próprio ponto).
    Retorna a fração de casos em que o vizinho mais próximo tem mesma label.
    """
    nn = NearestNeighbors(n_neighbors=n_neighbors).fit(embeddings)
    distances, indices = nn.kneighbors(embeddings)

    total = len(labels)
    hits = 0

    for i in range(total):
        # indices[i,0] é o próprio ponto
        for neighbor_idx in indices[i, 1:]:
            if labels[i] == labels[neighbor_idx]:
                hits += 1
                break

    return hits / total

def adjusted_rand_index(labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
    """Calcula Adjusted Rand Index entre labels verdadeiros e previstos."""
    return adjusted_rand_score(labels_true, labels_pred)

def normalized_mutual_info(labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
    """Calcula Normalized Mutual Information entre labels verdadeiros e previstos."""
    return normalized_mutual_info_score(labels_true, labels_pred)
