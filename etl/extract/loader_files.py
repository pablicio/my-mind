from pathlib import Path
from langchain_community.document_loaders import TextLoader
from etl.extract.ocr_files import save_text_output

def load_text_with_loader(file_path, ext, supported_extensions, output_dir=None):
    """
    Carrega texto usando o loader apropriado baseado na extensão do arquivo.
    Se o arquivo .md já existir no output_dir, retorna o texto salvo e ignora o loader.

    Args:
        file_path (str or Path): Caminho do arquivo original.
        ext (str): Extensão do arquivo (ex: ".pdf").
        supported_extensions (dict): Mapeamento de extensões para classes loader.
        output_dir (Path or str, optional): Diretório para salvar ou buscar o .md cache.

    Returns:
        str: Texto extraído (do cache ou novo).
    """
    file_path = Path(file_path)

    if output_dir:
        output_dir = Path(output_dir)
        cached_file = output_dir / f"{file_path.stem}_ocr.md"

        if cached_file.exists():
            print(f"[SKIP] Já processado: {file_path.name}")
            return cached_file.read_text(encoding="utf-8")

    loader_class = supported_extensions.get(ext)
    if not loader_class:
        raise NotImplementedError(f"Loader não disponível para extensão '{ext}'")

    print(f"[Loader] Iniciando carregamento: {file_path.name}")
    docs = loader_class(file_path).load()
    text = ''.join(doc.page_content for doc in docs)
    safe_text = text.encode("utf-8", errors="ignore").decode("utf-8")

    if output_dir:
        output_file = save_text_output(safe_text, file_path, output_dir)
        print(f"[Loader] Texto salvo em: {output_file}")
        return output_file.read_text(encoding="utf-8")

    print(f"[Loader] {ext.upper()} carregado (sem salvar)")
    return safe_text

def load_non_pdf_text(file_path: str, loader_class, output_dir: Path = None) -> str:
    """
    Carrega arquivos estruturados não-PDF com o loader apropriado.
    Se o arquivo .md já existir no output_dir, retorna o texto salvo e ignora o loader.

    Args:
        file_path (str): Caminho do arquivo original.
        loader_class: Classe loader para o tipo de arquivo (ex: TextLoader, CSVLoader).
        output_dir (Path, optional): Diretório para salvar ou buscar o .md cache.

    Returns:
        str: Texto extraído (do cache ou novo).
    """
    file_path = Path(file_path)

    if output_dir:
        output_dir = Path(output_dir)
        cached_file = output_dir / f"{file_path.stem}_ocr.md"

        if cached_file.exists():
            print(f"[SKIP] Já processado: {file_path.name}")
            return cached_file.read_text(encoding="utf-8")

    print(f"[Loader] Texto estruturado: {file_path.name}")

    # Para TextLoader, especifica encoding para evitar erros comuns
    if loader_class == TextLoader:
        loader = loader_class(str(file_path), encoding="utf-8")
    else:
        loader = loader_class(str(file_path))

    docs = loader.load()
    text = ''.join(doc.page_content for doc in docs)
    safe_text = text.encode("utf-8", errors="ignore").decode("utf-8")

    if output_dir:
        output_file = save_text_output(safe_text, file_path, output_dir)
        print(f"[Loader] Texto salvo em: {output_file}")
        return output_file.read_text(encoding="utf-8")

    print(f"[Loader] {file_path.suffix.upper()} carregado (sem salvar)")
    return safe_text
