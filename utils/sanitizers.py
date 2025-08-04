from typing import List

def format_chunks_for_prompt(chunks: List[str]) -> str:
    """
    Recebe uma lista de trechos de texto e os concatena em uma única string,
    separando-os por linhas com delimitadores para facilitar a leitura pelo modelo.

    Exemplo de saída:
    ---
    Chunk 1 texto...

    ---

    Chunk 2 texto...

    ---
    """
    separator = "\n---\n"
    formatted_text = separator.join(chunks)
    return formatted_text
