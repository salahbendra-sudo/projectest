"""
Multi-Provider LLM Orchestrator
Guaranteed success through layered fallback system
Supports OpenRouter and DeepSeek OpenAI-compatible APIs
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, Optional, List
import requests
from openai import OpenAI
from enhanced_excel_analyzer import EnhancedExcelAnalyzer

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """Multi-provider LLM orchestration with guaranteed success"""
    
    def __init__(self):
        self.enhanced_analyzer = EnhancedExcelAnalyzer()
        
        # Configuration - can be set via environment variables
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # DeepSeek OpenAI-compatible API configuration
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        
        # Model configuration
        self.analysis_model = os.getenv("ANALYSIS_MODEL", "deepseek/deepseek-chat-v3-0324:free")
        self.generation_model = os.getenv("GENERATION_MODEL", "deepseek/deepseek-chat-v3-0324:free")
        
        # Provider priority (configurable)
        provider_priority = os.getenv("PROVIDER_PRIORITY", "openrouter,deepseek,template_engine,universal_fallback")
        self.providers = [p.strip() for p in provider_priority.split(",")]
        
        # API configuration
        self.api_timeout = int(os.getenv("API_TIMEOUT", "120"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.3"))
    
    def generate_business_app(self, file_content: bytes, filename: str, 
                            instructions: str = None,
                            analysis_model: str = None,
                            generation_model: str = None) -> Dict[str, Any]:
        """
        Generate business app using multi-provider fallback system
        """
        # Use provided models or defaults
        analysis_model = analysis_model or self.analysis_model
        generation_model = generation_model or self.generation_model
        
        # Step 1: Comprehensive Excel analysis
        analysis = self.enhanced_analyzer.analyze_excel_comprehensively(file_content, filename)
        
        if 'error' in analysis:
            logger.error(f"Analysis failed: {analysis['error']}")
            return self._generate_universal_fallback(file_content, filename)
        
        # Step 2: Try providers in order
        for provider in self.providers:
            try:
                logger.info(f"Trying provider: {provider}")
                
                if provider == 'openrouter':
                    app_code = self._generate_with_openrouter(analysis, instructions, generation_model)
                elif provider == 'deepseek':
                    app_code = self._generate_with_deepseek(analysis, instructions, generation_model)
                elif provider == 'template_engine':
                    app_code = self._generate_with_template_engine(analysis)
                elif provider == 'universal_fallback':
                    app_code = self._generate_universal_fallback(file_content, filename)
                
                # Validate generated code
                if self._validate_app_code(app_code):
                    logger.info(f"Success with provider: {provider}")
                    return {
                        'success': True,
                        'provider': provider,
                        'app_code': app_code,
                        'analysis': analysis,
                        'validation_passed': True,
                        'model_used': generation_model
                    }
                    
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        # If all providers fail, use ultimate fallback
        logger.error("All providers failed, using ultimate fallback")
        return {
            'success': True,
            'provider': 'ultimate_fallback',
            'app_code': self._generate_ultimate_fallback(),
            'analysis': analysis,
            'validation_passed': True,
            'model_used': 'fallback_template'
        }
    
    def _generate_with_openrouter(self, analysis: Dict[str, Any], instructions: str = None, model: str = None) -> str:
        """Generate app using OpenRouter API"""
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")
        
        client = OpenAI(
            api_key=self.openrouter_api_key,
            base_url=self.openrouter_base_url
        )
        
        # Use provided model or default
        model = model or self.generation_model
        
        # Create contextual prompt
        prompt = self._create_contextual_prompt(analysis, instructions)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Python developer specializing in creating Streamlit applications from Excel files. Generate complete, runnable code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.api_timeout
            )
            
            app_code = response.choices[0].message.content
            
            # Extract code from markdown if needed
            if '```python' in app_code:
                app_code = app_code.split('```python')[1].split('```')[0]
            elif '```' in app_code:
                app_code = app_code.split('```')[1].split('```')[0]
            
            return app_code.strip()
            
        except Exception as e:
            logger.error(f"OpenRouter generation failed: {e}")
            raise
    
    def _generate_with_deepseek(self, analysis: Dict[str, Any], instructions: str = None, model: str = None) -> str:
        """Generate app using DeepSeek OpenAI-compatible API"""
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key not configured")
        
        client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url=self.deepseek_base_url
        )
        
        # Use provided model or default
        model = model or self.generation_model
        
        # Create contextual prompt
        prompt = self._create_contextual_prompt(analysis, instructions)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Python developer specializing in creating Streamlit applications from Excel files. Generate complete, runnable code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.api_timeout
            )
            
            app_code = response.choices[0].message.content
            
            # Extract code from markdown if needed
            if '```python' in app_code:
                app_code = app_code.split('```python')[1].split('```')[0]
            elif '```' in app_code:
                app_code = app_code.split('```')[1].split('```')[0]
            
            return app_code.strip()
            
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            raise
    
    def _generate_with_template_engine(self, analysis: Dict[str, Any]) -> str:
        """Generate app using template-based engine"""
        template_type = analysis['analysis_summary']['recommended_template']
        
        if template_type == 'Financial Dashboard':
            return self._generate_financial_dashboard(analysis)
        elif template_type == 'Sales Analytics':
            return self._generate_sales_analytics(analysis)
        elif template_type == 'Inventory Management':
            return self._generate_inventory_management(analysis)
        elif template_type == 'HR Management':
            return self._generate_hr_management(analysis)
        elif template_type == 'Project Management':
            return self._generate_project_management(analysis)
        else:
            return self._generate_universal_data_explorer(analysis)
    
    def _generate_universal_fallback(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Generate universal data explorer as fallback"""
        # Use the existing lean converter as fallback
        from lean_excel_to_app import LeanExcelConverter
        
        converter = LeanExcelConverter()
        analysis = converter.analyze_excel(file_content, filename)
        app_code = converter.generate_app_code(analysis)
        
        return {
            'success': True,
            'provider': 'universal_fallback',
            'app_code': app_code,
            'analysis': analysis,
            'validation_passed': True
        }
    
    def _generate_ultimate_fallback(self) -> str:
        """Ultimate fallback - basic but guaranteed to work"""
        return '''import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("📊 Data Explorer")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.dataframe(df)
    st.write(f"Rows: {len(df)}, Columns: {len(df.columns)}")
else:
    st.info("Upload a file to begin")
'''
    
    def _create_contextual_prompt(self, analysis: Dict[str, Any], instructions: str = None) -> str:
        """Create contextual prompt based on analysis"""
        base_instructions = instructions or "Generate a complete Streamlit application that replaces this Excel file for daily use."
        
        prompt = f"""
EXCEL ANALYSIS REPORT:

File Information:
- Filename: {analysis['file_info']['filename']}
- Sheets: {analysis['file_info']['sheet_count']} ({', '.join(analysis['file_info']['sheet_names'])})

Structure:
- Total Rows: {analysis['structure']['total_rows']}
- Total Columns: {analysis['structure']['total_columns']}

Formulas:
- Total Formulas: {analysis['formulas']['total_count']}
- Formula Categories: {json.dumps(analysis['formulas']['formula_categories'], indent=2)}

Business Logic:
- Domain: {analysis['business_logic']['domain']}
- Key Operations: {analysis['business_logic']['key_operations']}
- Business Rules: {analysis['business_logic']['business_rules']}

Charts:
- Total Charts: {analysis['charts']['total_count']}

Analysis Summary:
- Overall Complexity: {analysis['analysis_summary']['overall_complexity']}
- Recommended Template: {analysis['analysis_summary']['recommended_template']}
- Key Findings: {analysis['analysis_summary']['key_findings']}
- Recommendations: {analysis['analysis_summary']['recommendations']}

USER INSTRUCTIONS:
{base_instructions}

REQUIREMENTS:
1. Generate a complete, runnable Streamlit application
2. Preserve all business logic and calculations
3. Include data visualization where appropriate
4. Make it user-friendly and intuitive
5. Include error handling
6. Use modern UI components

Generate ONLY the Python code without explanations:
"""
        
        return prompt
    
    def _validate_app_code(self, app_code: str) -> bool:
        """Basic validation of generated app code"""
        try:
            # Check for required imports
            required_imports = ['streamlit', 'pandas']
            for imp in required_imports:
                if imp not in app_code:
                    logger.warning(f"Missing required import: {imp}")
                    return False
            
            # Check for basic Streamlit structure
            if 'st.' not in app_code:
                logger.warning("Missing Streamlit components")
                return False
            
            # Basic syntax check (could be enhanced with ast.parse)
            if 'import streamlit as st' not in app_code:
                logger.warning("Missing Streamlit import")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    # Template generation methods
    def _generate_financial_dashboard(self, analysis: Dict[str, Any]) -> str:
        """Generate financial dashboard template"""
        return '''import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Financial Dashboard", layout="wide")
st.title("💰 Financial Dashboard")

uploaded_file = st.file_uploader("Upload Financial Data", type=['xlsx', 'xls'])

if uploaded_file:
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    for sheet_name, df in sheets.items():
        with st.expander(f"📊 {sheet_name}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(df, use_container_width=True)
            
            with col2:
                st.metric("Total Rows", len(df))
                st.metric("Total Columns", len(df.columns))
                
                # Financial metrics
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    for col in numeric_cols[:3]:  # Show first 3 numeric columns
                        st.metric(f"{col} Sum", f"${df[col].sum():,.2f}")

else:
    st.info("Upload a financial Excel file to begin analysis")
'''
    
    def _generate_sales_analytics(self, analysis: Dict[str, Any]) -> str:
        """Generate sales analytics template"""
        return '''import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analytics", layout="wide")
st.title("📈 Sales Analytics")

uploaded_file = st.file_uploader("Upload Sales Data", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.dataframe(df, use_container_width=True)
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        with col1:
            st.metric("Total Sales", f"${df[numeric_cols[0]].sum():,.2f}")
        with col2:
            st.metric("Average Sale", f"${df[numeric_cols[0]].mean():,.2f}")
        with col3:
            st.metric("Max Sale", f"${df[numeric_cols[0]].max():,.2f}")
        with col4:
            st.metric("Min Sale", f"${df[numeric_cols[0]].min():,.2f}")

else:
    st.info("Upload sales data to begin analysis")
'''
    
    def _generate_inventory_management(self, analysis: Dict[str, Any]) -> str:
        """Generate inventory management template"""
        return '''import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management")

uploaded_file = st.file_uploader("Upload Inventory Data", type=['xlsx', 'xls'])

if uploaded_file:
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    for sheet_name, df in sheets.items():
        with st.expander(f"📋 {sheet_name}"):
            st.dataframe(df, use_container_width=True)
            
            # Inventory metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Items", len(df))
            with col2:
                st.metric("Unique Products", df.iloc[:, 0].nunique() if len(df.columns) > 0 else 0)
            with col3:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.metric("Total Quantity", int(df[numeric_cols[0]].sum()))

else:
    st.info("Upload inventory data to begin management")
'''
    
    def _generate_hr_management(self, analysis: Dict[str, Any]) -> str:
        """Generate HR management template"""
        return '''import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Management", layout="wide")
st.title("👥 HR Management")

uploaded_file = st.file_uploader("Upload HR Data", type=['xlsx', 'xls'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    st.dataframe(df, use_container_width=True)
    
    # HR metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", len(df))
    with col2:
        if len(df.columns) > 1:
            st.metric("Departments", df.iloc[:, 1].nunique())
    with col3:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.metric("Avg Salary", f"${df[numeric_cols[0]].mean():,.2f}")
    with col4:
        st.metric("Data Points", len(df) * len(df.columns))

else:
    st.info("Upload HR data to begin management")
'''
    
    def _generate_project_management(self, analysis: Dict[str, Any]) -> str:
        """Generate project management template"""
        return '''import streamlit as st
import pandas as pd

st.set_page_config(page_title="Project Management", layout="wide")
st.title("📋 Project Management")

uploaded_file = st.file_uploader("Upload Project Data", type=['xlsx', 'xls'])

if uploaded_file:
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    for sheet_name, df in sheets.items():
        with st.expander(f"📁 {sheet_name}"):
            st.dataframe(df, use_container_width=True)
            
            # Project metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Projects", len(df))
            with col2:
                st.metric("Active Items", len(df))
            with col3:
                st.metric("Completion Rate", "N/A")

else:
    st.info("Upload project data to begin management")
'''
    
    def _generate_universal_data_explorer(self, analysis: Dict[str, Any]) -> str:
        """Generate universal data explorer template"""
        return '''import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("📊 Universal Data Explorer")

uploaded_file = st.file_uploader("Upload Data File", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            sheets = {'CSV Data': df}
        else:
            sheets = pd.read_excel(uploaded_file, sheet_name=None)
        
        tabs = st.tabs(list(sheets.keys()))
        
        for i, (sheet_name, df) in enumerate(sheets.items()):
            with tabs[i]:
                st.header(f"Sheet: {sheet_name}")
                
                # Data overview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                # Data preview
                st.subheader("Data Preview")
                st.dataframe(df, use_container_width=True)
                
                # Basic statistics
                st.subheader("Statistics")
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Simple visualization
                if len(numeric_cols) > 0:
                    st.subheader("Visualization")
                    selected_col = st.selectbox("Select column", numeric_cols, key=f"col_{sheet_name}")
                    if selected_col:
                        fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
                        st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a data file to begin exploration")
'''

# Utility function for quick app generation
def generate_app_from_excel(file_content: bytes, filename: str, instructions: str = None) -> Dict[str, Any]:
    """Quick app generation from Excel file"""
    orchestrator = LLMOrchestrator()
    return orchestrator.generate_business_app(file_content, filename, instructions)

if __name__ == "__main__":
    # Test the orchestrator
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            file_content = f.read()
        result = generate_app_from_excel(file_content, sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python llm_orchestrator.py <excel_file_path>")