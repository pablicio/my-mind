# My Mind

## 🤖 LLM-Powered PDF & Notes ETL Pipeline (Python)

This project provides a **modular ETL pipeline** in Python that transforms raw PDF files — including scanned images — into structured Markdown files. These can be used as **contextual data sources for LLM-based systems** (e.g. retrieval-augmented generation, semantic search, assistants, or chatbots).

The system is optimized for **personal knowledge management**, but can be easily scaled to support **enterprise document processing**.


## 🎯 Key Features

- ✅ Extracts text from both digital and scanned PDFs using **EasyOCR**
- ✅ Converts pages to images for OCR using **pdf2image** or **PyMuPDF**
- ✅ Cleans and normalizes text before saving it to `.md` files
- ✅ Supports recursive folder traversal
- ✅ Uses **LangChain + OpenAI** to embed content (optional)
- ✅ Modular architecture for ETL: `extract/`, `transform/`, `load/`, `utils/`, `config/`
- ✅ Automatic temporary file cleanup
- ✅ Logs errors and processes robustly, PDF-by-PDF

---

## 🏗️ Project Structure

```
project_root/
├── etl/                         # Módulos ETL (extração, transformação, carga)
│   ├── extract/                 # Extração de dados brutos (OCR, PDF, web, etc.)
│   │   ├── pdf_to_image.py
│   │   ├── ocr_easyocr.py
│   │   └── file_collector.py
│   ├── transform/               # Limpeza, normalização, split de texto
│   │   ├── text_cleaner.py
│   │   └── text_splitter.py
│   ├── load/                    # Escrita em Markdown, JSON, vetores, etc.
│   │   ├── markdown_writer.py
│   │   └── vector_store_writer.py
│   └── run_etl.py               # Script de orquestração da etapa ETL
│
├── data/                        # Dados persistentes (não versionados no Git)
│   ├── raw/                     # PDFs, imagens e dados brutos
│   ├── processed/               # Dados transformados
│   └── output/                  # Saídas finais (Markdowns, JSONs, embeddings)
│
├── training/                    # Tudo relacionado a fine-tuning (opcional)
│   ├── dataset_preparation.py   # Conversão para dataset de treino
│   ├── train.py                 # Script de treinamento
│   └── checkpoints/             # Pesos treinados salvos
│
├── inference/                   # Pipelines de inferência / Q&A / RAG
│   ├── rag_pipeline.py          # Busca + geração com LLM
│   └── cli_app.py               # Interface de linha de comando (ou FastAPI, Streamlit etc.)
│
├── utils/                       # Funções auxiliares reutilizáveis
│   ├── logging_utils.py
│   ├── file_utils.py
│   ├── config_loader.py
│   └── sanitizers.py
│
├── config/                      # Configurações centralizadas
│   ├── settings.py
│   └── .env                     # Chaves secretas e variáveis de ambiente
│
├── notebooks/                   # Experimentos exploratórios (Jupyter)
│   └── ocr_eval.ipynb
│
├── requirements.txt             # Dependências Python
├── README.md
└── main.py                      # Ponto de entrada principal (opcional)

````

---

## ⚙️ Setup Instructions

### 1. Clone and install dependencies

```bash
git clone https://github.com/pablicio/my-mind.git
cd my-mind
pip install -r requirements.txt
````

### 2. Configure your `.env` (for OpenAI, if using embeddings)

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

### 3. Configure pipeline settings

Edit `config/settings.py` to adjust:

```python
input_dir = "input/"
output_dir = "output/"
ocr_languages = ['en', 'pt']  # EasyOCR supported languages
chunk_size = 1000             # For LangChain chunking (optional)
chunk_overlap = 100
```

---

## 🧠 How It Works

### 📥 Extraction Phase (`extract/`)

* `pdf_to_image.py`: Converts every PDF page into a high-res `.png` image
* `ocr.py`: Uses EasyOCR to read text from each image

### 🧹 Transformation Phase (`transform/`)

* `text_cleaner.py`: Optional cleaning (e.g., remove artifacts, normalize unicode)

### 📤 Load Phase (`load/`)

* `markdown_writer.py`: Writes one `.md` file per PDF with sections per page
* Output example:

  ```markdown
  ---
  pdf: my_report.pdf
  pages: 5
  ---
  ## Page 1
  (text here)
  ## Page 2
  (text here)
  ```

---

## 🧪 Running the Pipeline

Use the following command to process all PDFs:

```bash
python main.py
```

Each PDF will be:

1. Converted to images
2. Processed with OCR
3. Converted into clean Markdown
4. Saved in the `/output` folder

All temporary files are cleaned up automatically.

---

## 📌 Error Handling & Logging

* All processing steps are wrapped in `try/except` blocks.
* Errors are logged using Python's `logging` module (`pipeline.log`).
* Faulty PDFs are skipped, the pipeline continues.

---

## 🔗 Optional: Embedding with LangChain + OpenAI

To enable document chunking and embeddings (e.g. for vector storage):

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embeddings = OpenAIEmbeddings()
db = FAISS.from_texts(text_chunks, embeddings)
```

This allows the Markdown chunks to be embedded and queried in a RAG pipeline.

---

## 🧠 Use Cases

* 🧘 Personal LLM-powered assistants
* 📂 Semantic search over your notes
* 📑 Legal or HR document processors
* 🤖 Enterprise knowledge bots
* 📝 Structured summarization from PDFs

---

## 🛣️ Roadmap

* [ ] Add Whisper transcription support for audio PDFs
* [ ] Add front-end drag-and-drop web interface
* [ ] Integrate with vector DBs (Weaviate, Pinecone, Qdrant)
* [ ] Export to other formats (JSON, CSV, Obsidian vault)

---

## 📄 License

MIT License. Feel free to use, fork, and adapt.

---

## 🙋‍♂️ Contributing

Pull requests are welcome. For major changes, open an issue first to discuss the direction.

---

## 👋 Contact

Made with ❤️ by \[Your Name]
📬 Email: [your@email.com](mailto:your@email.com)
🌐 Linkedin: [https://github.com/yourusername](https://github.com/yourusername)


