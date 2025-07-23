# etl/extract/smart_loader.py
import os
from typing import List
from PyPDF2 import PdfReader
from etl.extract.ocr_files import read_text_from_image, convert_pdf_to_text
from etl.extract.loader_files import load_text_with_loader

from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredEPubLoader
)

def collect_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Coleta todos os arquivos de uma pasta (recursivamente), opcionalmente filtrando por extensões.

    Args:
        directory (str): Caminho da pasta raiz.
        extensions (List[str], optional): Lista de extensões desejadas, ex: ['.pdf', '.png'].

    Returns:
        List[str]: Lista de caminhos completos dos arquivos encontrados.
    """
    file_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
            if extensions is None or os.path.splitext(file)[1].lower() in extensions:
                file_paths.append(os.path.join(root, file))

    return file_paths

def is_scanned_pdf(filepath: str, max_pages: int = 3) -> bool:
    """
    Verifica se um PDF contém texto selecionável.
    
    Args:
        filepath (str): Caminho do arquivo PDF.
        max_pages (int): Número máximo de páginas a verificar.

    Returns:
        bool: True se o PDF parece ser escaneado (sem texto), False se contém texto embutido.
    """
    try:
        reader = PdfReader(filepath, strict=False)
        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break
            text = page.extract_text()
            if text and text.strip():  # Texto não vazio
                return False  # Contém texto

        return True  # Nenhuma página com texto

    except Exception as e:
        print(f"[ERRO] Falha ao ler PDF '{filepath}': {e}")
        return True  # Por segurança, assume que precisa de OCR

def load_document(filepath, output_dir=r"C:\projetos\IA\my-mind\data\output"):
    """
    Carrega e processa documentos de diferentes formatos:
    - PDFs escaneados são processados com OCR
    - PDFs normais e outros formatos são delegados a loaders apropriados
    - Imagens recebem OCR direto
    """
    
    supported_extensions = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".epub": UnstructuredEPubLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader,
    }

    files = collect_files(filepath, extensions=[".pdf", ".jpg", ".png", ".txt", ".docx"])

    for file in files:
        ext = Path(file).suffix.lower()

        if ext == ".pdf":
            if is_scanned_pdf(file):
                convert_pdf_to_text(file, output_dir)  # OCR para PDFs escaneados
            else:
                load_text_with_loader(file, ext, supported_extensions, output_dir)

        elif ext in [".png", ".jpg"]:
            read_text_from_image(file, output_dir)

        elif ext in supported_extensions:
            print(f"[Loader] Texto estruturado: {file}")
            loader = supported_extensions[ext]
            loader(file).load()

        else:
            raise NotImplementedError(f"Formato ainda não suportado: {ext}")
        
        
