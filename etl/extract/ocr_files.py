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

def read_text_from_image(image_input, output_dir: Path = None, image_name=None) -> str:
    """
    Executa OCR em uma imagem e salva/recupera o resultado (cache simples).

    Args:
        image_input: Caminho da imagem (str/Path) ou imagem como array numpy.
        reader: Instância do easyocr.Reader.
        output_dir: Pasta para salvar o texto OCR (opcional).
        image_name: Nome alternativo (usado se image_input for array).

    Returns:
        Texto extraído da imagem ou False se já existir.
    """
    img_np = None
    image_path = None

    # Detecta tipo de entrada
    if isinstance(image_input, (str, Path)):
        image_path = Path(image_input)
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)
    elif isinstance(image_input, np.ndarray):
        img_np = image_input
        if image_name:
            image_path = Path(image_name)
    else:
        raise ValueError("image_input deve ser caminho ou numpy array")

    # Cache: pula se já existe
    if output_dir and image_path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{image_path.stem}_ocr.md"
        if output_file.exists():
            print(f"[SKIP] OCR já existe: {output_file.name}")
            return False

    # Executa OCR
    logging.info(f"[OCR] Processando: {image_path.name if image_path else 'imagem sem nome'}")
    reader = create_easyocr_reader(['pt', 'en'])
    results = reader.readtext(img_np)
    
    text = " ".join([word for _, word, _ in results])
    save_text_output(text, image_input, Path(output_dir))

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
    output_file = output_dir / f"{source_path.stem}_ocr.md"
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
    output_file = output_dir / f"{pdf_path.stem}_ocr.md"

    if output_file.exists():
        print(f"[SKIP] OCR já realizado. Pulando: {output_file.name}")
        return output_file.read_text(encoding='utf-8')

    reader = create_easyocr_reader(langs)
    logging.info(f"Convertendo PDF em imagens (dpi=150)...")
    images = convert_from_path(str(pdf_path), dpi=150)

    logging.info(f"Executando OCR em {len(images)} páginas...")
    all_texts = []

    for i, image in enumerate(images, 1):
        logging.info(f"Pág {i}/{len(images)}")
        try:
            text = read_text_from_image(np.array(image), reader, output_dir, image_name=f"{pdf_path.stem}_page_{i}")
        except RuntimeError as e:
            logging.error(f"Erro na página {i}: {e}")
            logging.info("Tentando fallback para CPU...")
            reader = create_easyocr_reader(langs, force_cpu=True)
            text = read_text_from_image(np.array(image), reader, output_dir, image_name=f"{pdf_path.stem}_page_{i}")
        all_texts.append(text)

    full_text = "\n\n".join(all_texts)
    return save_text_output(full_text, pdf_path, output_dir).read_text(encoding='utf-8')
