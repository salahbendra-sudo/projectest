"""
Modular Code Generator for Excel-to-Web Application Generator

This module generates complete web applications from Excel analysis results,
including frontend, backend, and database components.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GeneratedFile:
    """Represents a generated file with path and content"""
    path: str
    content: str

class ModularCodeGenerator:
    """Generates modular web application code from Excel analysis"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code generation templates"""
        return {
            "streamlit_app": self._get_streamlit_template(),
            "fastapi_backend": self._get_fastapi_template(),
            "requirements": self._get_requirements_template(),
            "dockerfile": self._get_dockerfile_template(),
            "config": self._get_config_template()
        }
    
    def generate_application(self, analysis_result: Dict[str, Any], 
                           template_type: str = "streamlit") -> List[GeneratedFile]:
        """Generate complete web application from analysis"""
        files = []
        
        # Generate main application file
        if template_type == "streamlit":
            files.append(self._generate_streamlit_app(analysis_result))
        elif template_type == "fastapi":
            files.append(self._generate_fastapi_app(analysis_result))
        
        # Generate requirements file
        files.append(self._generate_requirements_file(analysis_result))
        
        # Generate configuration files
        files.append(self._generate_config_file(analysis_result))
        
        # Generate Dockerfile for deployment
        files.append(self._generate_dockerfile(analysis_result))
        
        # Generate additional utility files
        files.extend(self._generate_utility_files(analysis_result))
        
        return files
    
    def _generate_streamlit_app(self, analysis_result: Dict[str, Any]) -> GeneratedFile:
        """Generate Streamlit application"""
        template = self.templates["streamlit_app"]
        
        # Extract key information from analysis
        sheets = list(analysis_result["sheets"].keys())
        formulas = analysis_result["formulas"]
        charts = analysis_result["charts"]
        template_type = analysis_result.get("template_type", {})
        
        # Generate data loading section
        data_loading_code = self._generate_data_loading_code(analysis_result)
        
        # Generate visualization section
        visualization_code = self._generate_visualization_code(analysis_result)
        
        # Generate calculation section
        calculation_code = self._generate_calculation_code(analysis_result)
        
        # Handle plotly imports and visualization tab
        if charts:
            plotly_imports = "import plotly.express as px\nimport plotly.graph_objects as go"
            visualization_tab = 'tab_names.append("Visualizations")'
            visualization_tab_content = '''
    with tabs[1]:
        st.header("Visualizations")
        visualizations = create_visualizations(data)
        for name, fig in visualizations.items():
            st.plotly_chart(fig, use_container_width=True)
'''
        else:
            plotly_imports = "# No plotly imports needed - no charts detected"
            visualization_tab = "# No visualization tab needed - no charts detected"
            visualization_tab_content = "# No visualization tab content - no charts detected"
        
        # Replace template placeholders
        content = template.replace("{{DATA_LOADING}}", data_loading_code)
        content = content.replace("{{VISUALIZATION}}", visualization_code)
        content = content.replace("{{CALCULATIONS}}", calculation_code)
        content = content.replace("{{SHEET_COUNT}}", str(len(sheets)))
        content = content.replace("{{FORMULA_COUNT}}", str(len(formulas)))
        content = content.replace("{{CHART_COUNT}}", str(len(charts)))
        content = content.replace("{{TEMPLATE_TYPE}}", template_type.get("name", "Custom"))
        content = content.replace("{{PLOTLY_IMPORTS}}", plotly_imports)
        content = content.replace("{{VISUALIZATION_TAB}}", visualization_tab)
        content = content.replace("{{VISUALIZATION_TAB_CONTENT}}", visualization_tab_content)
        
        return GeneratedFile("app.py", content)
    
    def _generate_fastapi_app(self, analysis_result: Dict[str, Any]) -> GeneratedFile:
        """Generate FastAPI backend application"""
        template = self.templates["fastapi_backend"]
        
        # Generate API endpoints based on formulas
        endpoints_code = self._generate_api_endpoints(analysis_result)
        
        # Generate data models
        models_code = self._generate_data_models(analysis_result)
        
        content = template.replace("{{API_ENDPOINTS}}", endpoints_code)
        content = content.replace("{{DATA_MODELS}}", models_code)
        
        return GeneratedFile("main.py", content)
    
    def _generate_requirements_file(self, analysis_result: Dict[str, Any]) -> GeneratedFile:
        """Generate requirements.txt file"""
        template = self.templates["requirements"]
        
        # Add specific packages based on analysis
        packages = []
        
        # Always include core packages
        packages.extend([
            "pandas>=1.5.0",
            "numpy>=1.21.0",
            "openpyxl>=3.0.0"
        ])
        
        # Add visualization packages if charts exist
        if analysis_result["charts"]:
            packages.extend([
                "plotly>=5.0.0",
                "matplotlib>=3.5.0"
            ])
        
        # Add web framework - default to streamlit for now
        packages.append("streamlit>=1.22.0")
        
        content = template.replace("{{PACKAGES}}", "\n".join(packages))
        
        return GeneratedFile("requirements.txt", content)
    
    def _generate_dockerfile(self, analysis_result: Dict[str, Any]) -> GeneratedFile:
        """Generate Dockerfile for deployment"""
        template = self.templates["dockerfile"]
        
        # Determine entry point based on application type
        entry_point = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
        
        content = template.replace("{{ENTRY_POINT}}", entry_point)
        
        return GeneratedFile("Dockerfile", content)
    
    def _generate_config_file(self, analysis_result: Dict[str, Any]) -> GeneratedFile:
        """Generate configuration file"""
        template = self.templates["config"]
        
        config_data = {
            "template_type": analysis_result.get("template_type", {}).get("name", "custom"),
            "sheets": list(analysis_result["sheets"].keys()),
            "formula_count": len(analysis_result["formulas"]),
            "chart_count": len(analysis_result["charts"]),
            "generated_at": "2024-01-01"  # Would be actual timestamp
        }
        
        content = template.replace("{{CONFIG_DATA}}", json.dumps(config_data, indent=2))
        
        return GeneratedFile("config.json", content)
    
    def _generate_utility_files(self, analysis_result: Dict[str, Any]) -> List[GeneratedFile]:
        """Generate additional utility files"""
        files = []
        
        # Generate data processing utilities
        data_utils = self._generate_data_utils(analysis_result)
        files.append(GeneratedFile("utils/data_processing.py", data_utils))
        
        # Generate formula translation utilities
        formula_utils = self._generate_formula_utils(analysis_result)
        files.append(GeneratedFile("utils/formula_translator.py", formula_utils))
        
        return files
    
    def _generate_data_loading_code(self, analysis_result: Dict[str, Any]) -> str:
        """Generate data loading code"""
        sheets = list(analysis_result["sheets"].keys())
        
        code_lines = [
            "# Data loading and preprocessing",
            "import pandas as pd",
            "import streamlit as st",
            "import io",
            "",
            "def load_data():",
            "    '''Load and process Excel data from uploaded file'''",
            "    try:",
            "        # File upload widget",
            "        uploaded_file = st.file_uploader(\"Upload Excel File\", type=['xlsx', 'xls'])",
            "        ",
            "        if uploaded_file is not None:",
            "            # Load all sheets",
            f"            sheets = {sheets}",
            "            data = {}",
            "            for sheet in sheets:",
            "                # Load each sheet with appropriate processing",
            "                df = pd.read_excel(uploaded_file, sheet_name=sheet)",
            "                data[sheet] = df",
            "            return data",
            "        else:",
            "            st.info('Please upload an Excel file to begin')",
            "            return {}",
            "    except Exception as e:",
            "        st.error(f'Error loading data: {e}')",
            "        return {}",
            ""
        ]
        
        return "\n".join(code_lines)
    
    def _generate_visualization_code(self, analysis_result: Dict[str, Any]) -> str:
        """Generate visualization code"""
        charts = analysis_result["charts"]
        
        if not charts:
            return "# No charts detected in original Excel file"
        
        code_lines = [
            "# Data visualization",
            "import plotly.express as px",
            "import plotly.graph_objects as go",
            "",
            "def create_visualizations(data):",
            "    '''Create interactive visualizations'''",
            "    visualizations = {}",
            "    "
        ]
        
        for i, chart in enumerate(charts[:5]):  # Limit to first 5 charts
            code_lines.extend([
                f"    # Chart: {chart.name}",
                f"    try:",
                f"        fig_{i} = px.line(data['{chart.sheet}'])  # Placeholder",
                f"        fig_{i}.update_layout(title='{chart.title}')",
                f"        visualizations['{chart.name}'] = fig_{i}",
                f"    except Exception as e:",
                f"        st.warning(f'Could not create chart {chart.name}: {{e}}')",
                ""
            ])
        
        code_lines.append("    return visualizations")
        
        return "\n".join(code_lines)
    
    def _generate_calculation_code(self, analysis_result: Dict[str, Any]) -> str:
        """Generate calculation code from Excel formulas"""
        formulas = analysis_result["formulas"]
        
        if not formulas:
            return "# No formulas detected in original Excel file"
        
        code_lines = [
            "# Business logic calculations",
            "import numpy as np",
            "",
            "def perform_calculations(data):",
            "    '''Perform calculations based on Excel formulas'''",
            "    results = {}",
            ""
        ]
        
        # Group formulas by category
        financial_formulas = [f for f in formulas if f.category == "financial"]
        statistical_formulas = [f for f in formulas if f.category == "statistical"]
        
        if financial_formulas:
            code_lines.extend([
                "    # Financial calculations",
                "    for sheet_name, df in data.items():",
                "        if 'revenue' in df.columns and 'cost' in df.columns:",
                "            df['profit'] = df['revenue'] - df['cost']",
                "            results['profit_margin'] = (df['profit'] / df['revenue']).mean()",
                ""
            ])
        
        if statistical_formulas:
            code_lines.extend([
                "    # Statistical calculations",
                "    for sheet_name, df in data.items():",
                "        numeric_cols = df.select_dtypes(include=[np.number]).columns",
                "        if len(numeric_cols) > 0:",
                "            results[f'{sheet_name}_stats'] = {",
                "                'mean': df[numeric_cols].mean().to_dict(),",
                "                'std': df[numeric_cols].std().to_dict()",
                "            }",
                ""
            ])
        
        code_lines.append("    return results")
        
        return "\n".join(code_lines)
    
    def _generate_api_endpoints(self, analysis_result: Dict[str, Any]) -> str:
        """Generate API endpoints"""
        formulas = analysis_result["formulas"]
        
        code_lines = [
            "# API endpoints",
            "from fastapi import FastAPI, HTTPException",
            "import pandas as pd",
            "",
            "app = FastAPI()",
            "",
            "@app.get('/')",
            "async def root():",
            "    return {'message': 'Excel-to-Web API'}",
            ""
        ]
        
        # Create endpoints for key formulas
        key_formulas = [f for f in formulas if f.complexity >= 5]
        for i, formula in enumerate(key_formulas[:10]):  # Limit to first 10
            endpoint_name = formula.formula.split('(')[0].lower() if '(' in formula.formula else f"calc_{i}"
            code_lines.extend([
                f"@app.get('/{endpoint_name}')",
                f"async def {endpoint_name}_endpoint():",
                f"    '''Endpoint for: {formula.formula}'''",
                f"    try:",
                f"        # Implement calculation logic here",
                f"        result = {{'formula': '{formula.formula}', 'result': 'calculated_value'}}",
                f"        return result",
                f"    except Exception as e:",
                f"        raise HTTPException(status_code=500, detail=str(e))",
                ""
            ])
        
        return "\n".join(code_lines)
    
    def _generate_data_models(self, analysis_result: Dict[str, Any]) -> str:
        """Generate data models"""
        sheets = analysis_result["sheets"]
        
        code_lines = [
            "# Data models",
            "from pydantic import BaseModel",
            "from typing import Dict, List, Optional",
            ""
        ]
        
        for sheet_name, sheet_info in list(sheets.items())[:5]:  # Limit to first 5 sheets
            model_name = sheet_name.replace(" ", "").replace("-", "").title()
            code_lines.extend([
                f"class {model_name}Model(BaseModel):",
                f"    '''Data model for {sheet_name} sheet'''",
                "    # Define fields based on your data structure",
                "    pass",
                ""
            ])
        
        return "\n".join(code_lines)
    
    def _generate_data_utils(self, analysis_result: Dict[str, Any]) -> str:
        """Generate data processing utilities"""
        return """
# Data processing utilities
import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    '''Clean and preprocess DataFrame'''
    # Remove empty rows and columns
    df = df.dropna(how='all').dropna(axis=1, how='all')
    
    # Convert numeric columns
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
    
    return df

def detect_data_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    '''Detect data types in DataFrame'''
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'date': date_cols
    }
"""
    
    def _generate_formula_utils(self, analysis_result: Dict[str, Any]) -> str:
        """Generate formula translation utilities"""
        return """
# Formula translation utilities
import re

def excel_to_python_formula(excel_formula: str) -> str:
    '''Convert Excel formula syntax to Python'''
    # Remove leading = if present
    if excel_formula.startswith('='):
        excel_formula = excel_formula[1:]
    
    # Basic function translations
    translations = {
        'SUM(': 'sum(',
        'AVERAGE(': 'np.mean(',
        'MAX(': 'max(',
        'MIN(': 'min(',
        'IF(': 'if_else(',
        'VLOOKUP(': 'vlookup(',
    }
    
    python_formula = excel_formula
    for excel_func, python_func in translations.items():
        python_formula = python_formula.replace(excel_func, python_func)
    
    return python_formula

def if_else(condition, true_value, false_value):
    '''Python implementation of Excel IF function'''
    return true_value if condition else false_value

def vlookup(lookup_value, table_array, col_index_num, range_lookup=True):
    '''Python implementation of Excel VLOOKUP function'''
    # Simplified implementation
    for row in table_array:
        if row[0] == lookup_value:
            return row[col_index_num - 1]
    return None
"""
    
    # Template methods
    def _get_streamlit_template(self) -> str:
        return """
import streamlit as st
import pandas as pd
{{PLOTLY_IMPORTS}}

# Configure page
st.set_page_config(
    page_title="Excel-to-Web App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown('''
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
</style>
''', unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 Excel-to-Web Application</div>', unsafe_allow_html=True)

# App info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Sheets", "{{SHEET_COUNT}}")
with col2:
    st.metric("Formulas", "{{FORMULA_COUNT}}")
with col3:
    st.metric("Charts", "{{CHART_COUNT}}")

st.info(f"Template Type: {{TEMPLATE_TYPE}}")

{{DATA_LOADING}}

{{VISUALIZATION}}

{{CALCULATIONS}}

# Main application logic
def main():
    # Load data
    data = load_data()
    
    if not data:
        st.error("No data loaded. Please check your Excel file.")
        return
    
    # Create tabs for different sections
    tab_names = ["Data Explorer"]
    {{VISUALIZATION_TAB}}
    tab_names.append("Calculations")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        st.header("Data Explorer")
        selected_sheet = st.selectbox("Select Sheet", list(data.keys()))
        if selected_sheet in data:
            st.dataframe(data[selected_sheet], use_container_width=True)
    
    {{VISUALIZATION_TAB_CONTENT}}
    
    with tabs[-1]:
        st.header("Calculations")
        results = perform_calculations(data)
        for key, value in results.items():
            st.metric(key, str(value))

if __name__ == "__main__":
    main()
"""
    
    def _get_fastapi_template(self) -> str:
        return """
{{DATA_MODELS}}

{{API_ENDPOINTS}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    def _get_requirements_template(self) -> str:
        return """
{{PACKAGES}}
"""
    
    def _get_dockerfile_template(self) -> str:
        return """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD {{ENTRY_POINT}}
"""
    
    def _get_config_template(self) -> str:
        return """
{{CONFIG_DATA}}
"""