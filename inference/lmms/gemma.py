from transformers import pipeline

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = pipeline(
            "text-generation",
            model="google/gemma-2b-it",
            device_map="auto",
            trust_remote_code=True
        )
    return _llm

def call_llm(prompt: str, max_tokens: int = 256) -> str:
    llm = get_llm()
    output = llm(prompt.strip(), max_new_tokens=max_tokens)
    return output[0]["generated_text"].strip()
