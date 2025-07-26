import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SEPARATORS = ["\n### ", "\n## ", "\n# ", "\n\n", ". ", " "]

def process_markdown_file(file_path, base_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS
    )

    chunks = splitter.split_text(text)
    rel_path = os.path.relpath(file_path, base_dir)
    filename = os.path.basename(file_path)

    chunk_dicts = []
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "content": chunk.strip(),
            "metadata": {
                "source_file": filename,
                "relative_path": rel_path,
                "chunk_index": i
            }
        }
        chunk_dicts.append(chunk_data)

    return chunk_dicts

def load_processed_files(output_jsonl):
    processed_files = set()
    if os.path.exists(output_jsonl):
        with open(output_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    source_file = data.get("metadata", {}).get("relative_path")
                    if source_file:
                        processed_files.add(source_file)
                except json.JSONDecodeError:
                    continue
    return processed_files

def chunk_markdown_folder(input_folder, output_jsonl="chunks_output.jsonl"):
    processed_files = load_processed_files(output_jsonl)
    all_chunks = []

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, input_folder)
                if rel_path in processed_files:
                    print(f"Ignorando já processado: {rel_path}")
                    continue
                print(f"Processando: {file_path}")
                chunks = process_markdown_file(file_path, input_folder)
                all_chunks.extend(chunks)

    # Append os novos chunks ao arquivo jsonl
    with open(output_jsonl, 'a', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')

    print(f"\n✅ {len(all_chunks)} chunks novos salvos em: {output_jsonl}")

