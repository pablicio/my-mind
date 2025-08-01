# main.py
from etl.extract.smart_loader import load_document
from etl.transform.text_cleaner import process_markdown_folder
from etl.transform.text_splitter import chunk_markdown_folder

# Exemplo de uso
if __name__ == '__main__':
    
    # Pipeline de Extração
    
    # Lista de diretórios ou arquivos
    # paths = [
    #     r"D:\ARQUIVOS",
    #     r"D:\Workspace\NOTAS\GST"
    # ]

    # Executa para cada caminho
    # for path in paths:
    #     load_document(path)

    # Pipeline de Transformação
    # Clean data
    # process_markdown_folder(r"data\output", r"data\output\clean")

    # Creat Chunks
    chunk_markdown_folder(r"data\output\clean", r"data\output\chunks\chunks_output.json")