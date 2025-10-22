"""
Enhanced Frontend for Excel-to-Web Application Generator

This module provides an improved user interface with better UX,
real-time processing feedback, and deployment management.
"""

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
import json
from typing import Optional, Dict, Any

from unified_processor import UnifiedProcessor, ProcessingResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedFrontend:
    """Enhanced frontend with improved UX and real-time feedback"""
    
    def __init__(self):
        self.processor = UnifiedProcessor()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'processing_result' not in st.session_state:
            st.session_state.processing_result = None
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'current_deployment' not in st.session_state:
            st.session_state.current_deployment = None
        if 'deployment_history' not in st.session_state:
            st.session_state.deployment_history = []
    
    def render_hero_section(self):
        """Render hero section with improved design"""
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; margin-bottom: 2rem;">
            <h1 style="color: white; font-size: 3rem; margin-bottom: 1rem;">🚀 Excel-to-Web Generator</h1>
            <p style="color: white; font-size: 1.5rem; margin-bottom: 2rem;">
                Transform Excel files into interactive web apps instantly!
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; color: white;">
                    📊 Charts & Graphs
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; color: white;">
                    🔢 Formulas & Calculations
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; color: white;">
                    🎨 Interactive Dashboards
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; color: white;">
                    ⚡ Instant Deployment
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_upload_section(self):
        """Render file upload section with enhanced validation"""
        st.markdown("### 📂 Upload Your Excel File")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose your Excel file",
                type=['xlsx', 'xls', 'xlsm'],
                help="Supported formats: .xlsx, .xls, .xlsm (max 10MB)",
                key="file_uploader"
            )
        
        with col2:
            template_type = st.selectbox(
                "App Template",
                ["Streamlit Dashboard", "FastAPI Backend"],
                help="Choose the type of web application to generate"
            )
        
        if uploaded_file is not None:
            return self._handle_file_upload(uploaded_file, template_type)
        
        return None
    
    def _handle_file_upload(self, uploaded_file, template_type: str):
        """Handle file upload and validation"""
        try:
            # Validate file size
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error("❌ File too large (max 10MB)")
                return None
            
            # Read and validate file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.uploaded_data = df
            
            # Show file analysis
            self._render_file_analysis(df, uploaded_file.name)
            
            return {
                'file': uploaded_file,
                'template_type': 'streamlit' if 'Streamlit' in template_type else 'fastapi',
                'dataframe': df
            }
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.write("Please make sure your file is a valid Excel file.")
            return None
    
    def _render_file_analysis(self, df: pd.DataFrame, filename: str):
        """Render file analysis information"""
        st.markdown("### 📊 File Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filename", filename)
        with col2:
            st.metric("Rows", len(df))
        with col3:
            st.metric("Columns", len(df.columns))
        with col4:
            st.metric("Data Points", len(df) * len(df.columns))
        
        # Show data preview
        st.markdown("#### 👀 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Show column information
        st.markdown("#### 📋 Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum()
        })
        st.dataframe(col_info, use_container_width=True)
    
    def render_generation_section(self, file_info: Dict[str, Any]):
        """Render app generation section with progress tracking"""
        st.markdown("### 🎯 Generate Your Web App")
        
        if st.button("🚀 Generate & Deploy App", key="generate_btn", use_container_width=True):
            with st.spinner("Processing your Excel file..."):
                return self._process_excel_file(file_info)
        
        return None
    
    def _process_excel_file(self, file_info: Dict[str, Any]) -> ProcessingResult:
        """Process Excel file through the unified pipeline"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            file_info['dataframe'].to_excel(tmp.name, index=False)
            tmp_path = tmp.name
        
        try:
            # Process through unified pipeline
            result = self.processor.process_excel_to_web(
                Path(tmp_path),
                file_info['template_type'],
                f"app-{uuid.uuid4().hex[:8]}"
            )
            
            st.session_state.processing_result = result
            
            if result.success:
                st.session_state.current_deployment = result.deployment_info
                st.session_state.deployment_history.append(result.deployment_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                deployment_info=None,
                analysis_result=None,
                generated_files=[],
                error_message=str(e),
                processing_time=0
            )
        finally:
            # Cleanup temporary file
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")
    
    def render_results_section(self, result: ProcessingResult):
        """Render processing results"""
        if result.success:
            self._render_success_section(result)
        else:
            self._render_error_section(result)
    
    def _render_success_section(self, result: ProcessingResult):
        """Render success section with deployment information"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%); padding: 2rem; border-radius: 1rem; text-align: center; color: white;">
            <h1 style="color: white; margin-bottom: 1rem;">🎉 Success!</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Your Excel file has been transformed into a web application!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Deployment information
        deployment = result.deployment_info
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 App Information")
            st.metric("Processing Time", f"{result.processing_time:.2f}s")
            st.metric("Generated Files", len(result.generated_files))
            st.metric("Deployment Status", "Running")
        
        with col2:
            st.markdown("#### 🔗 Access Your App")
            st.markdown(f"**Public URL:** [{deployment.public_url}]({deployment.public_url})")
            st.markdown(f"**Deployment ID:** `{deployment.deployment_id}`")
            st.markdown(f"**Created:** {deployment.created_at}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌐 Open App", use_container_width=True):
                st.markdown(f"<meta http-equiv='refresh' content='0;url={deployment.public_url}'>", unsafe_allow_html=True)
        
        with col2:
            if st.button("📋 View Logs", use_container_width=True):
                self._show_application_logs(deployment.deployment_id)
        
        with col3:
            if st.button("🔄 New App", use_container_width=True):
                st.session_state.processing_result = None
                st.session_state.uploaded_data = None
                st.rerun()
        
        # Analysis insights
        if result.analysis_result:
            self._render_analysis_insights(result.analysis_result)
    
    def _render_error_section(self, result: ProcessingResult):
        """Render error section"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 2rem; border-radius: 1rem; text-align: center; color: white;">
            <h1 style="color: white; margin-bottom: 1rem;">❌ Processing Failed</h1>
            <p style="font-size: 1.2rem;">We encountered an issue while processing your file.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.error(f"Error: {result.error_message}")
        
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.processing_result = None
            st.rerun()
    
    def _show_application_logs(self, deployment_id: str):
        """Show application logs"""
        logs = self.processor.get_application_logs(deployment_id)
        if logs:
            st.markdown("#### 📝 Application Logs")
            st.text_area("Logs", logs, height=300)
        else:
            st.warning("No logs available for this deployment.")
    
    def _render_analysis_insights(self, analysis_result: Dict[str, Any]):
        """Render analysis insights from Excel file"""
        st.markdown("#### 🔍 Analysis Insights")
        
        # Template detection
        template_info = analysis_result.get("template_type", {})
        if template_info.get("confidence", 0) > 0.5:
            st.success(f"📋 Detected template: **{template_info.get('name', 'Unknown')}** (confidence: {template_info.get('confidence', 0):.1%})")
        
        # Formula analysis
        formulas = analysis_result.get("formulas", [])
        if formulas:
            formula_categories = {}
            for formula in formulas:
                category = getattr(formula, 'category', 'unknown')
                formula_categories[category] = formula_categories.get(category, 0) + 1
            
            st.info(f"🔢 Found **{len(formulas)}** formulas across **{len(formula_categories)}** categories")
        
        # Chart analysis
        charts = analysis_result.get("charts", [])
        if charts:
            st.info(f"📊 Found **{len(charts)}** charts that will be recreated in your web app")
    
    def render_deployment_management(self):
        """Render deployment management section"""
        st.markdown("### 🏗️ Deployment Management")
        
        deployments = self.processor.list_deployments()
        
        if not deployments:
            st.info("No active deployments. Upload an Excel file to create your first web app!")
            return
        
        for deployment in deployments:
            with st.expander(f"App: {deployment.get('public_url', 'Unknown')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Status:** {deployment.get('status', 'Unknown')}")
                    st.markdown(f"**URL:** [{deployment.get('public_url', 'N/A')}]({deployment.get('public_url', '')})")
                    st.markdown(f"**Container:** {deployment.get('container_id', 'N/A')[:12]}...")
                
                with col2:
                    if st.button("Stop", key=f"stop_{deployment.get('deployment_id')}"):
                        if self.processor.undeploy_application(deployment.get('deployment_id')):
                            st.success("App stopped successfully")
                            st.rerun()
    
    def render_footer(self):
        """Render footer with system information"""
        st.markdown("---")
        
        system_info = self.processor.get_system_info()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📈 System Status")
            st.metric("Active Deployments", system_info["active_deployments"])
            st.metric("System Status", system_info["status"])
        
        with col2:
            st.markdown("#### 🛠️ Components")
            for component, status in system_info["components"].items():
                st.write(f"- {component.title()}: **{status}**")
        
        with col3:
            st.markdown("#### 📋 Supported Features")
            st.write("- Excel formula translation")
            st.write("- Chart recreation")
            st.write("- Interactive dashboards")
            st.write("- Instant deployment")
    
    def run(self):
        """Run the enhanced frontend"""
        # Configure page
        st.set_page_config(
            page_title="Excel-to-Web Generator",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .success-box {
                background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
                padding: 2rem;
                border-radius: 1rem;
                text-align: center;
                color: white;
            }
            .error-box {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                padding: 2rem;
                border-radius: 1rem;
                text-align: center;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Render application
        self.render_hero_section()
        
        # Check if we have a processing result
        if st.session_state.processing_result:
            self.render_results_section(st.session_state.processing_result)
        else:
            # Show upload and generation sections
            file_info = self.render_upload_section()
            if file_info:
                result = self.render_generation_section(file_info)
                if result:
                    self.render_results_section(result)
        
        # Show deployment management
        self.render_deployment_management()
        
        # Show footer
        self.render_footer()

def main():
    """Main function to run the enhanced frontend"""
    frontend = EnhancedFrontend()
    frontend.run()

if __name__ == "__main__":
    main()