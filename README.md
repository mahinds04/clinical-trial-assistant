# Clinical Trial Query Assistant

A local, privacy-friendly Clinical Trial Query Assistant powered by Ollama. This application allows you to query clinical trial data using natural language, with all processing happening locally on your machine.

## Features

- Local index of clinical trial records from ClinicalTrials.gov
- RAG (Retrieval-Augmented Generation) chatbot using Ollama models
- Simple CLI interface
- Streamlit web interface
- Completely privacy-friendly - all data and processing stays on your machine

## Prerequisites

1. [Ollama](https://ollama.ai/) installed and running locally
2. Python 3.8+
3. Clinical trials dataset from ClinicalTrials.gov (Kaggle)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/clinical-trial-assistant.git
cd clinical-trial-assistant
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Place your clinical trials dataset in the `data` folder as `clin_trials.csv`

4. Create the vector index:
```bash
python src/indexer/create_index.py
```

## Usage

### CLI Interface

Run the CLI interface:
```bash
python src/ui/cli.py
```

### Streamlit Interface

Run the Streamlit app:
```bash
streamlit run src/ui/app.py
```

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
