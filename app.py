import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add src directory to Python path for imports
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the assistant
try:
    from rag.assistant import ClinicalTrialAssistant
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all dependencies are installed correctly.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple main function for testing
def main():
    st.title("🏥 Clinical Trial Query Assistant")
    st.write("Welcome to the Clinical Trial Assistant!")
    
    # Test the assistant import
    try:
        assistant = ClinicalTrialAssistant()
        st.success("✅ Assistant loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load assistant: {e}")
    
    st.info("This is a simplified version for deployment testing.")

if __name__ == "__main__":
    main()


