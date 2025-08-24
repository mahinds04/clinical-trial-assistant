import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimpleClinicalTrialAssistant:
    """Simplified version for demo purposes when full dependencies aren't available."""
    
    def __init__(self):
        self.demo_data = self.load_demo_data()
    
    def load_demo_data(self):
        """Load demo data from CSV."""
        try:
            data_path = Path(__file__).parent.parent / "data" / "clin_trials_demo.csv"
            if data_path.exists():
                # Use basic file reading since pandas might not be available
                with open(data_path, 'r') as f:
                    lines = f.readlines()
                
                # Parse CSV manually
                headers = lines[0].strip().split(',')
                data = []
                for line in lines[1:]:
                    values = line.strip().split(',')
                    if len(values) == len(headers):
                        data.append(dict(zip(headers, values)))
                return data
        except Exception as e:
            st.error(f"Error loading demo data: {e}")
        return []
    
    def simple_search(self, query):
        """Simple keyword-based search in demo data."""
        query_lower = query.lower()
        results = []
        
        for trial in self.demo_data:
            # Search in title, conditions, and status
            searchable_text = f"{trial.get('Brief Title', '')} {trial.get('Conditions', '')} {trial.get('Overall Status', '')}".lower()
            
            if any(word in searchable_text for word in query_lower.split()):
                results.append(trial)
        
        return results[:3]  # Return top 3 results
    
    def query(self, question, n_results=3):
        """Query with simple search and basic response generation."""
        results = self.simple_search(question)
        
        if not results:
            return {
                "answer": "I couldn't find any trials matching your query in the demo dataset. Try searching for 'cancer', 'diabetes', 'heart disease', 'asthma', or 'alzheimer's'.",
                "sources": [],
                "nct_ids": []
            }
        
        # Generate a simple response
        answer_parts = [f"I found {len(results)} relevant clinical trial(s):"]
        nct_ids = []
        
        for i, trial in enumerate(results, 1):
            title = trial.get('Brief Title', 'Untitled')
            status = trial.get('Overall Status', 'Unknown')
            phase = trial.get('Phases', 'Unknown')
            nct_id = trial.get('NCT Number', 'Unknown')
            
            answer_parts.append(f"{i}. {title} - Status: {status}, Phase: {phase}")
            nct_ids.append(nct_id)
        
        answer_parts.append(f"\nSources: {', '.join(nct_ids)}")
        
        return {
            "answer": "\n".join(answer_parts),
            "sources": results,
            "nct_ids": nct_ids
        }

def load_demo_data_for_display():
    """Load demo data for display purposes."""
    try:
        data_path = Path(__file__).parent.parent / "data" / "clin_trials_demo.csv"
        if data_path.exists():
            with open(data_path, 'r') as f:
                lines = f.readlines()
            
            headers = lines[0].strip().split(',')
            data = []
            for line in lines[1:]:
                values = line.strip().split(',')
                if len(values) == len(headers):
                    data.append(dict(zip(headers, values)))
            return data
    except Exception as e:
        st.error(f"Error loading demo data: {e}")
    return []

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
        - "Show me asthma treatment studies"
        """)
        
        # Display demo data info
        demo_data = load_demo_data_for_display()
        if demo_data:
            st.header("Dataset Info")
            st.metric("Total Trials", len(demo_data))
            
            # Status distribution
            statuses = [trial.get('Overall Status', 'Unknown') for trial in demo_data]
            status_counts = {}
            for status in statuses:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            st.subheader("Status Distribution")
            for status, count in status_counts.items():
                st.text(f"{status}: {count}")
            
            # Phase distribution
            phases = [trial.get('Phases', 'Unknown') for trial in demo_data]
            phase_counts = {}
            for phase in phases:
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
            st.subheader("Phase Distribution")
            for phase, count in phase_counts.items():
                st.text(f"{phase}: {count}")
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        with st.spinner("Initializing Clinical Trial Assistant..."):
            try:
                # Try to use the full assistant first
                from rag.assistant import ClinicalTrialAssistant
                assistant = ClinicalTrialAssistant()
                st.session_state.assistant = assistant
                st.session_state.assistant_type = "full"
                st.success("Full assistant initialized successfully!")
            except Exception as e:
                # Fall back to simple assistant
                st.warning(f"Full assistant not available ({str(e)}), using simplified version with demo data.")
                assistant = SimpleClinicalTrialAssistant()
                st.session_state.assistant = assistant
                st.session_state.assistant_type = "simple"
                st.success("Demo assistant initialized successfully!")
    
    # Chat interface
    st.header("Ask a Question")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. {source.get('Brief Title', 'Untitled')}**")
                        st.markdown(f"- Status: {source.get('Overall Status', 'Unknown')}")
                        st.markdown(f"- Phase: {source.get('Phases', 'Unknown')}")
                        st.markdown(f"- NCT ID: {source.get('NCT Number', 'Unknown')}")
                        if i < len(message["sources"]):
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
                                st.markdown(f"**{i}. {source.get('Brief Title', 'Untitled')}**")
                                st.markdown(f"- Status: {source.get('Overall Status', 'Unknown')}")
                                st.markdown(f"- Phase: {source.get('Phases', 'Unknown')}")
                                st.markdown(f"- NCT ID: {source.get('NCT Number', 'Unknown')}")
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
    demo_data = load_demo_data_for_display()
    if demo_data:
        st.subheader("Available Clinical Trials")
        
        # Convert to display format
        display_data = []
        for trial in demo_data:
            display_data.append({
                "NCT Number": trial.get('NCT Number', ''),
                "Title": trial.get('Brief Title', ''),
                "Status": trial.get('Overall Status', ''),
                "Phase": trial.get('Phases', ''),
                "Condition": trial.get('Conditions', ''),
                "Start Date": trial.get('Start Date', '')
            })
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            all_statuses = list(set([trial.get('Overall Status', 'Unknown') for trial in demo_data]))
            status_filter = st.selectbox("Filter by Status", ["All"] + all_statuses)
        
        with col2:
            all_phases = list(set([trial.get('Phases', 'Unknown') for trial in demo_data]))
            phase_filter = st.selectbox("Filter by Phase", ["All"] + all_phases)
        
        # Apply filters
        filtered_data = display_data.copy()
        if status_filter != "All":
            filtered_data = [trial for trial in filtered_data if trial["Status"] == status_filter]
        if phase_filter != "All":
            filtered_data = [trial for trial in filtered_data if trial["Phase"] == phase_filter]
        
        # Display filtered data
        if filtered_data:
            st.table(filtered_data)
            
            # Simple analytics
            st.subheader("Quick Analytics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Filtered Trials", len(filtered_data))
            
            with col2:
                recruiting_count = len([t for t in filtered_data if t["Status"] == "Recruiting"])
                st.metric("Recruiting", recruiting_count)
            
            with col3:
                phase2_count = len([t for t in filtered_data if "Phase 2" in t["Phase"]])
                st.metric("Phase 2", phase2_count)
        else:
            st.info("No trials match the selected filters.")

if __name__ == "__main__":
    main()