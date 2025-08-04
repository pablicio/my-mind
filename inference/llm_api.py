import importlib

def call_llm(prompt: str, model_name: str, max_tokens: int = 256) -> str:
    """
    Chamada genérica que delega para o módulo do modelo específico.
    """
    try:
        module = importlib.import_module(f"inference.lmms.{model_name}")
        return module.call_llm(prompt, max_tokens=max_tokens)
    except ModuleNotFoundError:
        raise ValueError(f"Modelo '{model_name}' não encontrado.")
    except AttributeError:
        raise ValueError(f"O módulo '{model_name}' deve definir 'call_llm(prompt, max_tokens)'.")

