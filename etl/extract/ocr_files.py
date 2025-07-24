import numpy as np
import easyocr
import torch
import logging
import time
import fitz
from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def has_gpu() -> bool:
    """Verifica se CUDA GPU está disponível."""
    return torch.cuda.is_available()

def create_easyocr_reader(langs=['pt', 'en'], force_cpu=False) -> easyocr.Reader:
    """
    Cria uma instância do leitor EasyOCR, forçando CPU se solicitado.

    Args:
        langs (list): Lista de idiomas para OCR.
        force_cpu (bool): Se True, força uso da CPU mesmo se GPU disponível.

    Returns:
        easyocr.Reader: Instância configurada do leitor.
    """
    use_gpu = has_gpu() and not force_cpu
    logging.info(f"Instanciando EasyOCR (GPU={use_gpu})...")
    return easyocr.Reader(langs, gpu=use_gpu)

def read_text_from_image(image_input, output_dir: Path = None, image_name=None) -> str:
    """
    Executa OCR em imagem (caminho ou numpy array) e salva resultado (cache simples).

    Args:
        image_input (str|Path|np.ndarray): Caminho da imagem ou array numpy da imagem.
        reader (easyocr.Reader, opcional): Instância EasyOCR já criada. Se None, cria internamente.
        output_dir (Path, opcional): Pasta para salvar o texto OCR.
        image_name (str, opcional): Nome usado para salvar resultado se input for array.

    Returns:
        str: Texto extraído da imagem.
    """
    img_np = None
    image_path = None

    # Detecta tipo da entrada
    if isinstance(image_input, (str, Path)):
        image_path = Path(image_input)
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)
    elif isinstance(image_input, np.ndarray):
        img_np = image_input
        if image_name:
            image_path = Path(image_name)
    else:
        raise ValueError("image_input deve ser caminho (str/Path) ou numpy array")

    # Verifica cache
    if output_dir and image_path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{image_path.stem}_ocr.md"
        if output_file.exists():
            print(f"[SKIP] OCR já existe: {output_file.name}")
            return output_file.read_text(encoding='utf-8')

    # Executa OCR
    logging.info(f"[OCR] Processando: {image_path.name if image_path else 'imagem sem nome'}")

    reader = create_easyocr_reader(['pt', 'en'])
    results = reader.readtext(img_np)

    text = " ".join([word for _, word, _ in results])

    # Salva resultado
    if output_dir and (image_path or image_name):
        save_text_output(
            text,
            image_path if image_path else image_name,
            Path(output_dir)
        )

    return text


def save_text_output(text: str, source_path, output_dir: Path) -> Path:
    """
    Salva texto extraído em arquivo .md com nome baseado no arquivo original.

    Args:
        text (str): Texto a salvar.
        source_path (str|Path): Arquivo origem para nomear saída.
        output_dir (Path): Diretório para salvar arquivo.

    Returns:
        Path: Caminho para o arquivo salvo.
    """
    source_path = Path(source_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{source_path.stem}_ocr.md"
    output_file.write_text(text, encoding='utf-8')
    logging.info(f"[OK] Texto salvo em: {output_file}")
    return output_file

def _ocr_page_bytes(i, image_bytes, langs, force_cpu):
    start = time.perf_counter()
    reader = easyocr.Reader(langs, gpu=not force_cpu)
    png = BytesIO(image_bytes)
    img = Image.open(png).convert("L")
    text = " ".join([w for _, w, _ in reader.readtext(np.array(img))])
    return i, text, time.perf_counter() - start

def convert_pdf_to_text(pdf_path: str, output_dir: str, langs=['pt','en'], force_cpu=False) -> str:
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    out_md = output_dir / f"{pdf_path.stem}_ocr.md"
    if out_md.exists():
        logging.info(f"[SKIP] já existe: {out_md.name}")
        return out_md.read_text(encoding='utf-8')

    doc = fitz.open(str(pdf_path))
    page_texts = []
    ocr_jobs = []

    # 1) extração nativa
    for i, page in enumerate(doc, 1):
        text = page.get_text().strip()
        if text:
            page_texts.append((i, text))
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(1,1), colorspace=fitz.csGRAY)
            ocr_jobs.append((i, pix.tobytes()))

    # 2) OCR apenas nas páginas sem texto
    if ocr_jobs:
        can_gpu = torch.cuda.is_available() and not force_cpu
        max_workers = 2 if can_gpu else min(8, len(ocr_jobs))
        logging.info(f"OCR em {len(ocr_jobs)} páginas → workers={max_workers}, gpu={can_gpu}")

        with ProcessPoolExecutor(max_workers=max_workers) as exe:
            futures = {
                exe.submit(_ocr_page_bytes, i, img_bytes, langs, not can_gpu): i
                for i, img_bytes in ocr_jobs
            }
            for fut in as_completed(futures):
                i = futures[fut]
                try:
                    i, text, elapsed = fut.result(timeout=120)
                    logging.info(f"Pág {i} OCR em {elapsed:.2f}s")
                    page_texts.append((i, text))
                except TimeoutError:
                    logging.error(f"[TIMEOUT] OCR pág {i}")
                except Exception as e:
                    logging.error(f"[ERRO] OCR pág {i}: {e}")

    # 3) monta e salva
    page_texts.sort(key=lambda x: x[0])
    full = "\n\n".join(txt for _, txt in page_texts)
    out_md.write_text(full, encoding='utf-8')
    logging.info(f"[OK] Salvou em: {out_md}")
    return full