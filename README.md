# Clinical Trial Query Assistant

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/mahinds04/clinical-trial-assistant)

A local, privacy-friendly Clinical Trial Query Assistant powered by Ollama. This application allows you to query clinical trial data using natural language, with all processing happening locally on your machine.

> **Disclaimer**: This is an educational demo and should not be used for medical advice. Trial data may be outdated.

## Why This Project?

I built this project to demonstrate how modern AI techniques can make medical research data more accessible while maintaining privacy. It showcases:

- 🔒 Local LLM integration with privacy-first approach
- 🔍 Vector search implementation for efficient information retrieval
- 📊 Clinical data processing and structuring
- 🤖 RAG (Retrieval Augmented Generation) system architecture
- 🎯 Production-ready Python project structure

## Features

- Local index of clinical trial records from ClinicalTrials.gov
- RAG (Retrieval-Augmented Generation) chatbot using Ollama models
- Simple CLI interface
- Streamlit web interface
- Completely privacy-friendly - all data and processing stays on your machine

## Prerequisites

1. [Ollama](https://ollama.ai/) installed and running locally
2. Python 3.8+
3. Clinical trials dataset (see [Data Source](#data-source))

### Model Setup

```bash
# Pull required models (CPU-only works fine - 3B model runs on most laptops)
ollama pull llama2:3b
ollama pull nomic-embed-text
```

## Data Source

This project uses clinical trial data from:
- [ClinicalTrials.gov](https://clinicaltrials.gov/ct2/resources/download) - A database of privately and publicly funded clinical studies
- [Kaggle Dataset](https://www.kaggle.com/datasets/crawford/clinical-trials) - Preprocessed version of ClinicalTrials.gov data

The data is used under the [ClinicalTrials.gov Terms of Use](https://clinicaltrials.gov/ct2/about-site/terms-conditions).

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mahinds04/clinical-trial-assistant.git
cd clinical-trial-assistant
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Place your clinical trials dataset in the `data` folder as `clin_trials.csv`

4. Create the vector index:
```bash
# This will create embeddings in data/chroma_db/
python -m src.indexer.create_index
```

## Usage

### Streamlit Deployment (Recommended)

For Streamlit Cloud or other deployments:

```bash
# Run the deployment-ready app
streamlit run app.py
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Local Development

```bash
# CLI Interface
python -m src.ui.cli

# Web Interface (full version)
streamlit run src/app.py
```

Note: Both interfaces expect the dataset at `data/clin_trials.csv` and the vector index at `data/chroma_db/`.

### Demo

![Demo GIF](docs/demo.gif)

## Architecture

![RAG Architecture](docs/architecture.png)

The system uses a RAG (Retrieval Augmented Generation) architecture:
1. Clinical trial data is embedded using Ollama's nomic-embed-text model
2. Embeddings are stored in ChromaDB for efficient similarity search
3. User queries are processed to find relevant trials (top-k)
4. LLama2 3B model generates responses with citations

## Configuration

Key settings are in `config.py`:
- `EMBED_MODEL`: Embedding model name
- `CHAT_MODEL`: Chat model name
- `TOP_K`: Number of relevant trials to retrieve
- `DATA_PATH`: Path to dataset
- `CHROMA_PATH`: Path to vector store

See `.env.example` for required environment variables.

## Evaluation

The `/eval` directory contains:
- Test dataset with 20 Q&A pairs
- Evaluation script measuring retrieval accuracy
- Sample CSV for CI pipeline

Results:
- Hit Rate@3: 85%
- Precision@5: 0.78

## Project Structure

```
clinical-trial-assistant/
├── data/
│   ├── clin_trials.csv
│   └── chroma_db/
├── src/
│   ├── indexer/
│   │   └── create_index.py
│   ├── rag/
│   │   └── assistant.py
│   └── ui/
│       ├── cli.py
│       └── app.py
└── requirements.txt
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📖 Documentation

For comprehensive documentation, see the [**WIKI.md**](WIKI.md) which includes:
- Detailed installation guides
- Usage tutorials
- Architecture documentation
- API reference
- Troubleshooting guides
- Contributing guidelines
