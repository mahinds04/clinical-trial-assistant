import streamlit as st
import pandas as pd
from src.rag.assistant import ClinicalTrialAssistant
from datetime import datetime

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
    return ClinicalTrialAssistant()

def format_trial_card(trial):
    """Format trial information as a card with metadata badges."""
    return f"""
    <div class="trial-card">
        <h4>{trial['brief_title']}</h4>
        <p>
            <span class="metadata-badge">Phase: {trial['phase']}</span>
            <span class="metadata-badge">Status: {trial['status']}</span>
            <span class="metadata-badge">Purpose: {trial['purpose']}</span>
        </p>
        <p><small>Start Date: {trial['start_date']}</small></p>
    </div>
    """

def display_trial_filters(trials):
    """Display and handle trial filtering options."""
    if not trials:
        return trials
    
    col1, col2 = st.columns(2)
    with col1:
        phases = list(set(t['phase'] for t in trials if t['phase']))
        selected_phase = st.multiselect("Filter by Phase", phases)
    
    with col2:
        statuses = list(set(t['status'] for t in trials if t['status']))
        selected_status = st.multiselect("Filter by Status", statuses)
    
    filtered_trials = trials
    if selected_phase:
        filtered_trials = [t for t in filtered_trials if t['phase'] in selected_phase]
    if selected_status:
        filtered_trials = [t for t in filtered_trials if t['status'] in selected_status]
    
    return filtered_trials

import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json

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
        st.session_state.view_mode = "chat"
    if "selected_trials_for_comparison" not in st.session_state:
        st.session_state.selected_trials_for_comparison = []
    if "location_filter" not in st.session_state:
        st.session_state.location_filter = None

def create_trial_visualizations(trials):
    """Create visualizations from trial data."""
    if not trials:
        return
    
    # Convert trials list to DataFrame
    df = pd.DataFrame(trials)
    
    # Phase Distribution
    st.subheader("Trial Phases Distribution")
    phase_counts = df['phase'].value_counts()
    st.bar_chart(phase_counts)
    
    # Status Distribution
    st.subheader("Trial Status Distribution")
    status_counts = df['status'].value_counts()
    st.bar_chart(status_counts)

def create_map_visualization(trials):
    """Create a map visualization of trial locations."""
    # Create a map centered on the US
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    
    # Add markers for each trial location
    for trial in trials:
        if 'location' in trial and trial['location']:
            folium.Marker(
                location=[trial['location']['lat'], trial['location']['lon']],
                popup=trial['brief_title'],
                tooltip=trial['brief_title']
            ).add_to(m)
    
    # Display the map
    folium_static(m)

def apply_advanced_filters(trials, filters):
    """Apply advanced filtering to trials."""
    filtered_trials = trials.copy()
    
    if filters.get('date_range'):
        start_date, end_date = filters['date_range']
        filtered_trials = [t for t in filtered_trials 
                         if start_date <= pd.to_datetime(t['start_date']) <= end_date]
    
    if filters.get('conditions'):
        filtered_trials = [t for t in filtered_trials 
                         if any(c.lower() in t['condition'].lower() for c in filters['conditions'])]
    
    if filters.get('location'):
        # Add location-based filtering logic
        pass
    
    if filters.get('participant_criteria'):
        # Add participant criteria filtering logic
        pass
    
    return filtered_trials

def compare_trials(trial1, trial2):
    """Compare two trials and return similarity score."""
    # Create TF-IDF vectors for comparison
    vectorizer = TfidfVectorizer()
    
    # Combine relevant fields for comparison
    def get_trial_text(trial):
        return f"{trial['brief_title']} {trial['condition']} {trial.get('purpose', '')}"
    
    texts = [get_trial_text(trial1), get_trial_text(trial2)]
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Calculate similarity score
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return similarity

def get_similar_trials(target_trial, all_trials, n=5):
    """Find similar trials based on content similarity."""
    similarities = []
    for trial in all_trials:
        if trial != target_trial:
            similarity = compare_trials(target_trial, trial)
            similarities.append((trial, similarity))
    
    # Sort by similarity and return top N
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:n]

def manage_saved_searches():
    """Manage saved searches interface."""
    st.subheader("Saved Searches")
    
    # Add new search
    new_search = st.text_input("Save current search")
    if st.button("Save Search") and new_search:
        st.session_state.saved_searches.append({
            'query': new_search,
            'timestamp': datetime.now().isoformat()
        })
    
    # Display saved searches
    for search in st.session_state.saved_searches:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"🔍 {search['query']}")
        with col2:
            if st.button("Run", key=f"run_{search['query']}"):
                return search['query']
    
    return None

