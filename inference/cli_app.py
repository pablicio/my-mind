import sys
from inference.rag_pipeline import RagPipeline

def cli_app():
    # Inicializa a pipeline com o diretório persistente de embeddings
    rag = RagPipeline(persist_directory="./data/output/embeddings/")

    print("=== RAG CLI App ===")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        query = input("Pergunta: ").strip()
        if query.lower() in {"sair", "exit", "quit"}:
            print("Encerrando o programa. Até logo!")
            sys.exit(0)

        if not query:
            print("⚠️ Por favor, digite uma pergunta válida.\n")
            continue

        try:
            # Geração da resposta com k e max_tokens configuráveis
            resposta = rag.generate_answer(query, k=3, max_tokens=512)
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            continue

        print("\nResposta:")
        print(resposta)
        print("\n" + "=" * 40 + "\n")

