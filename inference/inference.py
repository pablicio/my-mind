# Inferência
from inference.streamlite_app import chat_app
from inference.cli_app import cli_app

def run_inference(mode="cli"):
    print("\n🟢 Iniciando interface de inferência...")
    if mode == "cli":
        cli_app()
    elif mode == "chat":
        chat_app()
    else:
        raise ValueError("Modo de inferência inválido. Use 'cli' ou 'chat'.")