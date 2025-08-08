from etl.load.vector_reader import EmbeddingSearcher
from etl.load.vector_writer import VectorWriter
from utils.metrics import calculate_embedding_metrics, calculate_chunk_metrics

def run_embedding_metrics(
    label_key: str = "source_file",
    limit: int = 100,
    persist_directory: str = "./data/output/embeddings/",
    verbose: bool = True,
):
    print("\n🟢 Avaliando métricas de embeddings...")
    searcher = EmbeddingSearcher(persist_directory=persist_directory)
    embeddings, labels = searcher.load_embeddings_and_labels(label_key=label_key, limit=limit)
    calculate_embedding_metrics(embeddings, labels, verbose=verbose)

def run_chunk_metrics(
    chunk_json_path: str = "./data/output/chunks/chunks_output.json",
    persist_directory: str = "./data/output/embeddings/",
    k: int = 5,
    sample_size: int = 100,
    verbose: bool = True,
):
    print("\n🟢 Avaliando métricas de chunks...")
    vw = VectorWriter(persist_directory=persist_directory)
    chunks = vw.load_and_add_chunks(json_path=chunk_json_path)
    calculate_chunk_metrics(vw, chunks, k=k, sample_size=sample_size, verbose=verbose)
