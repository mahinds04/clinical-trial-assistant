import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rag.assistant import ClinicalTrialAssistant

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rest of the code from src/ui/app.py...
