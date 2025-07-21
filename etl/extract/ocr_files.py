from pathlib import Path
import numpy as np
import easyocr
from pdf2image import convert_from_path
import torch
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def has_gpu() -> bool:
    """Retorna True se GPU CUDA estiver disponível, caso contrário False."""
    return torch.cuda.is_available()

def create_easyocr_reader(langs=['pt', 'en'], force_cpu=False) -> easyocr.Reader:
    """Cria uma instância do leitor EasyOCR com fallback para CPU."""
    use_gpu = has_gpu() and not force_cpu
    logging.info(f"Instanciando EasyOCR (GPU={use_gpu})...")
    return easyocr.Reader(langs, gpu=use_gpu)


def read_text_from_image(image_input, reader: easyocr.Reader, output_dir: Path = None) -> str:
    """
    Executa OCR em uma imagem e salva/recupera resultado se output_dir for fornecido.

    Args:
        image_input: caminho da imagem (str ou Path) ou array numpy da imagem.
        reader: instância easyocr.Reader.
        output_dir: Pasta onde salvar texto OCR (opcional).

    Returns:
        str: Texto extraído da imagem.
    """
    image_path = None
    if isinstance(image_input, (str, Path)):
        image_path = Path(image_input)
        img_np = np.array(Image.open(str(image_path)))
    else:
        img_np = image_input

    if output_dir and image_path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{image_path.stem}_ocr.txt"
        if output_file.exists():
            msg = f"[SKIP] OCR já existe: {output_file.name}"
            print(msg)
            logging.info(msg)
            return output_file.read_text(encoding='utf-8')

    results = reader.readtext(img_np)
    words = [word for _, word, _ in results]
    text = " ".join(words)

    if output_dir and image_path:
        output_file.write_text(text, encoding='utf-8')
        logging.info(f"[OK] OCR salvo: {output_file.name}")

    return text

def save_text_output(text: str, source_path, output_dir: Path) -> Path:
    """
    Salva o texto extraído em um arquivo .txt nomeado a partir do arquivo original.

    Args:
        text: Texto a ser salvo.
        source_path: Caminho original do arquivo de entrada (str ou Path).
        output_dir: Diretório onde salvar o arquivo de saída.

    Returns:
        Path: Caminho para o arquivo salvo.
    """
    source_path = Path(source_path)  # <- Corrige o erro
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{source_path.stem}_ocr.txt"
    output_file.write_text(text, encoding='utf-8')
    logging.info(f"[OK] Texto salvo em: {output_file}")
    return output_file


def convert_pdf_to_text(pdf_path: str, output_dir: str, langs=['pt', 'en']) -> str:
    """
    Converte um PDF em imagens, aplica OCR e salva texto extraído.

    Args:
        pdf_path: Caminho do PDF.
        output_dir: Pasta onde salvar o texto final.
        langs: Idiomas usados no OCR.

    Returns:
        Texto extraído do PDF.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_file = output_dir / f"{pdf_path.stem}_ocr.txt"

    if output_file.exists():
        logging.info(f"OCR já realizado. Pulando: {output_file.name}")
        return output_file.read_text(encoding='utf-8')

    reader = create_easyocr_reader(langs)
    logging.info(f"Convertendo PDF em imagens (dpi=150)...")
    images = convert_from_path(str(pdf_path), dpi=150)

    logging.info(f"Executando OCR em {len(images)} páginas...")
    all_texts = []

    for i, image in enumerate(images, 1):
        logging.info(f"Pág {i}/{len(images)}")
        try:
            text = read_text_from_image(np.array(image), reader)
        except RuntimeError as e:
            logging.error(f"Erro na página {i}: {e}")
            logging.info("Tentando fallback para CPU...")
            reader = create_easyocr_reader(langs, force_cpu=True)
            text = read_text_from_image(np.array(image), reader)
        all_texts.append(text)

    full_text = "\n\n".join(all_texts)
    return save_text_output(full_text, pdf_path, output_dir).read_text(encoding='utf-8')
