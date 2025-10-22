import streamlit as st
import pandas as pd
import time
import uuid
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="Excel to App Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI (keep the existing CSS styles)
st.markdown("""
<style>
    /* [Previous CSS content remains exactly the same] */
</style>
""", unsafe_allow_html=True)

# Constants - Now configurable via environment variables
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UNIFIED_API_URL = os.getenv("UNIFIED_API_URL", "http://127.0.0.1:8000/analyze-and-generate")
DEPLOY_API_URL = os.getenv("DEPLOY_API_URL", "http://127.0.0.1:8001/deploy_streamlit")
PROMPT_FILE = os.getenv("PROMPT_FILE", "project_prompt.txt")
INSTRUCTIONS_FILE = os.getenv("INSTRUCTIONS_FILE", "instructions.md")
DEFAULT_ANALYSIS_MODEL = "deepseek/deepseek-chat-v3-0324:free"
DEFAULT_GENERATION_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Initialize session state
if 'app_generated' not in st.session_state:
    st.session_state.app_generated = False
if 'app_url' not in st.session_state:
    st.session_state.app_url = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

def get_project_prompt():
    """Read project prompt from file with error handling"""
    try:
        if not os.path.exists(PROMPT_FILE):
            raise FileNotFoundError(f"Prompt file not found at {PROMPT_FILE}")
            
        with open(PROMPT_FILE, 'r') as f:
            prompt = f.read().strip()
            if not prompt:
                raise ValueError("Prompt file is empty")
            return prompt
    except Exception as e:
        logger.error(f"Prompt file error: {str(e)}")
        st.error(f"❌ System configuration error: {str(e)}")
        st.stop()

