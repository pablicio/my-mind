# 🧠 My Mind

## 🤖 LLM-Powered PDF & Notes ETL Pipeline (Python)

**My Mind** is a modular **ETL pipeline** for extracting, cleaning, and transforming PDF documents (both digital and scanned) into structured **Markdown files**. These files can be used as contextual data for **LLM-powered applications** such as:

* Retrieval-Augmented Generation (RAG)
* Semantic search
* Personal assistants or chatbots
* Custom knowledge bases

Optimized for **personal knowledge management**, but easily extendable to **enterprise-scale document processing**.

---
## 🎯 Key Features

* ✅ Supports both **scanned** and **text-based PDFs**
* ✅ OCR powered by **EasyOCR** with GPU fallback
* ✅ Converts PDFs to images via **pdf2image**
* ✅ Intelligent file loader: detects OCR vs structured extraction
* ✅ Modular ETL folders: `extract/`, `transform/`, `load/`, `utils/`
* ✅ Saves cleaned, structured Markdown files with metadata
* ✅ Optional embedding pipeline using **LangChain + OpenAI**
* ✅ Robust logging and error handling (PDF-by-PDF)
* ✅ Automatic cleanup of temporary files

---

## 🏗️ Project Structure

```
project_root/
├── etl/                         
│   ├── extract/                 # File type detection, OCR and loader logic
│   │   ├── loader_files.py         # Loads structured documents (Text, Docx, Epub, etc.)
│   │   ├── ocr_files.py            # OCR pipeline for images and scanned PDFs
│   │   └── smart_loader.py        # Main controller (decides loader vs OCR)
│   │
│   ├── transform/               # Text preprocessing
│   │   ├── text_cleaner.py         # Cleans newlines, symbols, whitespace
│   │   └── text_splitter.py        # Splits long texts into chunks
│   │
│   ├── load/                    # Output persistence
│   │   ├── markdown_writer.py      # Saves as `.md` with metadata
│   │   ├── vector_writer.py        # Optional vector DB embedding (FAISS, Chroma)
│   │   └── json_writer.py          # Optional JSON export
│   │
│   └── run_etl.py              # Main pipeline runner script
│
├── data/                       
│   ├── raw/                        # Input documents (PDFs, images)
│   ├── processed/                 # Cleaned intermediate texts
│   └── output/                    # Final `.md`, `.json`, embeddings, etc.
│
├── training/                    # Optional fine-tuning support
│   ├── dataset_preparation.py      # Converts extracted data into training-ready format
│   ├── train.py                    # Fine-tunes models (e.g. LLaMA, GPT)
│   └── checkpoints/               # Saved model weights
│
├── inference/                   # RAG-ready serving interface
│   ├── rag_pipeline.py             # Query + retrieval + generation logic
│   └── cli_app.py                  # CLI or web interface (Streamlit/FastAPI)
│
├── utils/                       # Reusable helpers
│   ├── logging_utils.py
│   ├── file_utils.py
│   ├── config_loader.py
│   └── sanitizers.py
│
├── config/                     
│   ├── settings.py                 # Central pipeline settings
│   └── .env                        # API keys and secrets
│
├── notebooks/                   # Jupyter notebooks for testing and exploration
│   └── ocr_eval.ipynb
│
├── requirements.txt             
├── README.md
└── main.py                      # Entry point for full pipeline execution
```

---

## ⚙️ Getting Started

### 1. Install dependencies

```bash
git clone https://github.com/pablicio/my-mind.git
cd my-mind
pip install -r requirements.txt
```

### 2. Set up `.env` (Optional for embeddings)

Create a `.env` file in the root folder:

```env
OPENAI_API_KEY=sk-...
```

### 3. Configure the pipeline

Edit the config file `config/settings.py`:

```python
input_dir = "input/"
output_dir = "output/"
ocr_languages = ['pt', 'en']
chunk_size = 1000
chunk_overlap = 100
```

---

## 🔁 Pipeline Overview

### 📥 Extraction (`etl/extract/`)

* Uses EasyOCR to extract text from scanned images or PDFs
* Auto-selects loader based on file type
* PDF scanned vs structured is detected dynamically
* Text files (.txt, .docx, .epub) use LangChain-compatible loaders

### 🧹 Transformation (`etl/transform/`)

* Cleans and normalizes extracted text
* Optionally splits into chunks for embedding

### 📤 Load (`etl/load/`)

* Saves Markdown (`.md`) files with YAML frontmatter
* Optionally embeds content into FAISS or Chroma vector stores

Example Markdown output:

```markdown
---
source: example.pdf
pages: 4
processed: 2025-07-22
---

## Page 1
(Text here...)

## Page 2
(Next page...)
```

---

## 🧪 Run the Pipeline

```bash
python main.py
```

Each file will be:

1. Checked for OCR or loader-based extraction
2. Converted (if needed) to image
3. Processed and cleaned
4. Saved as `.md` (optionally embedded)

---

## 🧠 Optional Embeddings (LangChain + OpenAI)

Add this to generate embeddings:

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embeddings = OpenAIEmbeddings()
db = FAISS.from_texts(text_chunks, embeddings)
```

---

## 🔍 Use Cases

* 📖 Knowledge assistants over personal PDFs
* 🔎 Semantic search for enterprise documents
* 🧘‍♀️ Life-logging and memory augmentation
* 🧾 Legal, financial, academic file indexing
* 💬 Natural-language document Q\&A

---

## 🛣️ Roadmap

* [ ] Whisper support for audio-based PDFs
* [ ] Web UI with file upload
* [ ] Vector DB integration (Weaviate, Pinecone, Qdrant)
* [ ] Obsidian vault export
* [ ] Metadata tagging + chunk filtering

---

## 📄 License

MIT License — free for personal and commercial use.

---

## 🤝 Contributing

PRs are welcome! For feature requests or improvements, feel free to open an issue.

---

## 👋 Author

Made with ❤️ by \[Thiago Pablicio]
📧 Email: [pabliciotjg@gmail.com)](mailto:pabliciotjg@gmail.com)
🔗 GitHub: [github.com/pablicio](https://github.com/pablicio)
🔗 LinkedIn: [Thiago Pablicio](https://www.linkedin.com/in/thiago-pablicio-86357446/)

