# Etapa base com Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza e instala dependências de sistema
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta do Streamlit (caso use)
EXPOSE 8501

# Comando padrão pode ser o CLI, main, ou streamlit
CMD ["python", "main.py"]
# ou: CMD ["streamlit", "run", "inference/streamlite_app.py"]