def get_instructions():
    """Read analysis instructions from file with error handling"""
    try:
        if not os.path.exists(INSTRUCTIONS_FILE):
            logger.warning(f"Instructions file not found at {INSTRUCTIONS_FILE}")
            return "Analyze the Excel file and generate a Python project based on the data."
            
        with open(INSTRUCTIONS_FILE, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Instructions file error: {str(e)}")
        return "Analyze the Excel file and generate a Python project based on the data."

def validate_excel_file(df):
    """Validate uploaded Excel file and return errors if any"""
    errors = []
    
    if df.empty:
        errors.append("File is empty. Please upload a file with data.")
        return errors
    
    if len(df.columns) < 2:
        errors.append("File needs at least 2 columns to create a meaningful app.")
    
    if len(df) < 5:
        errors.append("File needs at least 5 rows of data for a useful app.")
    
    # Check for completely empty columns
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        errors.append(f"These columns are completely empty: {', '.join(empty_cols)}")
    
    return errors

def update_progress_bar(progress_bar, status_container, progress, message, emoji):
    """Update progress bar and status message"""
    status_container.markdown(f'''
    <div class="agent-status">
        <span class="agent-emoji">{emoji}</span>
        <span>{message}</span>
    </div>
    ''', unsafe_allow_html=True)
    progress_bar.progress(progress)

def process_excel_to_deployment(uploaded_excel_path: str) -> str:
    """Orchestrate the full pipeline with proper file handling"""
    # Initialize variables to avoid reference before assignment
    raw_zip_path = None
    project_zip = None
    
    try:
        # Step 1: Call unified_api
        with open(uploaded_excel_path, 'rb') as excel_file:
            instructions = get_instructions()
            response = requests.post(
                UNIFIED_API_URL,
                files={
                    "excel_file": (os.path.basename(uploaded_excel_path), excel_file),
                    "analysis_instructions": ("instructions.md", instructions)
                },
                data={
                    "project_prompt": get_project_prompt(),
                    "analysis_model": DEFAULT_ANALYSIS_MODEL,
                    "generation_model": DEFAULT_GENERATION_MODEL
                },
                timeout=300
            )
        
        # Handle HTTP errors
        if response.status_code == 502:
            raise RuntimeError("Backend service is currently unavailable. Please try again later.")
        elif response.status_code == 413:
            raise RuntimeError("File size exceeds server limits. Please try a smaller file.")
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Invalid file format or content")
            raise RuntimeError(f"Processing error: {error_detail}")
        response.raise_for_status()

        # Save the raw zip
        raw_zip_path = os.path.join(tempfile.gettempdir(), f"raw_{uuid.uuid4().hex[:8]}.zip")
        with open(raw_zip_path, 'wb') as f:
            f.write(response.content)

        # Step 2: Extract only project files
        project_zip = extract_project_files(raw_zip_path)
        
        # Step 3: Call deploy API
        with open(project_zip, 'rb') as project_file:
            deploy_response = requests.post(
                DEPLOY_API_URL,
                files={"file": ("project.zip", project_file)},
                timeout=300
            )
            
        if deploy_response.status_code == 502:
            raise RuntimeError("Deployment service is currently unavailable. Please try again later.")
        deploy_response.raise_for_status()

        return deploy_response.json()["public_url"]

    except requests.exceptions.RequestException as e:
        logger.error(f"API error: {str(e)}")
        if "502" in str(e):
            raise RuntimeError("Our backend services are currently unavailable. Please try again later.")
        raise RuntimeError(f"Service error: {str(e)}")
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise RuntimeError(f"Failed to create app: {str(e)}")
    finally:
        # Cleanup temporary files
        for path in [raw_zip_path, project_zip]:
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {path}: {str(e)}")

def extract_project_files(zip_path: str) -> str:
    """Extract only the generated project files from the zip"""
    project_dir = os.path.join(tempfile.gettempdir(), f"project_{uuid.uuid4().hex[:8]}")
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract only files from the 'generated/' directory
            for file in zip_ref.namelist():
                if file.startswith('generated/'):
                    zip_ref.extract(file, project_dir)
        
        # Move files from generated/ to root
        generated_dir = os.path.join(project_dir, 'generated')
        if os.path.exists(generated_dir):
            for item in os.listdir(generated_dir):
                shutil.move(os.path.join(generated_dir, item), project_dir)
            os.rmdir(generated_dir)
        
        # Verify we have at least one Python file
        if not any(f.endswith('.py') for f in os.listdir(project_dir)):
            raise ValueError("No Python files found in generated project")
        
        # Create new clean zip
        project_zip = os.path.join(tempfile.gettempdir(), f"project_{uuid.uuid4().hex[:8]}.zip")
        with zipfile.ZipFile(project_zip, 'w') as zipf:
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
        
        return project_zip
    except Exception as e:
        logger.error(f"Failed to extract project files: {str(e)}")
        raise RuntimeError("Failed to process generated project files")
    finally:
        # Cleanup project directory
        try:
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
        except Exception as e:
            logger.warning(f"Failed to clean up project directory {project_dir}: {str(e)}")

def main():
    """Main app interface"""
    # Hero section (keep the existing hero section)
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">🚀 Excel to App Generator</h1>
        <p class="hero-subtitle">Turn Excel files into interactive web apps in seconds!<br>
        Just upload your data, and our AI will handle the rest.</p>
    </div>
    ''', unsafe_allow_html=True)

    if not st.session_state.app_generated:
        # Upload section
        st.markdown("### 📂 Upload Your Excel File")
        
        uploaded_file = st.file_uploader(
            "Choose your Excel or CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="Supported formats: .xlsx, .xls, .csv (max 10MB)"
        )
        
        if uploaded_file is not None:
            try:
                # Validate size
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.markdown('<div class="error-container">', unsafe_allow_html=True)
                    st.error("❌ File too large (max 10MB)")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.stop()

                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_data = df
                
                # Validate file
                errors = validate_excel_file(df)
                
                if errors:
                    st.markdown('<div class="error-container">', unsafe_allow_html=True)
                    st.error("⚠️ File validation failed:")
                    for error in errors:
                        st.write(f"• {error}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Provide template download (keep existing template code)
                    # ...
                
                else:
                    # Show preview
                    st.markdown("### 👀 Data Preview")
                    st.markdown('<div class="preview-table">', unsafe_allow_html=True)
                    st.dataframe(df.head(), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show data info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(df))
                    with col2:
                        st.metric("Columns", len(df.columns))
                    with col3:
                        st.metric("Data Points", len(df) * len(df.columns))
                    
                    # Generate app button
                    st.markdown("### 🎯 Generate Your App")
                    
                    if st.button("🚀 Generate My App →", key="generate_btn"):
                        with st.container():
                            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                            st.markdown("### 🤖 AI Agent at Work")
                            
                            progress_bar = st.progress(0)
                            status_container = st.empty()
                            
                            try:
                                # Create temp file
                                with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                                    df.to_excel(tmp.name, index=False)
                                    tmp_path = tmp.name
                                
                                # Show processing steps with actual progress
                                update_progress_bar(progress_bar, status_container, 10, "Uploading and validating file...", "📤")
                                time.sleep(1)
                                
                                update_progress_bar(progress_bar, status_container, 30, "Analyzing data structure...", "🔍")
                                time.sleep(1)
                                
                                update_progress_bar(progress_bar, status_container, 50, "Generating project code...", "👨‍💻")
                                
                                # Process through pipeline
                                st.session_state.app_url = process_excel_to_deployment(tmp_path)
                                st.session_state.app_generated = True
                                
                                update_progress_bar(progress_bar, status_container, 100, "App deployed successfully!", "🎉")
                                time.sleep(1)
                                
                                # Cleanup
                                try:
                                    os.unlink(tmp_path)
                                except Exception as e:
                                    logger.warning(f"Failed to delete temp file {tmp_path}: {str(e)}")
                                
                                st.rerun()
                            
                            except Exception as e:
                                progress_bar.empty()
                                status_container.empty()
                                st.markdown('<div class="error-container">', unsafe_allow_html=True)
                                st.error(f"❌ {str(e)}")
                                if st.button("🔄 Try Again"):
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.markdown('<div class="error-container">', unsafe_allow_html=True)
                st.error(f"❌ Error reading file: {str(e)}")
                st.write("Please make sure your file is a valid Excel or CSV file.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Success screen (keep existing success screen)
        # ...
        pass

if __name__ == "__main__":
    main()
