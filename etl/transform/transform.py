from etl.transform.text_cleaner import process_markdown_folder
from etl.transform.text_splitter import chunk_markdown_folder

def run_transformation(input_folder: str, output_clean: str, output_chunks: str):
    print("\n🟢 Iniciando transformação (limpeza e chunking)...")
    process_markdown_folder(input_folder, output_clean)
    chunk_markdown_folder(output_clean, output_chunks)