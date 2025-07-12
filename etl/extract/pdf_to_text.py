# file: pdf_ocr_utils.py

import os
import re
import time
import shutil
from pathlib import Path
from pdf2image import convert_from_path
import easyocr

from utils.directory import construct_folder_path, get_desktop_folder

def remove_file_with_retry(file_path, retries=5, delay=1):
    """Tenta remover um arquivo, mesmo se ele estiver temporariamente bloqueado pelo sistema."""
    for attempt in range(retries):
        try:
            os.remove(file_path)
            print(f"Successfully deleted: {file_path}")
            return True
        except PermissionError:
            print(f"PermissionError: {file_path} is in use. Retrying in {delay}s...")
            time.sleep(delay)
    print(f"Failed to delete: {file_path} after {retries} attempts.")
    return False

def remove_directory_with_retry(directory_path, retries=5, delay=1):
    """Tenta remover uma pasta com todos os arquivos, mesmo que estejam temporariamente bloqueados."""
    for attempt in range(retries):
        try:
            shutil.rmtree(directory_path, onerror=remove_error)
            print(f"Successfully deleted directory: {directory_path}")
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    print(f"Failed to delete directory: {directory_path} after {retries} attempts.")
    return False

def remove_error(func, path, exc_info):
    """Handler de erro para rmtree: tenta remover arquivos travados."""
    if func == os.unlink:
        remove_file_with_retry(path)
    elif func == os.rmdir:
        print(f"Directory still in use, cannot delete: {path}")

def convert_PDF_to_text(reader, image_path):
    """
    Converte PDF em imagens, aplica OCR (EasyOCR), retorna texto extraído.
    Args:
        reader: Instância de easyocr.Reader
        image_path: Caminho do PDF
    Returns:
        Texto extraído de todas as páginas.
    """
    desktop_folder = get_desktop_folder()
    image_folder = construct_folder_path(desktop_folder, "PDF_IMAGES")

    images = convert_from_path(image_path)
    image_files = []

    for i, image in enumerate(images):
        image_file = f"{image_folder}/page_{i}.png"
        image.save(image_file, "PNG")
        image_files.append(image_file)

    all_texts = []

    for image_file in image_files:
        ocr_result = reader.readtext(image_file)

        words = []
        for count, result in enumerate(ocr_result):
            bbox, word, confidence = result
            if count < 3:
                print(f"OCR sample: {result}")
            words.append(word)

        text = " ".join(words)
        all_texts.append(text)

    remove_directory_with_retry(image_folder)
    return " ".join(all_texts)
