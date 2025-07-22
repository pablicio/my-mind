# main.py
from etl.extract.smart_loader import load_document

# Exemplo de uso
if __name__ == '__main__':
    # Lista de diretórios ou arquivos
    paths = [
        r"D:\ARQUIVOS",
        r"D:\Workspace\NOTAS\GST"
    ]

    # Executa para cada caminho
    for path in paths:
        load_document(path)
