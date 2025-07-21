# main.py
from etl.extract.smart_loader import load_document

# Exemplo de uso
if __name__ == '__main__':
    raw_path = r"D:\ARQUIVOS"

    load_document(raw_path)