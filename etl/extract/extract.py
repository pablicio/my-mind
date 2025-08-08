
from etl.extract.smart_loader import load_document

def run_extraction(paths: list[str]):
    print("\n🟢 Iniciando extração...")
    for path in paths:
        load_document(path)