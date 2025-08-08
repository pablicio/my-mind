import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from etl.extract.extract import run_extraction
from etl.load.load import run_embedding_generation
from etl.load.evaluate_load import run_embedding_metrics
from etl.load.evaluate_load import run_chunk_metrics
from etl.transform.transform import run_transformation
from inference.inference import run_inference

# =======================
# Execução Principal
# =======================

if __name__ == '__main__':
    # Paths de entrada
    paths = [
        r"D:\ARQUIVOS",
        r"D:\Workspace\NOTAS\GST"
    ]
    
    # Parâmetros de pasta
    raw_dir = r"data/output"
    clean_dir = r"data/output/clean"
    chunks_path = r"data/output/chunks/chunks_output.json"
    embeddings_dir = r"data/output/embeddings/"

    # ========================
    # EXECUÇÃO DO PIPELINE
    # ========================
    run_extraction(paths)
    run_transformation(raw_dir, clean_dir, chunks_path)
    run_embedding_generation(chunks_path, embeddings_dir)
    run_chunk_metrics(chunk_json_path=chunks_path, persist_directory=embeddings_dir, k=5, sample_size=500)
    run_embedding_metrics(label_key="source_file", limit=100)
    run_inference(mode="cli")
