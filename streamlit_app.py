import streamlit as st
import requests
import os

# Configure page
st.set_page_config(
    page_title="Business Plan Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment or use default
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Check if backend is running
@st.cache_resource
def check_backend():
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

# Main UI
st.title("🏢 Business Plan Studio")
st.markdown("Professional business planning and financial projections")

# Check connection
backend_available = check_backend()

if backend_available:
    st.success("✅ Connected to backend")
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "Projects", "API Documentation"])
    
    if page == "Dashboard":
        st.header("Dashboard")
        st.info("Welcome to Business Plan Studio!")
        
        try:
            response = requests.get(f"{API_URL}/api/projects")
            if response.status_code == 200:
                projects = response.json()
                st.metric("Total Projects", len(projects))
                if projects:
                    st.subheader("Recent Projects")
                    for project in projects[:5]:
                        st.write(f"📋 {project.get('name', 'Unnamed Project')}")
        except Exception as e:
            st.warning(f"Could not fetch projects: {str(e)}")
    
    elif page == "Projects":
        st.header("Projects")
        try:
            response = requests.get(f"{API_URL}/api/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    st.json(projects)
                else:
                    st.info("No projects found. Create a new one to get started!")
        except Exception as e:
            st.error(f"Error loading projects: {str(e)}")
    
    elif page == "API Documentation":
        st.header("API Documentation")
        st.write(f"Backend URL: `{API_URL}`")
        st.write(f"API Docs: [{API_URL}/docs]({API_URL}/docs)")
        st.write(f"Health Check: `{API_URL}/health`")

else:
    st.error("❌ Cannot connect to backend")
    st.warning(f"Tried to connect to: `{API_URL}`")
    st.info("""
    **To run locally:**
    1. Start the backend: `cd backend && python -m uvicorn app.main:app --reload`
    2. The Streamlit app will connect automatically
    
    **For cloud deployment:**
    Set the `API_URL` environment variable to your backend URL
    """)
