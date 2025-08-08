from etl.load.vector_writer import VectorWriter

def run_embedding_generation(json_chunks_path: str, embedding_output_dir: str):
    print("\n🟢 Gerando embeddings...")
    vw = VectorWriter(persist_directory=embedding_output_dir)
    vw.load_and_add_chunks(json_path=json_chunks_path)
