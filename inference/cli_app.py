import sys
from inference.rag_pipeline import RagPipeline

def main():
    rag = RagPipeline(persist_directory="./data/output/embeddings/")

    print("=== RAG CLI App ===")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        query = input("Pergunta: ").strip()
        if query.lower() in {"sair", "exit", "quit"}:
            print("Encerrando o programa. Até logo!")
            sys.exit(0)

        if not query:
            print("Por favor, digite uma pergunta válida.")
            continue

        resposta = rag.generate_answer(query, k=2)
        print("\nResposta:\n", resposta)
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
