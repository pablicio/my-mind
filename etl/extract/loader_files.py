from pathlib import Path
from etl.extract.ocr_files import save_text_output

def load_text_with_loader(file_path, ext, supported_extensions, output_dir=None):
    """
    Usa o loader apropriado para carregar texto de um arquivo com extensão conhecida.
    Se o arquivo .md já existir no output_dir, ele é retornado diretamente e o loader é ignorado.

    Args:
        file_path (str or Path): Caminho do arquivo original.
        ext (str): Extensão do arquivo (ex: ".pdf").
        supported_extensions (dict): Mapeamento de extensões para loaders.
        output_dir (Path ou str, opcional): Diretório onde salvar e buscar os arquivos .md.

    Returns:
        str: Conteúdo do texto extraído, lido a partir do .md (cache ou novo).
    """
    file_path = Path(file_path)

    if output_dir:
        output_dir = Path(output_dir)
        cached_file = output_dir / f"{file_path.stem}_ocr.md"

        # Early return com aviso se já existe
        if cached_file.exists():
            print(f"[SKIP] Já processado: {file_path.name}")
            return cached_file.read_text(encoding='utf-8')

    loader_class = supported_extensions.get(ext)
    if not loader_class:
        raise NotImplementedError(f"Loader não disponível para {ext}")

    print(f"[Loader] Iniciando carregamento: {file_path.name}")
    text = ''.join(doc.page_content for doc in loader_class(file_path).load())
    safe_text = text.encode('utf-8', errors='ignore').decode('utf-8')

    if output_dir:
        output_file = save_text_output(safe_text, file_path, output_dir)
        print(f"[Loader] Texto salvo em: {output_file}")
        return output_file.read_text(encoding='utf-8')

    print(f"[Loader] {ext.upper()} carregado (sem salvar): {safe_text}")
    return safe_text



