import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time
import os
import io
import zipfile
from pathlib import Path
import tempfile

# ------------------------------------
# Page Configuration
# ------------------------------------
st.set_page_config(
    page_title="Project AEGIS - Biomedical Analytics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------
# Custom CSS with Background Image
# ------------------------------------
def load_css():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Semi-transparent overlay for better readability */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #1f77b4, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 2rem;
        animation: fadeIn 2s ease-in-out;
    }
    
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    
    .metric-card {
        background-color: rgba(240, 242, 246, 0.9);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
        backdrop-filter: blur(5px);
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .security-badge {
        background-color: rgba(212, 237, 218, 0.9);
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
        backdrop-filter: blur(5px);
    }
    
    .footer {
        text-align: center;
        color: gray;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
    
    .profile-card {
        background-color: rgba(238, 245, 250, 0.9);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        backdrop-filter: blur(5px);
    }
    
    .file-upload-section {
        background-color: rgba(248, 249, 250, 0.9);
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #1f77b4;
        margin-bottom: 2rem;
    }
    
    .data-preview {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------
# File Processing Functions
# ------------------------------------
def process_csv_file(uploaded_file):
    """Process CSV file and return DataFrame"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, f"✅ CSV file loaded successfully: {len(df)} rows, {len(df.columns)} columns"
    except Exception as e:
        return None, f"❌ Error loading CSV: {str(e)}"

def process_xpt_file(uploaded_file):
    """Process XPT file and return DataFrame"""
    try:
        # For XPT files (SAS transport files)
        try:
            import xport
            df = xport.to_dataframe(uploaded_file)
        except:
            # Fallback: try with pandas if xport not available
            st.warning("XPT processing limited - install 'xport' package for better support")
            df = pd.read_sas(uploaded_file, format='xport')
        return df, f"✅ XPT file loaded successfully: {len(df)} rows, {len(df.columns)} columns"
    except Exception as e:
        return None, f"❌ Error loading XPT: {str(e)}"

def process_excel_file(uploaded_file):
    """Process Excel file and return DataFrame"""
    try:
        df = pd.read_excel(uploaded_file)
        return df, f"✅ Excel file loaded successfully: {len(df)} rows, {len(df.columns)} columns"
    except Exception as e:
        return None, f"❌ Error loading Excel: {str(e)}"

def process_zip_folder(uploaded_file):
    """Process ZIP folder containing multiple files"""
    extracted_files = []
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)
                
                # Process all files in the extracted folder
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_info = {
                            'name': file,
                            'path': file_path,
                            'size': os.path.getsize(file_path)
                        }
                        
                        # Try to read as DataFrame if it's a supported file type
                        if file.lower().endswith(('.csv', '.xpt', '.xlsx', '.xls')):
                            try:
                                if file.lower().endswith('.csv'):
                                    df = pd.read_csv(file_path)
                                elif file.lower().endswith('.xpt'):
                                    df = pd.read_sas(file_path, format='xport')
                                else:
                                    df = pd.read_excel(file_path)
                                file_info['dataframe'] = df
                                file_info['rows'] = len(df)
                                file_info['columns'] = len(df.columns)
                            except Exception as e:
                                file_info['error'] = str(e)
                        
                        extracted_files.append(file_info)
        
        return extracted_files, f"✅ ZIP folder processed: {len(extracted_files)} files extracted"
    except Exception as e:
        return None, f"❌ Error processing ZIP folder: {str(e)}"

def analyze_dataframe(df, dataset_name=""):
    """Perform comprehensive analysis on DataFrame"""
    analysis = {}
    
    # Basic Information
    analysis['basic_info'] = {
        'Dataset Name': dataset_name,
        'Shape': f"{df.shape[0]} rows × {df.shape[1]} columns",
        'Memory Usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
        'Duplicate Rows': df.duplicated().sum(),
        'Total Missing Values': df.isnull().sum().sum()
    }
    
    # Data Types
    analysis['dtypes'] = df.dtypes.astype(str).to_dict()
    
    # Descriptive Statistics
    analysis['descriptive_stats'] = df.describe(include='all')
    
    # Missing Values Analysis
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    analysis['missing_values'] = pd.DataFrame({
        'Missing Count': missing_data,
        'Missing Percentage': missing_percent
    }).sort_values('Missing Count', ascending=False)
    
    # Correlation Analysis (for numeric columns)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        analysis['correlation'] = df[numeric_cols].corr()
    
    return analysis

def create_visualizations(df, dataset_name=""):
    """Create automated visualizations based on data types"""
    visualizations = []
    
    # Numeric columns histogram
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        for col in numeric_cols[:3]:  # Show first 3 numeric columns
            fig = px.histogram(df, x=col, title=f"Distribution of {col}")
            visualizations.append(fig)
    
    # Categorical columns bar chart
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols[:2]:  # Show first 2 categorical columns
            value_counts = df[col].value_counts().head(10)
            fig = px.bar(x=value_counts.index, y=value_counts.values, 
                        title=f"Top Values in {col}")
            visualizations.append(fig)
    
    # Correlation heatmap if enough numeric columns
    if len(numeric_cols) >= 3:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(corr_matrix, title="Correlation Heatmap")
        visualizations.append(fig)
    
    return visualizations

# ------------------------------------
# Authentication (Demo)
# ------------------------------------
def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/DNA_Icon.svg/512px-DNA_Icon.svg.png",
                width=150
            )
            
            st.markdown(
                "<h2 style='text-align:center; color:#1f77b4;'>Project AEGIS Secure Login</h2>",
                unsafe_allow_html=True
            )

            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")

            login_btn = st.button("Login", use_container_width=True)
            if login_btn:
                if username == "admin" and password == "aegis2024":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Access granted! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

            st.markdown("<p class='footer'>© 2025 Project AEGIS — Biomedical AI Lab</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()
    return True

# ------------------------------------
# Data Upload & Analysis Page
# ------------------------------------
def show_data_analysis():
    st.markdown('<div class="main-header">📊 Data Analysis Center</div>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/3588/3588773.png", width=150)

    # File Upload Section
    st.markdown('<div class="file-upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Your Biomedical Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_csv = st.file_uploader(
            "Upload CSV File", 
            type=['csv'],
            help="Upload comma-separated values file"
        )
        
        uploaded_xpt = st.file_uploader(
            "Upload XPT File", 
            type=['xpt'],
            help="Upload SAS transport file"
        )
    
    with col2:
        uploaded_excel = st.file_uploader(
            "Upload Excel File", 
            type=['xlsx', 'xls'],
            help="Upload Excel spreadsheet"
        )
        
        uploaded_zip = st.file_uploader(
            "Upload ZIP Folder", 
            type=['zip'],
            help="Upload ZIP folder containing multiple data files"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Process uploaded files
    current_df = None
    current_analysis = None
    
    if uploaded_csv:
        with st.spinner("Processing CSV file..."):
            df, message = process_csv_file(uploaded_csv)
            if df is not None:
                current_df = df
                st.success(message)
            else:
                st.error(message)
    
    elif uploaded_xpt:
        with st.spinner("Processing XPT file..."):
            df, message = process_xpt_file(uploaded_xpt)
            if df is not None:
                current_df = df
                st.success(message)
            else:
                st.error(message)
    
    elif uploaded_excel:
        with st.spinner("Processing Excel file..."):
            df, message = process_excel_file(uploaded_excel)
            if df is not None:
                current_df = df
                st.success(message)
            else:
                st.error(message)
    
    elif uploaded_zip:
        with st.spinner("Processing ZIP folder..."):
            files_info, message = process_zip_folder(uploaded_zip)
            if files_info is not None:
                st.success(message)
                
                # Display extracted files information
                st.subheader("📂 Extracted Files")
                for file_info in files_info:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(f"**{file_info['name']}**")
                    with col2:
                        st.write(f"Size: {file_info['size']} bytes")
                    with col3:
                        if 'dataframe' in file_info:
                            st.success(f"✅ {file_info['rows']} rows")
                        elif 'error' in file_info:
                            st.error("❌ Load failed")
                
                # Let user select which file to analyze
                analyzable_files = [f for f in files_info if 'dataframe' in f]
                if analyzable_files:
                    selected_file = st.selectbox(
                        "Select file to analyze:",
                        options=[f['name'] for f in analyzable_files]
                    )
                    selected_file_info = next(f for f in analyzable_files if f['name'] == selected_file)
                    current_df = selected_file_info['dataframe']
    
    # Display data and analysis if we have a DataFrame
    if current_df is not None:
        # Data Preview
        st.subheader("👀 Data Preview")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(current_df.head(100), use_container_width=True)
        
        with col2:
            st.metric("Total Rows", f"{len(current_df):,}")
            st.metric("Total Columns", f"{len(current_df.columns):,}")
            st.metric("Memory", f"{current_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Perform Analysis
        if st.button("🚀 Perform Comprehensive Analysis", use_container_width=True):
            with st.spinner("Analyzing data..."):
                current_analysis = analyze_dataframe(current_df, "Uploaded Dataset")
                
                # Display Analysis Results
                st.subheader("📈 Data Analysis Results")
                
                # Basic Information
                st.markdown("### 📋 Basic Information")
                info_cols = st.columns(4)
                basic_info = current_analysis['basic_info']
                info_cols[0].metric("Dataset", basic_info['Dataset Name'])
                info_cols[1].metric("Shape", basic_info['Shape'])
                info_cols[2].metric("Duplicates", basic_info['Duplicate Rows'])
                info_cols[3].metric("Missing Values", basic_info['Total Missing Values'])
                
                # Data Types
                st.markdown("### 🔧 Data Types")
                dtype_df = pd.DataFrame(list(current_analysis['dtypes'].items()), 
                                      columns=['Column', 'Data Type'])
                st.dataframe(dtype_df, use_container_width=True)
                
                # Missing Values Analysis
                st.markdown("### ⚠️ Missing Values Analysis")
                missing_df = current_analysis['missing_values']
                missing_df = missing_df[missing_df['Missing Count'] > 0]
                if len(missing_df) > 0:
                    fig = px.bar(missing_df.head(10), 
                               x=missing_df.index, 
                               y='Missing Count',
                               title="Top 10 Columns with Missing Values")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(missing_df, use_container_width=True)
                else:
                    st.success("🎉 No missing values found in the dataset!")
                
                # Descriptive Statistics
                st.markdown("### 📊 Descriptive Statistics")
                st.dataframe(current_analysis['descriptive_stats'], use_container_width=True)
                
                # Correlation Matrix
                if 'correlation' in current_analysis:
                    st.markdown("### 🔗 Correlation Matrix")
                    fig = px.imshow(current_analysis['correlation'],
                                  title="Correlation Heatmap",
                                  color_continuous_scale='RdBu_r',
                                  aspect="auto")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Automated Visualizations
                st.markdown("### 📈 Automated Visualizations")
                visualizations = create_visualizations(current_df)
                for viz in visualizations:
                    st.plotly_chart(viz, use_container_width=True)
        
        # Data Export Options
        st.markdown("---")
        st.subheader("📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = current_df.to_csv(index=False).encode()
            st.download_button(
                "💾 Download as CSV",
                data=csv_data,
                file_name="analyzed_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Summary statistics export
            if current_analysis:
                summary_df = current_analysis['descriptive_stats']
                summary_csv = summary_df.to_csv().encode()
                st.download_button(
                    "📊 Download Summary Stats",
                    data=summary_csv,
                    file_name="summary_statistics.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col3:
            if st.button("🔄 Analyze Another Dataset", use_container_width=True):
                st.rerun()

# ------------------------------------
# 🏠 Home Page
# ------------------------------------
def show_home():
    st.markdown('<div class="main-header">🏠 Welcome to Project AEGIS</div>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/2964/2964512.png", width=200)

    st.markdown("""
    ### 🔬 About the Platform
    **Project AEGIS** is a cutting-edge biomedical analytics suite designed for genomic research,
    precision nutrition, and predictive healthcare.  
    Built with advanced **AI models** and **secure data integration**, it empowers researchers to
    translate biological signals into actionable health insights.
    """)

    st.markdown("---")
    st.subheader("🧭 Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
    with c2:
        if st.button("🧬 Genomic Analysis", use_container_width=True):
            st.session_state.page = "Genomic Analysis"
            st.rerun()
    with c3:
        if st.button("📁 Data Analysis", use_container_width=True):
            st.session_state.page = "Data Analysis"
            st.rerun()
    with c4:
        if st.button("🤖 Model Training", use_container_width=True):
            st.session_state.page = "Model Training"
            st.rerun()

# ------------------------------------
# Dashboard Page
# ------------------------------------
def show_dashboard():
    st.markdown('<div class="main-header">🧬 Project AEGIS Dashboard</div>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/1081/1081055.png", width=150)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", "12,847", "1,234")
        st.markdown('<div class="metric-card">Integrated datasets from 3 sources</div>', unsafe_allow_html=True)
    with col2:
        st.metric("Genomic Variants", "4.2M", "84K")
        st.markdown('<div class="metric-card">Nutrition-related SNPs analyzed</div>', unsafe_allow_html=True)
    with col3:
        st.metric("Model Accuracy", "0.87", "0.02")
        st.markdown('<div class="metric-card">Glucose prediction performance</div>', unsafe_allow_html=True)
    with col4:
        st.metric("Security Score", "98%", "2%")
        st.markdown('<div class="security-badge">HIPAA Compliant</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("📈 Biomarker Trends")
        trend_data = pd.DataFrame({
            'Month': ['Jan','Feb','Mar','Apr','May','Jun'],
            'Glucose': [98,102,99,101,97,95],
            'Cholesterol': [195,202,198,205,192,188],
            'Vitamin D': [28,31,29,33,35,38]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_data['Month'], y=trend_data['Glucose'], name='Glucose', line=dict(color='#FF6B6B', width=3)))
        fig.add_trace(go.Scatter(x=trend_data['Month'], y=trend_data['Cholesterol'], name='Cholesterol', line=dict(color='#4ECDC4', width=3)))
        fig.add_trace(go.Scatter(x=trend_data['Month'], y=trend_data['Vitamin D'], name='Vitamin D', line=dict(color='#45B7D1', width=3)))
        fig.update_layout(title="Monthly Biomarker Averages", xaxis_title="Month", yaxis_title="Level", height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Export Data", trend_data.to_csv(index=False).encode(), "biomarker_trends.csv", "text/csv")

    with col2:
        st.subheader("🚀 Quick Actions")
        if st.button("📁 Upload Data", use_container_width=True):
            st.session_state.page = "Data Analysis"
            st.rerun()
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation in progress...")
        if st.button("🔍 Data Quality Check", use_container_width=True):
            st.warning("Running data quality assessment...")
        st.subheader("🔔 Recent Activity")
        for activity in [
            "Pipeline completed - 2 minutes ago",
            "New model trained - 1 hour ago",
            "Data encrypted - 3 hours ago",
            "Security audit passed - 1 day ago"
        ]:
            st.write(f"• {activity}")

# ------------------------------------
# Genomic Analysis Page
# ------------------------------------
def show_genomic_analysis():
    st.markdown('<div class="main-header">🧬 Genomic Analysis</div>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/1081/1081055.png", width=150)

    gene = st.selectbox("Select Gene", ["FTO (Obesity)", "MC4R (Appetite)", "APOE (Cholesterol)", "TCF7L2 (Glucose)"])
    variant_type = st.radio("Variant Type", ["SNPs", "Indels", "CNVs"])

    variants_data = pd.DataFrame({
        'Variant': [f'rs{np.random.randint(100000, 999999)}' for _ in range(50)],
        'Frequency': np.random.uniform(0, 1, 50),
        'Impact': np.random.choice(['Low', 'Moderate', 'High'], 50),
        'Chromosome': [f'Chr {i}' for i in np.random.randint(1, 23, 50)]
    })

    st.subheader("Variant Frequency Distribution")
    fig = px.scatter(variants_data, x='Frequency', y='Impact', color='Chromosome', size='Frequency',
                     title=f"Variant Frequency by Impact for {gene}", hover_data=['Variant'])
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Export Variant Data", variants_data.to_csv(index=False).encode(), "variant_data.csv", "text/csv")

# ------------------------------------
# Model Training Page
# ------------------------------------
def show_model_training():
    st.markdown('<div class="main-header">🤖 Model Training Center</div>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=150)

    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox("Model Type", ["Random Forest", "Logistic Regression", "Gradient Boosting", "Neural Network"])
        target_variable = st.selectbox("Target Variable", ["Elevated Glucose", "High Cholesterol", "Vitamin D Deficiency", "Obesity Risk"])
    with col2:
        feature_set = st.multiselect("Feature Selection", ["Demographics", "Nutrition", "Biomarkers", "Genetic Variants", "Lifestyle"], default=["Demographics", "Nutrition"])
        test_size = st.slider("Test Set Size", 0.1, 0.5, 0.2, 0.05)

    if st.button("🚀 Train Model", use_container_width=True):
        st.info(f"Training {model_type} model for {target_variable}...")
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress.progress(i + 1)
        st.success("✅ Model training complete! Accuracy: 0.88 | AUC: 0.91")

# ------------------------------------
# Main App
# ------------------------------------
def main():
    load_css()
    if check_authentication():
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = "Home"
        
        # Sidebar Layout
        st.sidebar.title("🧬 Project AEGIS")
        st.sidebar.markdown("<div class='profile-card'><strong>👤 User:</strong> admin<br><small>Biomedical Analyst</small></div>", unsafe_allow_html=True)

        # Navigation
        page = st.sidebar.radio("Navigation", ["Home", "Dashboard", "Data Analysis", "Genomic Analysis", "Model Training"])

        # Page routing
        if page == "Home":
            show_home()
        elif page == "Dashboard":
            show_dashboard()
        elif page == "Data Analysis":
            show_data_analysis()
        elif page == "Genomic Analysis":
            show_genomic_analysis()
        elif page == "Model Training":
            show_model_training()

# Run the app
if __name__ == "__main__":
    main()