import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configurações para dividir o texto em chunks:
CHUNK_SIZE = 800         # tamanho máximo de cada chunk em caracteres
CHUNK_OVERLAP = 100      # sobreposição entre chunks para manter contexto
SEPARATORS = ["\n### ", "\n## ", "\n# ", "\n\n", ". ", " "]  # separadores usados para divisão

def process_markdown_file(file_path, base_dir):
    """
    Processa um arquivo Markdown:
    - Lê o conteúdo do arquivo.
    - Divide o texto em chunks utilizando RecursiveCharacterTextSplitter da LangChain,
      que respeita separadores hierárquicos para cortes naturais.
    - Para cada chunk, cria um dicionário com o conteúdo e metadados (nome do arquivo,
      caminho relativo e índice do chunk).
    Retorna a lista de dicionários de chunks.
    
    Parâmetros:
    - file_path: caminho completo do arquivo markdown.
    - base_dir: diretório base para cálculo do caminho relativo.
    """
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
    """
    Carrega os arquivos já processados lendo um arquivo JSONL de chunks previamente
    salvos. Isso serve para evitar reprocessar arquivos que já tiveram seus chunks
    gerados.

    Retorna um conjunto com os caminhos relativos dos arquivos já processados.
    
    Parâmetro:
    - output_jsonl: caminho do arquivo JSONL que armazena os chunks processados.
    """
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
                    # Ignora linhas mal formatadas
                    continue
    return processed_files

def chunk_markdown_folder(input_folder, output_jsonl="chunks_output.jsonl"):
    """
    Processa todos os arquivos Markdown dentro da pasta 'input_folder' (recursivamente).
    Para cada arquivo .md que ainda não foi processado:
    - Gera chunks usando process_markdown_file.
    - Acumula os chunks para depois salvá-los no arquivo JSONL.
    - Atualiza o arquivo JSONL com os novos chunks, sem sobrescrever os anteriores.
    Exibe mensagens no console indicando os arquivos processados ou ignorados.

    Parâmetros:
    - input_folder: pasta raiz com arquivos Markdown a serem processados.
    - output_jsonl: arquivo JSONL onde os chunks serão salvos (padrão: "chunks_output.jsonl").
    """
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

    # Append os novos chunks ao arquivo jsonl, mantendo os anteriores
    with open(output_jsonl, 'a', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')

    print(f"\n✅ {len(all_chunks)} chunks novos salvos em: {output_jsonl}")
