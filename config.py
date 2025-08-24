"""Configuration for the Clinical Trial Assistant."""
from pathlib import Path

# Model configuration
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama2:3b"
TOP_K = 5

# Data paths
ROOT_DIR = Path(__file__).parent
DATA_PATH = ROOT_DIR / "data" / "clin_trials.csv"
CHROMA_PATH = ROOT_DIR / "data" / "chroma_db"

# Retrieval settings
MIN_RELEVANCE_SCORE = 0.7
MAX_CONTEXT_LENGTH = 2000

# UI settings
MAX_HISTORY_LENGTH = 10
TEMPERATURE = 0.7
