import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Simple app without complex dependencies
st.set_page_config(
    page_title="Clinical Trial Assistant",
    page_icon="🏥",
    layout="wide"
)

def main():
    st.title("🏥 Clinical Trial Query Assistant")
    st.write("Welcome to the Clinical Trial Assistant!")
    
    # Show system info
    st.subheader("System Information")
    st.write(f"Python version: {sys.version}")
    st.write(f"Working directory: {os.getcwd()}")
    
    # Check if src directory exists
    src_dir = Path("src")
    if src_dir.exists():
        st.success("✅ Source directory found")
        
        # Check for assistant file
        assistant_file = src_dir / "rag" / "assistant.py"
        if assistant_file.exists():
            st.success("✅ Assistant file found")
        else:
            st.error("❌ Assistant file not found")
    else:
        st.error("❌ Source directory not found")
    
    # Simple chat interface
    st.subheader("Query Interface")
    user_input = st.text_input("Ask about clinical trials:")
    
    if user_input:
        st.write(f"You asked: {user_input}")
        st.info("This is a simplified version. The full RAG system will be available once all dependencies are loaded.")
    
    # Sample data display
    st.subheader("Sample Clinical Trial Data")
    sample_data = {
        'NCT ID': ['NCT12345678', 'NCT87654321', 'NCT11111111'],
        'Title': ['Cancer Immunotherapy Trial', 'Diabetes Drug Study', 'COVID-19 Vaccine Trial'],
        'Phase': ['Phase 3', 'Phase 2', 'Phase 3'],
        'Status': ['Recruiting', 'Completed', 'Active']
    }
    df = pd.DataFrame(sample_data)
    st.dataframe(df)

if __name__ == "__main__":
    main()
