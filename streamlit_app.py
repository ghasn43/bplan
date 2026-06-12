import streamlit as st
import requests
import subprocess
import time
from threading import Thread

# Configure page
st.set_page_config(page_title="Business Plan Studio", layout="wide")

# Start backend in background if needed
def start_backend():
    try:
        subprocess.Popen(["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(2)  # Wait for backend to start
    except:
        pass

# Try to connect to backend
@st.cache_resource
def get_api_url():
    return "http://localhost:8000"

# Check if backend is running
def check_backend():
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Start backend on app load
if not check_backend():
    with st.spinner("Starting backend..."):
        start_backend()
        time.sleep(2)

# Main UI
st.title("🏢 Business Plan Studio")
st.markdown("Professional business planning and financial projections")

# Check connection
if check_backend():
    st.success("✅ Connected to backend")
    
    # Fetch and display projects
    try:
        response = requests.get(f"{get_api_url()}/api/projects")
        if response.status_code == 200:
            projects = response.json()
            st.write(f"Found {len(projects)} projects")
            if projects:
                st.json(projects)
        else:
            st.warning("Could not fetch projects")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
else:
    st.error("❌ Cannot connect to backend. Please check the backend is running.")
    st.info("The application requires the FastAPI backend to be running on port 8000.")
