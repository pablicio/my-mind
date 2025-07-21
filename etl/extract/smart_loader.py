# etl/extract/smart_loader.py
import os
from typing import List
from PyPDF2 import PdfReader
from utils.directory import sanitize_filename
from etl.extract.ocr_files import read_text_from_image, create_easyocr_reader, save_text_output, convert_pdf_to_text
from pathlib import Path

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

def load_document(filepath):

    files = collect_files(filepath, extensions=[".pdf", ".jpg", ".png", ".md"])
    output_dir = r"C:\projetos\IA\my-mind\data\output"

    for filepath in files:
        if sanitize_filename(filepath).endswith(".pdf"):
            if is_scanned_pdf(filepath):
                # Converte PDF em imagens e aplica OCR
                convert_pdf_to_text(filepath, output_dir)
            else:
                # Usa LangChain PyPDFLoader
                # return load_with_langchain(filepath)
                print("Ler com langhain", filepath)
        elif filepath.endswith((".png", ".jpg")):
            reader = create_easyocr_reader(['pt', 'en'])
            texto = read_text_from_image(filepath, reader, output_dir)
            if texto:
                # Salva o texto extraído
                print(f"[INFO] Salvando OCR de imagem: {filepath}")
                save_text_output(texto, filepath, Path(output_dir))

        elif filepath.endswith((".txt", ".md", ".docx")):
            print("Ler com langhain", filepath)
        else:
            raise NotImplementedError("Formato ainda não suportado.")
