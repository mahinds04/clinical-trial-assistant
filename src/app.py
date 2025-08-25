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

def initialize_assistant():
    """Initialize the clinical trial assistant with error handling."""
    try:
        assistant = ClinicalTrialAssistant()
        return assistant, None
    except Exception as e:
        return None, str(e)

def load_demo_data():
    """Load and display demo data statistics."""
    try:
        data_path = Path(__file__).parent.parent / "data" / "clin_trials_demo.csv"
        if data_path.exists():
            df = pd.read_csv(data_path)
            return df
    except Exception as e:
        st.error(f"Error loading demo data: {e}")
    return None

def main():
    st.title("🏥 Clinical Trial Assistant")
    st.markdown("Ask questions about clinical trials and get AI-powered answers from our database.")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This assistant helps you find information about clinical trials using natural language queries.
        
        **Example questions:**
        - "What trials are recruiting for cancer?"
        - "Tell me about Phase 2 diabetes studies"
        - "What heart disease prevention trials are available?"
        """)
        
        # Display demo data info
        df = load_demo_data()
        if df is not None:
            st.header("Dataset Info")
            st.metric("Total Trials", len(df))
            
            # Status distribution
            if 'Overall Status' in df.columns:
                status_counts = df['Overall Status'].value_counts()
                st.subheader("Status Distribution")
                for status, count in status_counts.items():
                    st.text(f"{status}: {count}")
            
            # Phase distribution
            if 'Phases' in df.columns:
                phase_counts = df['Phases'].value_counts()
                st.subheader("Phase Distribution")
                for phase, count in phase_counts.items():
                    st.text(f"{phase}: {count}")
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        with st.spinner("Initializing Clinical Trial Assistant..."):
            assistant, error = initialize_assistant()
            if assistant:
                st.session_state.assistant = assistant
                st.success("Assistant initialized successfully!")
            else:
                st.error(f"Failed to initialize assistant: {error}")
                st.info("This might be because the vector database hasn't been created yet. Please run the indexer first.")
                return
    
    # Chat interface
    st.header("Ask a Question")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. {source.get('brief_title', 'Untitled')}**")
                        st.markdown(f"- Status: {source.get('status', 'Unknown')}")
                        st.markdown(f"- Phase: {source.get('phase', 'Unknown')}")
                        st.markdown(f"- NCT ID: {source.get('nct_id', 'Unknown')}")
                        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("What would you like to know about clinical trials?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching trials and generating response..."):
                try:
                    response = st.session_state.assistant.query(prompt, n_results=3)
                    answer = response.get("answer", "I apologize, but I couldn't generate a response.")
                    sources = response.get("sources", [])
                    
                    st.markdown(answer)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    
                    # Display sources
                    if sources:
                        with st.expander("View Sources"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**{i}. {source.get('brief_title', 'Untitled')}**")
                                st.markdown(f"- Status: {source.get('status', 'Unknown')}")
                                st.markdown(f"- Phase: {source.get('phase', 'Unknown')}")
                                st.markdown(f"- NCT ID: {source.get('nct_id', 'Unknown')}")
                                if i < len(sources):
                                    st.markdown("---")
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Additional features
    st.header("Trial Explorer")
    
    # Display demo data table
    df = load_demo_data()
    if df is not None:
        st.subheader("Available Clinical Trials")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            if 'Overall Status' in df.columns:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All"] + list(df['Overall Status'].unique())
                )
        
        with col2:
            if 'Phases' in df.columns:
                phase_filter = st.selectbox(
                    "Filter by Phase", 
                    ["All"] + list(df['Phases'].unique())
                )
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter != "All" and 'Overall Status' in df.columns:
            filtered_df = filtered_df[filtered_df['Overall Status'] == status_filter]
        if phase_filter != "All" and 'Phases' in df.columns:
            filtered_df = filtered_df[filtered_df['Phases'] == phase_filter]
        
        # Display filtered data
        st.dataframe(filtered_df, use_container_width=True)
        
        # Simple analytics
        if len(filtered_df) > 0:
            st.subheader("Quick Analytics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Filtered Trials", len(filtered_df))
            
            with col2:
                if 'Overall Status' in filtered_df.columns:
                    recruiting_count = len(filtered_df[filtered_df['Overall Status'] == 'Recruiting'])
                    st.metric("Recruiting", recruiting_count)
            
            with col3:
                if 'Phases' in filtered_df.columns:
                    phase2_count = len(filtered_df[filtered_df['Phases'].str.contains('Phase 2', na=False)])
                    st.metric("Phase 2", phase2_count)

if __name__ == "__main__":
    main()
