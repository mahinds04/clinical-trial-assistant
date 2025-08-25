import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Optional imports (graceful fallback)
try:
    import folium
    from streamlit_folium import folium_static
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.warning("Map features disabled: folium not available")

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    st.warning("Advanced analytics disabled: scikit-learn not available")

# Add src directory to Python path for imports
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the assistant
try:
    from rag.assistant import ClinicalTrialAssistant
    ASSISTANT_AVAILABLE = True
except ImportError as e:
    st.error(f"Assistant import error: {e}")
    ASSISTANT_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .stButton>button {
        width: 100%;
    }
    .trial-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .metadata-badge {
        background-color: #f0f2f6;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the assistant
@st.cache_resource
def get_assistant():
    if ASSISTANT_AVAILABLE:
        return ClinicalTrialAssistant()
    return None

def format_trial_card(trial):
    """Format trial information as a card with metadata badges."""
    return f"""
    <div class="trial-card">
        <h4>{trial.get('brief_title', 'Unknown Title')}</h4>
        <p>
            <span class="metadata-badge">Phase: {trial.get('phase', 'N/A')}</span>
            <span class="metadata-badge">Status: {trial.get('status', 'N/A')}</span>
            <span class="metadata-badge">Purpose: {trial.get('purpose', 'N/A')}</span>
        </p>
        <p><small>Start Date: {trial.get('start_date', 'N/A')}</small></p>
    </div>
    """

def display_trial_filters(trials):
    """Display and handle trial filtering options."""
    if not trials:
        return trials
    
    col1, col2 = st.columns(2)
    with col1:
        phases = list(set(t.get('phase', '') for t in trials if t.get('phase')))
        selected_phase = st.multiselect("Filter by Phase", phases)
    
    with col2:
        statuses = list(set(t.get('status', '') for t in trials if t.get('status')))
        selected_status = st.multiselect("Filter by Status", statuses)
    
    filtered_trials = trials
    if selected_phase:
        filtered_trials = [t for t in filtered_trials if t.get('phase') in selected_phase]
    if selected_status:
        filtered_trials = [t for t in filtered_trials if t.get('status') in selected_status]
    
    return filtered_trials

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "saved_trials" not in st.session_state:
        st.session_state.saved_trials = []
    if "saved_searches" not in st.session_state:
        st.session_state.saved_searches = []
    if "custom_alerts" not in st.session_state:
        st.session_state.custom_alerts = []
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Chat"

def create_trial_visualizations(trials):
    """Create visualizations from trial data."""
    if not trials or not PLOTLY_AVAILABLE:
        st.info("Advanced visualizations require plotly (not available)")
        return
    
    # Convert trials list to DataFrame
    df = pd.DataFrame(trials)
    
    # Phase Distribution
    if 'phase' in df.columns:
        st.subheader("Trial Phases Distribution")
        phase_counts = df['phase'].value_counts()
        st.bar_chart(phase_counts)
    
    # Status Distribution
    if 'status' in df.columns:
        st.subheader("Trial Status Distribution")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)

def create_map_visualization(trials):
    """Create a map visualization of trial locations."""
    if not FOLIUM_AVAILABLE:
        st.info("Map visualization requires folium (not available)")
        return
        
    # Create a map centered on the US
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    
    # Add markers for each trial location
    for trial in trials:
        if 'location' in trial and trial['location']:
            folium.Marker(
                location=[trial['location']['lat'], trial['location']['lon']],
                popup=trial.get('brief_title', 'Unknown'),
                tooltip=trial.get('brief_title', 'Unknown')
            ).add_to(m)
    
    # Display the map
    folium_static(m)

def compare_trials(trial1, trial2):
    """Compare two trials and return similarity score."""
    if not SKLEARN_AVAILABLE:
        return 0.5  # Default similarity
        
    # Create TF-IDF vectors for comparison
    vectorizer = TfidfVectorizer()
    
    # Combine relevant fields for comparison
    def get_trial_text(trial):
        return f"{trial.get('brief_title', '')} {trial.get('condition', '')} {trial.get('purpose', '')}"
    
    texts = [get_trial_text(trial1), get_trial_text(trial2)]
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except:
        return 0.5

