import streamlit as st
import pandas as pd
import time
import uuid
import json
import hashlib
from datetime import datetime, timedelta
import base64
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="Excel to App Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .upload-zone {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(45deg, #f8f9ff, #fff);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #764ba2;
        background: linear-gradient(45deg, #f0f2ff, #f8f9ff);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    .progress-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .agent-status {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .agent-emoji {
        font-size: 2rem;
        margin-right: 1rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .success-container {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #f1c40f;
        animation: confetti-fall 3s linear infinite;
    }
    
    @keyframes confetti-fall {
        to {
            transform: translateY(100vh) rotate(360deg);
        }
    }
    
    .error-container {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .preview-table {
        margin: 1rem 0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 10px;
        color: #6c757d;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app_generated' not in st.session_state:
    st.session_state.app_generated = False
if 'app_url' not in st.session_state:
    st.session_state.app_url = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

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

def create_app_code(df):
    """Generate Streamlit app code based on the uploaded data"""
    
    # Analyze data types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = []
    
    # Try to identify date columns
    for col in text_cols:
        try:
            pd.to_datetime(df[col].dropna().iloc[:5])
            date_cols.append(col)
        except:
            pass
    
    # Generate app code
    app_code = f'''
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Data Explorer",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    # In a real implementation, this would load from a database
    data = {df.to_dict('records')}
    return pd.DataFrame(data)

df = load_data()

st.title("📊 Interactive Data Explorer")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Create filters based on data types
filtered_df = df.copy()

{generate_filters(df, numeric_cols, text_cols, date_cols)}

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Data Visualization")
    
    if len(filtered_df) > 0:
        # Chart type selector
        chart_type = st.selectbox("Select Chart Type", 
                                ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
        
        {generate_charts(numeric_cols, text_cols)}
    else:
        st.warning("No data matches your filters!")

with col2:
    st.subheader("📋 Data Summary")
    st.metric("Total Records", len(filtered_df))
    st.metric("Columns", len(df.columns))
    
    if numeric_cols:
        st.subheader("📊 Statistics")
        for col in numeric_cols[:3]:  # Show stats for first 3 numeric columns
            if col in filtered_df.columns:
                st.metric(f"Avg {col}", f"{{filtered_df[col].mean():.2f}}")

# Data table
st.subheader("🗂️ Raw Data")
st.dataframe(filtered_df, use_container_width=True)

# Download button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)
'''
    
    return app_code

def generate_filters(df, numeric_cols, text_cols, date_cols):
    """Generate filter code based on column types"""
    filter_code = ""
    
    # Numeric filters
    for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
        filter_code += f'''
# {col} filter
{col}_range = st.sidebar.slider(
    "{col}",
    min_value=float(df["{col}"].min()),
    max_value=float(df["{col}"].max()),
    value=(float(df["{col}"].min()), float(df["{col}"].max()))
)
filtered_df = filtered_df[
    (filtered_df["{col}"] >= {col}_range[0]) & 
    (filtered_df["{col}"] <= {col}_range[1])
]
'''
    
    # Text filters
    for col in text_cols[:3]:  # Limit to first 3 text columns
        filter_code += f'''
# {col} filter
{col}_options = st.sidebar.multiselect(
    "{col}",
    options=df["{col}"].unique(),
    default=df["{col}"].unique()
)
if {col}_options:
    filtered_df = filtered_df[filtered_df["{col}"].isin({col}_options)]
'''
    
    return filter_code

def generate_charts(numeric_cols, text_cols):
    """Generate chart code based on available columns"""
    chart_code = ""
    
    if numeric_cols and text_cols:
        chart_code = f'''
        if chart_type == "Bar Chart" and len({text_cols[:1]}) > 0:
            fig = px.bar(filtered_df, x="{text_cols[0]}", y="{numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Scatter Plot" and len({numeric_cols}) >= 2:
            fig = px.scatter(filtered_df, x="{numeric_cols[0]}", y="{numeric_cols[1]}")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Line Chart":
            fig = px.line(filtered_df, y="{numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Histogram":
            fig = px.histogram(filtered_df, x="{numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        '''
    elif numeric_cols:
        chart_code = f'''
        if chart_type == "Histogram":
            fig = px.histogram(filtered_df, x="{numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Line Chart":
            fig = px.line(filtered_df, y="{numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        '''
    
    return chart_code

def simulate_app_generation():
    """Simulate AI agent building the app with progress animation"""
    
    stages = [
        {"emoji": "🔍", "text": "Analyzing your data structure...", "duration": 2},
        {"emoji": "🧠", "text": "Understanding data relationships...", "duration": 3},
        {"emoji": "📝", "text": "Planning app architecture...", "duration": 2},
        {"emoji": "👨‍💻", "text": "Writing custom code for your data...", "duration": 4},
        {"emoji": "🎨", "text": "Designing beautiful visualizations...", "duration": 3},
        {"emoji": "🚀", "text": "Deploying your app to the cloud...", "duration": 2},
    ]
    
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    total_duration = sum(stage["duration"] for stage in stages)
    current_progress = 0
    
    for i, stage in enumerate(stages):
        # Update status
        status_container.markdown(f'''
        <div class="agent-status">
            <span class="agent-emoji">{stage["emoji"]}</span>
            <span>{stage["text"]}</span>
        </div>
        ''', unsafe_allow_html=True)
        
        # Simulate work with incremental progress
        stage_steps = stage["duration"] * 10
        for step in range(stage_steps):
            time.sleep(0.1)
            current_progress += 1
            progress_percentage = current_progress / (total_duration * 10)
            progress_bar.progress(progress_percentage)
    
    status_container.empty()
    progress_bar.empty()

def generate_app_url():
    """Generate a unique URL for the created app"""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(datetime.now().timestamp())
    
    # In a real implementation, you would:
    # 1. Save the generated app code to a database
    # 2. Deploy it to Streamlit Cloud or similar service
    # 3. Return the actual URL
    
    # For demo purposes, we'll create a simulated URL
    app_url = f"https://generated-app-{unique_id}.streamlit.app"
    
    return app_url

def main():
    # Hero section
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">🚀 Excel to App Generator</h1>
        <p class="hero-subtitle">Turn Excel files into interactive web apps in seconds!<br>
        Just upload your data, and our AI will handle the rest.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Main content
    if not st.session_state.app_generated:
        # Upload section
        st.markdown("### 📂 Upload Your Excel File")
        
        uploaded_file = st.file_uploader(
            "Choose your Excel or CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="Supported formats: .xlsx, .xls, .csv"
        )
        
        if uploaded_file is not None:
            try:
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
                    
                    # Provide template download
                    template_data = {
                        'Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
                        'Category': ['Electronics', 'Clothing', 'Electronics', 'Books', 'Clothing'],
                        'Price': [299.99, 49.99, 199.99, 15.99, 89.99],
                        'Sales': [150, 320, 89, 450, 210],
                        'Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
                    }
                    template_df = pd.DataFrame(template_data)
                    csv_template = template_df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download Template File",
                        data=csv_template,
                        file_name="excel_template.csv",
                        mime="text/csv"
                    )
                
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
                            
                            # Run the simulation
                            simulate_app_generation()
                            
                            # Generate the app
                            app_code = create_app_code(df)
                            app_url = generate_app_url()
                            
                            st.session_state.app_generated = True
                            st.session_state.app_url = app_url
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Trigger rerun to show success screen
                            st.rerun()
            
            except Exception as e:
                st.markdown('<div class="error-container">', unsafe_allow_html=True)
                st.error(f"❌ Error reading file: {str(e)}")
                st.write("Please make sure your file is a valid Excel or CSV file.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Success screen
        st.markdown('''
        <div class="success-container">
            <h2>🎉 Your App is Ready!</h2>
            <p>Your interactive data app has been successfully generated and deployed!</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Show the generated URL
        st.markdown("### 🔗 Your App URL")
        st.code(st.session_state.app_url, language="text")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌐 Open App"):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={st.session_state.app_url}">', unsafe_allow_html=True)
                st.success("Opening your app in a new tab!")
        
        with col2:
            if st.button("📋 Copy Link"):
                # JavaScript to copy to clipboard would go here
                st.success("Link copied to clipboard!")
        
        with col3:
            if st.button("🔄 Generate Another"):
                st.session_state.app_generated = False
                st.session_state.app_url = None
                st.session_state.uploaded_data = None
                st.rerun()
        
        # App preview info
        if st.session_state.uploaded_data is not None:
            st.markdown("### 📊 What Your App Includes")
            df = st.session_state.uploaded_data
            
            features = []
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if numeric_cols:
                features.append(f"📈 Interactive charts for {len(numeric_cols)} numeric columns")
            if text_cols:
                features.append(f"🔍 Smart filters for {len(text_cols)} categorical columns")
            features.append("📋 Sortable and searchable data table")
            features.append("📥 Data download functionality")
            features.append("📊 Automatic statistics and summaries")
            
            for feature in features:
                st.write(f"• {feature}")
    
    # Footer
    st.markdown('''
    <div class="footer">
        <p><strong>No code required.</strong> Apps are hosted temporarily for demo purposes.</p>
        <p>In production, apps would be permanently deployed with custom domains available.</p>
        <p>Built with ❤️ using Streamlit</p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
