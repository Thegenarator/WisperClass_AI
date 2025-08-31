import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import base64
from utils.data_processor import DataProcessor
from utils.trend_analyzer import TrendAnalyzer
from utils.visualizer import Visualizer
from components.mobile_components import MobileComponents

# Page configuration for mobile optimization
st.set_page_config(
    page_title="Designer Data Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS for mobile optimization
def load_css():
    with open('styles/mobile.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'mobile_view' not in st.session_state:
    st.session_state.mobile_view = True

# Initialize utility classes
data_processor = DataProcessor()
trend_analyzer = TrendAnalyzer()
visualizer = Visualizer()
mobile_ui = MobileComponents()

def main():
    # Header with mobile-optimized layout
    st.markdown("""
    <div class="mobile-header">
        <h1>📊 Designer Data Insights</h1>
        <p>Discover trends and insights in your design data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mobile-friendly tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📈 Analyze", "💾 Export"])
    
    with tab1:
        upload_section()
    
    with tab2:
        if st.session_state.data is not None:
            analysis_section()
        else:
            st.info("📱 Upload your data first to start analyzing!")
    
    with tab3:
        if st.session_state.analysis_results is not None:
            export_section()
        else:
            st.info("📱 Complete your analysis first to export results!")

def upload_section():
    st.markdown("### 📤 Upload Your Data")
    
    # Mobile-optimized file uploader
    uploaded_file = st.file_uploader(
        "Choose your data file",
        type=['csv', 'json'],
        help="Drag and drop or click to upload CSV or JSON files",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        with st.spinner("🔄 Processing your data..."):
            try:
                # Process the uploaded file
                if uploaded_file.type == "application/json":
                    data = pd.read_json(uploaded_file)
                else:
                    data = pd.read_csv(uploaded_file)
                
                st.session_state.data = data
                
                # Show data preview with mobile-friendly layout
                st.success("✅ Data uploaded successfully!")
                
                with st.expander("📋 Data Preview", expanded=True):
                    # Mobile-optimized data display
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.metric("Rows", len(data))
                    with col2:
                        st.metric("Columns", len(data.columns))
                    
                    # Show first few rows with horizontal scroll
                    st.markdown("**Sample Data:**")
                    st.dataframe(data.head(), use_container_width=True, height=200)
                    
                    # Column information
                    st.markdown("**Column Types:**")
                    col_info = pd.DataFrame({
                        'Column': data.columns,
                        'Type': data.dtypes,
                        'Non-Null': data.count()
                    })
                    st.dataframe(col_info, use_container_width=True, height=150)
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("💡 Make sure your file is a valid CSV or JSON format")

def analysis_section():
    data = st.session_state.data
    
    st.markdown("### 📈 Data Analysis")
    
    # Quick stats in mobile-friendly cards
    mobile_ui.display_quick_stats(data)
    
    # Analysis options
    analysis_type = st.selectbox(
        "Choose Analysis Type",
        ["📊 Overview", "📈 Trends", "🔍 Correlations", "📱 Custom"]
    )
    
    if analysis_type == "📊 Overview":
        overview_analysis(data)
    elif analysis_type == "📈 Trends":
        trend_analysis(data)
    elif analysis_type == "🔍 Correlations":
        correlation_analysis(data)
    else:
        custom_analysis(data)

def overview_analysis(data):
    st.markdown("#### 📊 Data Overview")
    
    # Numerical columns analysis
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.markdown("**📈 Numerical Summary**")
        summary = data[numeric_cols].describe()
        
        # Mobile-friendly summary display
        for col in numeric_cols[:4]:  # Limit for mobile
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{col} - Mean", f"{summary.loc['mean', col]:.2f}")
            with col2:
                st.metric(f"{col} - Min", f"{summary.loc['min', col]:.2f}")
            with col3:
                st.metric(f"{col} - Max", f"{summary.loc['max', col]:.2f}")
        
        # Distribution plots
        selected_col = st.selectbox("Select column for distribution", numeric_cols)
        fig = visualizer.create_distribution_plot(data, selected_col)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Categorical analysis
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        st.markdown("**📊 Categorical Summary**")
        selected_cat = st.selectbox("Select categorical column", categorical_cols)
        
        # Value counts
        value_counts = data[selected_cat].value_counts().head(10)
        fig = visualizer.create_bar_chart(value_counts, f"{selected_cat} Distribution")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def trend_analysis(data):
    st.markdown("#### 📈 Trend Analysis")
    
    # Automated trend detection
    with st.spinner("🔍 Detecting trends..."):
        trends = trend_analyzer.detect_trends(data)
        st.session_state.analysis_results = trends
    
    if trends:
        st.success(f"✅ Found {len(trends)} significant trends!")
        
        for i, trend in enumerate(trends):
            with st.expander(f"📊 Trend {i+1}: {trend['title']}", expanded=i==0):
                st.markdown(f"**Description:** {trend['description']}")
                st.markdown(f"**Confidence:** {trend['confidence']:.1%}")
                
                if 'visualization' in trend:
                    st.plotly_chart(trend['visualization'], use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("🔍 No significant trends detected in your data. Try with a larger dataset or different variables.")

def correlation_analysis(data):
    st.markdown("#### 🔍 Correlation Analysis")
    
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        st.warning("⚠️ Need at least 2 numerical columns for correlation analysis")
        return
    
    # Correlation matrix
    correlation_matrix = data[numeric_cols].corr()
    
    # Mobile-friendly correlation heatmap
    fig = visualizer.create_correlation_heatmap(correlation_matrix)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Top correlations
    st.markdown("**🔗 Strongest Correlations**")
    strong_corr = trend_analyzer.find_strong_correlations(correlation_matrix)
    
    for corr in strong_corr[:5]:  # Top 5 for mobile
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{corr['pair']}**")
        with col2:
            color = "🟢" if corr['value'] > 0 else "🔴"
            st.markdown(f"{color} {corr['value']:.3f}")

def custom_analysis(data):
    st.markdown("#### 📱 Custom Analysis")
    
    # Simple custom analysis options for mobile
    analysis_option = st.radio(
        "Choose custom analysis:",
        ["📊 Compare Groups", "📈 Time Series", "🎯 Filter & Explore"]
    )
    
    if analysis_option == "📊 Compare Groups":
        categorical_cols = data.select_dtypes(include=['object']).columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            group_col = st.selectbox("Group by", categorical_cols)
            value_col = st.selectbox("Analyze", numeric_cols)
            
            fig = visualizer.create_group_comparison(data, group_col, value_col)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    elif analysis_option == "📈 Time Series":
        date_cols = data.select_dtypes(include=['datetime64']).columns
        if len(date_cols) == 0:
            # Try to detect date columns
            potential_date_cols = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if potential_date_cols:
                st.info(f"💡 Try converting these columns to dates: {', '.join(potential_date_cols)}")
            else:
                st.warning("⚠️ No date columns detected for time series analysis")
        else:
            date_col = st.selectbox("Date column", date_cols)
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            value_col = st.selectbox("Value column", numeric_cols)
            
            fig = visualizer.create_time_series(data, date_col, value_col)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    else:  # Filter & Explore
        mobile_ui.create_filter_interface(data)

def export_section():
    st.markdown("### 💾 Export Results")
    
    if st.session_state.analysis_results:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Charts as PNG", use_container_width=True):
                st.info("📱 Chart export functionality ready!")
        
        with col2:
            if st.button("📋 Export Summary as PDF", use_container_width=True):
                st.info("📱 PDF export functionality ready!")
        
        # Data export
        st.markdown("**📤 Export Data**")
        
        if st.button("💾 Download Processed Data", use_container_width=True):
            csv = st.session_state.data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