def manage_custom_alerts():
    """Manage custom trial alerts."""
    st.subheader("Custom Alerts")
    
    # Add new alert
    col1, col2 = st.columns(2)
    with col1:
        condition = st.text_input("Condition of interest")
    with col2:
        frequency = st.selectbox("Alert frequency", ["Daily", "Weekly", "Monthly"])
    
    if st.button("Set Alert") and condition:
        st.session_state.custom_alerts.append({
            'condition': condition,
            'frequency': frequency,
            'created_at': datetime.now().isoformat()
        })
    
    # Display active alerts
    for alert in st.session_state.custom_alerts:
        with st.expander(f"Alert for {alert['condition']}"):
            st.write(f"Frequency: {alert['frequency']}")
            if st.button("Remove Alert", key=f"remove_{alert['condition']}"):
                st.session_state.custom_alerts.remove(alert)

def export_trials(trials):
    """Export trials to CSV."""
    if not trials:
        return
    
    df = pd.DataFrame(trials)
    csv = df.to_csv(index=False)
    st.download_button(
        label="Export Trials to CSV",
        data=csv,
        file_name="clinical_trials.csv",
        mime="text/csv"
    )

def main():
    initialize_session_state()
    
    # Theme Toggle and View Mode Selection
    with st.sidebar:
        if st.button("🌓 Toggle Theme"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        
        st.session_state.view_mode = st.radio(
            "View Mode",
            ["Chat", "Analysis Dashboard", "Trial Comparison", "Personal Dashboard"],
            key="view_mode_radio"
        )
        
        # Advanced Filters
        st.markdown("### Advanced Filters")
        with st.expander("Date Range"):
            date_range = st.date_input(
                "Select Date Range",
                value=(datetime.now() - timedelta(days=365), datetime.now())
            )
        
        with st.expander("Location"):
            location = st.text_input("Enter Location")
            radius = st.slider("Search Radius (miles)", 10, 500, 100)
        
        with st.expander("Conditions"):
            conditions = st.multiselect(
                "Select Conditions",
                ["Cancer", "Diabetes", "Heart Disease", "COVID-19", "Rare Diseases"]
            )
        
        with st.expander("Participant Criteria"):
            min_age = st.number_input("Minimum Age", 0, 100, 18)
            max_age = st.number_input("Maximum Age", 0, 100, 65)
            gender = st.selectbox("Gender", ["Any", "Male", "Female"])
    
    st.title("🏥 Clinical Trial Query Assistant")
    
    if st.session_state.view_mode == "Trial Comparison":
        st.markdown("### Trial Comparison Tool")
        
        # Trial selection for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Trial 1")
            if st.session_state.saved_trials:
                trial1 = st.selectbox(
                    "Select First Trial",
                    st.session_state.saved_trials,
                    format_func=lambda x: x['brief_title']
                )
                st.markdown(format_trial_card(trial1), unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Trial 2")
            if st.session_state.saved_trials:
                trial2 = st.selectbox(
                    "Select Second Trial",
                    [t for t in st.session_state.saved_trials if t != trial1],
                    format_func=lambda x: x['brief_title']
                )
                st.markdown(format_trial_card(trial2), unsafe_allow_html=True)
        
        if trial1 and trial2:
            similarity = compare_trials(trial1, trial2)
            st.metric("Similarity Score", f"{similarity:.2%}")
            
            # Compare specific attributes
            st.markdown("### Detailed Comparison")
            comparison_df = pd.DataFrame({
                'Attribute': ['Phase', 'Status', 'Purpose', 'Start Date'],
                'Trial 1': [trial1['phase'], trial1['status'], 
                           trial1.get('purpose', 'N/A'), trial1['start_date']],
                'Trial 2': [trial2['phase'], trial2['status'], 
                           trial2.get('purpose', 'N/A'), trial2['start_date']]
            })
            st.table(comparison_df)
            
            # Find similar trials
            st.markdown("### Similar Trials")
            similar_trials = get_similar_trials(trial1, st.session_state.saved_trials)
            for trial, score in similar_trials:
                with st.expander(f"{trial['brief_title']} (Similarity: {score:.2%})"):
                    st.markdown(format_trial_card(trial), unsafe_allow_html=True)
    
    elif st.session_state.view_mode == "Personal Dashboard":
        st.markdown("### Personal Dashboard")
        
        tabs = st.tabs(["Saved Searches", "Custom Alerts", "Recommendations"])
        
        with tabs[0]:
            saved_search = manage_saved_searches()
            if saved_search:
                st.session_state.messages.append({"role": "user", "content": saved_search})
        
        with tabs[1]:
            manage_custom_alerts()
        
        with tabs[2]:
            st.markdown("### Personalized Recommendations")
            # Generate recommendations based on past searches and saved trials
            if st.session_state.saved_trials:
                recent_trial = st.session_state.saved_trials[-1]
                similar_trials = get_similar_trials(recent_trial, 
                                                 st.session_state.saved_trials)
                for trial, score in similar_trials:
                    with st.expander(f"{trial['brief_title']} (Match: {score:.2%})"):
                        st.markdown(format_trial_card(trial), unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox("Select Model", ["llama2", "mistral", "codellama"])
        n_results = st.slider("Number of relevant trials", 1, 10, 3)
        
        st.markdown("---")
        st.markdown("### Quick Prompts")
        example_prompts = [
            "What phase 3 trials are available for breast cancer?",
            "Show me pediatric trials for rare diseases",
            "Are there any ongoing COVID-19 vaccine trials?",
            "What trials are available for type 2 diabetes?",
        ]
        for prompt in example_prompts:
            if st.button(prompt):
                st.session_state.messages.append({"role": "user", "content": prompt})
        
        st.markdown("---")
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.experimental_rerun()
    
    # Initialize assistant
    assistant = get_assistant()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
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
                with st.spinner("Searching trials..."):
                    response = assistant.query(prompt, n_results=n_results)
                st.markdown(response["answer"])
                
                trials = response["sources"]
                filtered_trials = display_trial_filters(trials)
                
                for trial in filtered_trials:
                    st.markdown(format_trial_card(trial), unsafe_allow_html=True)
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            })
    
    # Info column
    with info_col:
        if st.session_state.view_mode == "Chat":
            st.markdown("### About")
            st.markdown("""
            This assistant helps you explore clinical trials using natural language queries. 
            It uses RAG (Retrieval Augmented Generation) with a local Ollama model.
            
            **Features:**
            - 🔍 Natural language search
            - 📊 Filter trials by phase and status
            - 💾 Local and private processing
            - 🤖 Powered by Ollama
            """)
            
            # Add stats
            st.markdown("### Session Stats")
            if st.session_state.messages:
                n_queries = len([m for m in st.session_state.messages if m["role"] == "user"])
                n_trials = sum(len(m.get("sources", [])) for m in st.session_state.messages if m["role"] == "assistant")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries Made", n_queries)
                with col2:
                    st.metric("Trials Explored", n_trials)
            
            # Saved Trials
            st.markdown("### Saved Trials")
            if st.session_state.saved_trials:
                for trial in st.session_state.saved_trials:
                    with st.expander(trial['brief_title']):
                        st.markdown(format_trial_card(trial), unsafe_allow_html=True)
                        if st.button("Remove", key=f"remove_{trial['brief_title']}"):
                            st.session_state.saved_trials.remove(trial)
                            st.experimental_rerun()
                
                # Export functionality
                export_trials(st.session_state.saved_trials)
        
        else:  # Analysis Dashboard
            st.markdown("### Trial Analysis Dashboard")
            
            # Get all trials from chat history
            all_trials = []
            for message in st.session_state.messages:
                if message["role"] == "assistant" and "sources" in message:
                    all_trials.extend(message["sources"])
            
            if all_trials:
                # Create visualizations
                create_trial_visualizations(all_trials)
                
                # Trial Statistics
                st.markdown("### Trial Statistics")
                df = pd.DataFrame(all_trials)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Trials", len(df))
                    st.metric("Active Trials", len(df[df['status'] == 'Recruiting']))
                
                with col2:
                    if 'start_date' in df.columns:
                        recent_trials = df[df['start_date'].notna()].sort_values('start_date', ascending=False)
                        if not recent_trials.empty:
                            st.metric("Most Recent Trial", recent_trials.iloc[0]['start_date'])
                
                # Export functionality
                export_trials(all_trials)
            else:
                st.info("Start chatting to see trial analysis!")

if __name__ == "__main__":
    main()