def main():
    initialize_session_state()
    
    # Title
    st.title("🏥 Clinical Trial Query Assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # View mode selection
        st.session_state.view_mode = st.radio(
            "View Mode",
            ["Chat", "Analysis Dashboard", "Trial Comparison"],
            key="view_mode_radio"
        )
        
        # Assistant settings
        if ASSISTANT_AVAILABLE:
            n_results = st.slider("Number of relevant trials", 1, 10, 3)
        else:
            st.warning("Assistant not available - using demo mode")
            n_results = 3
        
        st.markdown("---")
        st.markdown("### Quick Prompts")
        example_prompts = [
            "What phase 3 trials are available for breast cancer?",
            "Show me pediatric trials for rare diseases",
            "Are there any ongoing COVID-19 vaccine trials?",
            "What trials are available for type 2 diabetes?",
        ]
        
        for prompt in example_prompts:
            if st.button(prompt, key=f"prompt_{hash(prompt)}"):
                st.session_state.messages.append({"role": "user", "content": prompt})
        
        st.markdown("---")
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Main content based on view mode
    if st.session_state.view_mode == "Chat":
        # Initialize assistant
        assistant = get_assistant()
        
        # Main chat area
        chat_col, info_col = st.columns([2, 1])
        
        with chat_col:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "sources" in message:
                        trials = message["sources"]
                        filtered_trials = display_trial_filters(trials)
                        
                        for trial in filtered_trials:
                            st.markdown(format_trial_card(trial), unsafe_allow_html=True)
            
            # Chat input
            if prompt := st.chat_input("What would you like to know about clinical trials?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    if assistant and ASSISTANT_AVAILABLE:
                        try:
                            with st.spinner("Searching trials..."):
                                response = assistant.query(prompt, n_results=n_results)
                            st.markdown(response["answer"])
                            
                            trials = response.get("sources", [])
                            filtered_trials = display_trial_filters(trials)
                            
                            for trial in filtered_trials:
                                st.markdown(format_trial_card(trial), unsafe_allow_html=True)
                                
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response["answer"],
                                "sources": response.get("sources", [])
                            })
                        except Exception as e:
                            st.error(f"Error processing query: {e}")
                            st.info("This might be due to missing dependencies or data.")
                    else:
                        # Demo response when assistant not available
                        demo_response = f"Demo response for: '{prompt}'. The full RAG system will provide detailed clinical trial information once all dependencies are available."
                        st.markdown(demo_response)
                        
                        # Sample trials for demo
                        sample_trials = [
                            {
                                "brief_title": "Sample Cancer Immunotherapy Trial",
                                "phase": "Phase 3",
                                "status": "Recruiting",
                                "purpose": "Treatment",
                                "start_date": "2024-01-15"
                            },
                            {
                                "brief_title": "Sample Diabetes Drug Study",
                                "phase": "Phase 2",
                                "status": "Active",
                                "purpose": "Treatment",
                                "start_date": "2024-03-20"
                            }
                        ]
                        
                        for trial in sample_trials:
                            st.markdown(format_trial_card(trial), unsafe_allow_html=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": demo_response,
                            "sources": sample_trials
                        })
        
        # Info column
        with info_col:
            st.markdown("### About")
            st.markdown("""
            This assistant helps you explore clinical trials using natural language queries. 
            It uses RAG (Retrieval Augmented Generation) with advanced AI models.
            
            **Features:**
            - 🔍 Natural language search
            - 📊 Filter trials by phase and status
            - 💾 Local and private processing
            - 🤖 Powered by modern AI
            """)
            
            # System status
            st.markdown("### System Status")
            st.success("✅ Streamlit" if True else "❌ Streamlit")
            st.success("✅ Assistant" if ASSISTANT_AVAILABLE else "❌ Assistant (demo mode)")
            st.success("✅ Analytics" if SKLEARN_AVAILABLE else "❌ Analytics")
            st.success("✅ Maps" if FOLIUM_AVAILABLE else "❌ Maps")
            st.success("✅ Charts" if PLOTLY_AVAILABLE else "❌ Charts")
            
            # Session stats
            if st.session_state.messages:
                n_queries = len([m for m in st.session_state.messages if m["role"] == "user"])
                n_trials = sum(len(m.get("sources", [])) for m in st.session_state.messages if m["role"] == "assistant")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries", n_queries)
                with col2:
                    st.metric("Trials", n_trials)
    
    elif st.session_state.view_mode == "Analysis Dashboard":
        st.markdown("### Trial Analysis Dashboard")
        
        # Get all trials from chat history
        all_trials = []
        for message in st.session_state.messages:
            if message["role"] == "assistant" and "sources" in message:
                all_trials.extend(message["sources"])
        
        if all_trials:
            create_trial_visualizations(all_trials)
            create_map_visualization(all_trials)
            export_trials(all_trials)
        else:
            st.info("Start chatting to see trial analysis!")
    
    elif st.session_state.view_mode == "Trial Comparison":
        st.markdown("### Trial Comparison Tool")
        
        if st.session_state.saved_trials and len(st.session_state.saved_trials) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                trial1 = st.selectbox(
                    "Select First Trial",
                    st.session_state.saved_trials,
                    format_func=lambda x: x.get('brief_title', 'Unknown')
                )
            
            with col2:
                trial2 = st.selectbox(
                    "Select Second Trial",
                    [t for t in st.session_state.saved_trials if t != trial1],
                    format_func=lambda x: x.get('brief_title', 'Unknown')
                )
            
            if trial1 and trial2:
                similarity = compare_trials(trial1, trial2)
                st.metric("Similarity Score", f"{similarity:.2%}")
                
                # Display trial cards
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Trial 1")
                    st.markdown(format_trial_card(trial1), unsafe_allow_html=True)
                with col2:
                    st.markdown("#### Trial 2")
                    st.markdown(format_trial_card(trial2), unsafe_allow_html=True)
        else:
            st.info("Save some trials from chat to compare them here!")

if __name__ == "__main__":
    main()


