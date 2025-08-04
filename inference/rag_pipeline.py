from typing import List, Optional
from utils.sanitizers import format_chunks_for_prompt
from etl.load.vector_writer import VectorWriter
from inference.llm_api import call_llm

# Definindo prompts como constantes para maior modularidade
PROMPT_GENERATION_TEMPLATE = """
Responda à pergunta com base nas informações do contexto abaixo.

Regras:
- Use o contexto, validando com o que você conhece.
- Na reposta dê um resumo coerente e claro e em português, máximo 4 parágrafos.
- Se a resposta não estiver no contexto, diga apenas: "Não foi possível encontrar uma resposta com base nas informações fornecidas."

[Pergunta]
{query}

[Contexto]
{context}

[Resposta]

"""

MODEL_NAME = "tiny"

class RagPipeline:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.vector_writer = VectorWriter(persist_directory=persist_directory)

    def retrieve_context(self, query: str, k: int = 5) -> List[str]:
        """
        Recupera os trechos (chunks) mais relevantes da base de conhecimento.
        Adiciona tratamento de exceções para falhas na busca.
        """
        try:
            documents = self.vector_writer.query(query, k=k)
            return [doc.page_content for doc in documents]
        except Exception as e:
            print(f"Erro na recuperação de contexto: {e}")
            return []

    def build_prompt(self, query: str, context_chunks: List[str]) -> str:
        """
        Cria um prompt de geração a partir do template pré-definido.
        """
        context = format_chunks_for_prompt(context_chunks)
        return PROMPT_GENERATION_TEMPLATE.format(context=context, query=query)
    
    def generate_answer(self, query: str, k: int = 5, max_tokens: int = 512) -> str:
        context_chunks = self.retrieve_context(query, k=k)

        if not context_chunks:
            return "⚠️ Desculpe, não encontrei informações relevantes na base de conhecimento."

        prompt = self.build_prompt(query, context_chunks)
        try:
            
            raw_answer = call_llm(prompt, model_name=MODEL_NAME, max_tokens=max_tokens)
        except Exception as e:
            print(f"Erro ao gerar a resposta: {e}")
            return "⚠️ Ocorreu um erro ao tentar gerar a resposta."

        return f"\n\n{raw_answer}"