import os
import re
from langdetect import detect

# Define o número mínimo de palavras para considerar um arquivo relevante para processamento
MIN_WORDS = 40  # mínimo de palavras para considerar o arquivo relevante

def detect_lang(text):
    """
    Detecta o idioma do texto usando a biblioteca langdetect.
    Retorna a sigla do idioma detectado (ex: 'en', 'pt', 'fr').
    Se ocorrer qualquer erro na detecção, retorna 'unknown'.
    """
    try:
        return detect(text)
    except:
        return "unknown"

def clean_markdown_text(text: str) -> str:
    """
    Limpa o texto Markdown removendo elementos que não são texto corrido, tais como:
    - blocos de código (```...```)
    - código inline (`...`)
    - imagens (![alt](url))
    - links mantendo apenas o texto (ex: [texto](url) -> texto)
    - cabeçalhos Markdown (#, ##, etc)
    - listas (itens iniciados por -, *, + ou números)
    - citações (linhas começando com >)
    - tags HTML ou links soltos entre <>
    - linhas em branco extras
    - espaços e tabulações em excesso
    Também remove caracteres não alfanuméricos comuns, preservando pontuação e caracteres acentuados usados no português.
    
    Retorna o texto limpo e normalizado.
    """
    text = re.sub(r'```[\s\S]*?```', '', text)                      # remove blocos de código
    text = re.sub(r'`[^`]*`', '', text)                             # remove inline code
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)                     # remove imagens
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)              # remove links, mantém texto
    text = re.sub(r'^\s{0,3}#{1,6}\s*', '', text, flags=re.MULTILINE)  # remove cabeçalhos
    text = re.sub(r'^\s*([-*+]|\d+\.)\s+', '', text, flags=re.MULTILINE)  # remove listas
    text = re.sub(r'^\s*>+\s?', '', text, flags=re.MULTILINE)       # remove citações
    text = re.sub(r'<[^>]+>', '', text)                             # remove tags HTML ou links soltos entre <>
    text = re.sub(r'\n{3,}', '\n\n', text)                          # remove linhas em branco extras
    text = re.sub(r'[ \t]+', ' ', text)                             # remove espaços em excesso
    text = '\n'.join(line.strip() for line in text.splitlines())   # remove espaços em cada linha
    text = re.sub(r'[^\w\s.,;:!?@%&()\-–—"\'´`~^°\[\]{}<>áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ€$\\\/|]+', '', text)

    return text.strip()

def process_markdown_folder(input_folder: str, output_folder: str):
    """
    Percorre recursivamente a pasta 'input_folder' buscando arquivos com extensão .md.
    Para cada arquivo Markdown:
    - Lê seu conteúdo
    - Limpa o texto com 'clean_markdown_text'
    - Detecta o idioma do texto limpo com 'detect_lang'
    - Ignora arquivos em inglês (lang == 'en')
    - Ignora arquivos com menos de MIN_WORDS palavras
    - Salva o texto limpo na mesma estrutura de pastas dentro de 'output_folder'
    - Exibe no console mensagens informando se o arquivo foi processado, ignorado ou descartado
    """
    for root, _, files in os.walk(input_folder):
        # calcula o caminho relativo da pasta atual para replicar a estrutura
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

                    # Ignora arquivos em inglês
                    if lang == "en":
                        print(f'Ignorado (inglês): {input_path}')
                        continue

                    # Ignora arquivos com pouco conteúdo (menos que MIN_WORDS)
                    if len(cleaned.split()) < MIN_WORDS:
                        print(f'Descartado (pouco conteúdo): {input_path}')
                        continue

                    # Salva arquivo limpo na pasta de destino
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)

                    print(f'Processado: {input_path} -> {output_path}')

                except Exception as e:
                    print(f'Erro ao processar {input_path}: {e}')
