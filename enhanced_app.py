"""
Enhanced Excel to Web App Converter
Guaranteed 100% Success Rate with Multi-Layer Fallback System
"""

import streamlit as st
import pandas as pd
import io
import zipfile
import tempfile
import os
from pathlib import Path
import time

from enhanced_excel_transformer import EnhancedExcelTransformer

# Configure page
st.set_page_config(
    page_title="Enhanced Excel to App - 100% Success",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    .provider-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
    }
    .confidence-meter {
        height: 10px;
        background: #e9ecef;
        border-radius: 5px;
        margin: 10px 0;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #28a745, #20c997);
        border-radius: 5px;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app_generated' not in st.session_state:
    st.session_state.app_generated = False
if 'project_zip' not in st.session_state:
    st.session_state.project_zip = None
if 'transformation_result' not in st.session_state:
    st.session_state.transformation_result = None

def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🚀 Enhanced Excel to Web App Converter")
    st.subheader("100% Success Rate - Multi-Layer Fallback System")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info box
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 💡 Enhanced Architecture Features:
    - **Comprehensive Excel Analysis**: Deep analysis of formulas, charts, and business logic
    - **Multi-Provider LLM Orchestration**: OpenRouter → Local LLM → Templates → Universal Fallback
    - **Enhanced Validation**: Syntax, imports, functionality, and security checks
    - **Guaranteed Success**: 4-layer fallback system ensures 100% transformation rate
    - **Business Logic Preservation**: Maintains original Excel calculations and workflows
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.app_generated:
        # File upload section
        st.markdown("### 📤 Upload Your Excel File")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose Excel or CSV file",
                type=['xlsx', 'xls', 'csv'],
                help="Supported formats: .xlsx, .xls, .csv (max 50MB)"
            )
        
        with col2:
            st.markdown("### 📋 Instructions")
            custom_instructions = st.text_area(
                "Custom instructions (optional)",
                placeholder="E.g., 'Focus on sales data visualization' or 'Include specific calculations...'",
                height=100
            )
            
            # Model configuration
            st.markdown("### 🤖 Model Configuration")
            
            # Provider selection
            provider_options = ["OpenRouter", "DeepSeek", "Template Engine", "Universal Fallback"]
            selected_provider = st.selectbox(
                "Primary Provider",
                provider_options,
                index=0,
                help="Select which LLM provider to use first"
            )
            
            # Model selection
            model_options = [
                "deepseek/deepseek-chat-v3-0324:free",
                "deepseek/deepseek-chat",
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
                "anthropic/claude-3-sonnet",
                "google/gemini-pro"
            ]
            
            analysis_model = st.selectbox(
                "Analysis Model",
                model_options,
                index=0,
                help="Model used for Excel analysis"
            )
            
            generation_model = st.selectbox(
                "Generation Model", 
                model_options,
                index=0,
                help="Model used for code generation"
            )
        
        if uploaded_file is not None:
            # Show file info
            file_size = len(uploaded_file.getvalue()) / 1024 / 1024
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({file_size:.2f} MB)")
            
            # Show quick preview
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_preview = pd.read_csv(uploaded_file)
                else:
                    df_preview = pd.read_excel(uploaded_file)
                
                st.markdown("### 👀 Quick Data Preview")
                st.dataframe(df_preview.head(), use_container_width=True)
                
                # Reset file pointer for processing
                uploaded_file.seek(0)
                
            except Exception as e:
                st.warning(f"⚠️ Quick preview failed: {e}")
            
            # Generate app button
            st.markdown("### 🎯 Generate Your Enhanced App")
            
            if st.button("🚀 Generate Enhanced Web App", type="primary", use_container_width=True):
                with st.spinner("🔄 Starting enhanced transformation process..."):
                    
                    # Show progress steps
                    progress_container = st.container()
                    
                    with progress_container:
                        st.markdown("#### 🔄 Transformation Progress")
                        
                        # Step 1: Analysis
                        step1 = st.empty()
                        step1.markdown("📊 **Step 1**: Comprehensive Excel Analysis...")
                        time.sleep(1)
                        
                        # Initialize transformer with selected models
                        transformer = EnhancedExcelTransformer(
                            analysis_model=analysis_model,
                            generation_model=generation_model
                        )
                        
                        # Set provider priority based on selection
                        provider_map = {
                            "OpenRouter": "openrouter",
                            "DeepSeek": "deepseek", 
                            "Template Engine": "template_engine",
                            "Universal Fallback": "universal_fallback"
                        }
                        primary_provider = provider_map[selected_provider]
                        
                        # Set environment variable for provider priority
                        os.environ["PROVIDER_PRIORITY"] = f"{primary_provider},template_engine,universal_fallback"
                        
                        # Step 2: Multi-provider generation
                        step2 = st.empty()
                        step2.markdown(f"🤖 **Step 2**: Multi-Provider LLM Generation ({selected_provider})...")
                        time.sleep(1)
                        
                        # Perform transformation
                        result = transformer.transform_excel_to_app(
                            uploaded_file.getvalue(),
                            uploaded_file.name,
                            custom_instructions,
                            analysis_model,
                            generation_model
                        )
                        
                        # Step 3: Validation
                        step3 = st.empty()
                        step3.markdown("✅ **Step 3**: Enhanced Validation...")
                        time.sleep(1)
                        
                        # Step 4: Project creation
                        step4 = st.empty()
                        step4.markdown("📦 **Step 4**: Creating Complete Project...")
                        time.sleep(1)
                        
                        # Store results
                        st.session_state.transformation_result = result
                        st.session_state.project_zip = result['project_zip']
                        st.session_state.app_generated = True
                        
                        st.rerun()
    
    else:
        # Success screen
        result = st.session_state.transformation_result
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success("🎉 Your enhanced web app has been generated successfully!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show transformation details
        st.markdown("### 📊 Transformation Details")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Provider Used", result['provider_used'].replace('_', ' ').title())
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            confidence = result['confidence_score']
            st.metric("Confidence Score", f"{confidence:.0%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            analysis = result['analysis']
            st.metric("Total Sheets", analysis['file_info']['sheet_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Complexity", analysis['analysis_summary']['overall_complexity'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show analysis summary
        st.markdown("### 🔍 Analysis Summary")
        
        analysis_summary = result['analysis']['analysis_summary']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Key Findings")
            for finding in analysis_summary.get('key_findings', []):
                st.write(f"• {finding}")
        
        with col2:
            st.markdown("#### 💡 Recommendations")
            for recommendation in analysis_summary.get('recommendations', []):
                st.write(f"• {recommendation}")
        
        # Show business logic
        business_logic = result['analysis'].get('business_logic', {})
        if business_logic:
            st.markdown("### 🏢 Business Logic Detected")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Domain", business_logic.get('domain', 'General'))
            
            with col2:
                st.metric("Key Operations", len(business_logic.get('key_operations', [])))
            
            with col3:
                st.metric("Business Rules", len(business_logic.get('business_rules', [])))
        
        # Show validation results
        validation = result['validation_result']
        st.markdown("### ✅ Validation Results")
        
        validation_cols = st.columns(5)
        checks = [
            ("Syntax", validation['syntax_check']),
            ("Imports", validation['imports_check']),
            ("Streamlit", validation['streamlit_check']),
            ("Functionality", validation['functionality_check']),
            ("Security", validation['security_check'])
        ]
        
        for i, (name, passed) in enumerate(checks):
            with validation_cols[i]:
                emoji = "✅" if passed else "❌"
                st.metric(f"{name} Check", emoji)
        
        # Download section
        st.markdown("### 📱 Download Your Enhanced App")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            #### 🎯 What's Included:
            - **app.py** - Complete Streamlit application with enhanced features
            - **requirements.txt** - All dependencies
            - **README.md** - Comprehensive setup instructions
            - **analysis_report.md** - Detailed Excel analysis
            - **DEPLOYMENT.md** - Deployment guide
            
            #### 🚀 How to Run:
            1. Download the project below
            2. Extract the ZIP file
            3. Install dependencies: `pip install -r requirements.txt`
            4. Run the app: `streamlit run app.py`
            
            #### ✨ Enhanced Features:
            - Multi-sheet data exploration with business logic preservation
            - Interactive data tables and advanced visualizations
            - Statistical analysis and calculations
            - Data export capabilities
            - Modern, responsive UI with enhanced UX
            """)
        
        with col2:
            # Download button
            st.download_button(
                label="📥 Download Enhanced Project",
                data=st.session_state.project_zip,
                file_name="enhanced_excel_app_project.zip",
                mime="application/zip",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Reset button
            if st.button("🔄 Generate Another App", use_container_width=True):
                st.session_state.app_generated = False
                st.session_state.project_zip = None
                st.session_state.transformation_result = None
                st.rerun()

if __name__ == "__main__":
    main()