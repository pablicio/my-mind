import os
import re
from langdetect import detect


MIN_WORDS = 40  # mínimo de palavras para considerar o arquivo relevante


def detect_lang(text):
    try:
        return detect(text)
    except:
        return "unknown"

def clean_markdown_text(text: str) -> str:
    text = re.sub(r'```[\s\S]*?```', '', text)                      # remove blocos de código
    text = re.sub(r'`[^`]*`', '', text)                             # remove inline code
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)                     # remove imagens
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)              # remove links, mantém texto
    text = re.sub(r'^\s{0,3}#{1,6}\s*', '', text, flags=re.MULTILINE)  # remove cabeçalhos
    text = re.sub(r'^\s*([-*+]|\d+\.)\s+', '', text, flags=re.MULTILINE)  # remove listas
    text = re.sub(r'^\s*>+\s?', '', text, flags=re.MULTILINE)       # remove citações
    text = re.sub(r'<[^>]+>', '', text)                             # remove links soltos entre <>
    text = re.sub(r'\n{3,}', '\n\n', text)                          # remove linhas em branco extras
    text = re.sub(r'[ \t]+', ' ', text)                             # remove espaços em excesso
    text = '\n'.join(line.strip() for line in text.splitlines())   # remove espaços em cada linha
    text = re.sub(r'[^\w\s.,;:!?@%&()\-–—"\'´`~^°\[\]{}<>áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ€$\\\/|]+', '', text)

    return text.strip()

def process_markdown_folder(input_folder: str, output_folder: str):
    for root, _, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        dest_dir = os.path.join(output_folder, rel_path)
        os.makedirs(dest_dir, exist_ok=True)

        for filename in files:
            if filename.lower().endswith('.md'):
                input_path = os.path.join(root, filename)
                output_path = os.path.join(dest_dir, filename)

                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    cleaned = clean_markdown_text(content)
                    lang = detect_lang(cleaned)

                    if lang == "en":
                        print(f'Ignorado (inglês): {input_path}')
                        continue

                    if len(cleaned.split()) < MIN_WORDS:
                        print(f'Descartado (pouco conteúdo): {input_path}')
                        continue

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)

                    print(f'Processado: {input_path} -> {output_path}')

                except Exception as e:
                    print(f'Erro ao processar {input_path}: {e}')