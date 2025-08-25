import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Set environment for cloud deployment
os.environ["DEPLOYMENT_ENV"] = "cloud"

# Import and run the main app
try:
    from src.app import main
    main()
except ImportError:
    st.error("Unable to import the main application. Please check the requirements.")
except Exception as e:
    st.error(f"Error running the application: {str(e)}")
    st.info("This might be a temporary issue. Please try refreshing the page.")