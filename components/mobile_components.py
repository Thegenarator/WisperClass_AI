import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

class MobileComponents:
    """Mobile-optimized UI components for the data analysis tool"""
    
    def __init__(self):
        self.primary_color = "#6366f1"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"
    
    def display_quick_stats(self, data: pd.DataFrame):
        """Display key statistics in mobile-friendly cards"""
        st.markdown("#### 📊 Quick Stats")
        
        # Main metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Rows",
                value=f"{len(data):,}",
                help="Total number of data points"
            )
        
        with col2:
            st.metric(
                label="📊 Columns", 
                value=len(data.columns),
                help="Number of data fields"
            )
        
        with col3:
            numeric_cols = len(data.select_dtypes(include=['number']).columns)
            st.metric(
                label="🔢 Numeric",
                value=numeric_cols,
                help="Numerical columns available"
            )
        
        with col4:
            missing_pct = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
            st.metric(
                label="❓ Missing",
                value=f"{missing_pct:.1f}%",
                help="Percentage of missing values"
            )
        
        # Data quality indicators
        if missing_pct > 10:
            st.warning(f"⚠️ High missing data detected ({missing_pct:.1f}%)")
        elif missing_pct > 5:
            st.info(f"ℹ️ Some missing data present ({missing_pct:.1f}%)")
        else:
            st.success("✅ Good data quality")
    
    def create_mobile_selector(self, options: List[str], label: str, key: str = None) -> str:
        """Create mobile-optimized selector"""
        if len(options) <= 4:
            # Use radio buttons for few options
            return st.radio(
                label,
                options,
                key=key,
                horizontal=True if len(options) <= 2 else False
            )
        else:
            # Use selectbox for many options
            return st.selectbox(label, options, key=key)
    
    def create_filter_interface(self, data: pd.DataFrame):
        """Create mobile-friendly data filtering interface"""
        st.markdown("#### 🔍 Filter & Explore")
        
        # Column selector
        selected_columns = st.multiselect(
            "Select columns to analyze",
            options=data.columns.tolist(),
            default=data.columns.tolist()[:5],  # Limit default selection for mobile
            help="Choose which columns to include in your analysis"
        )
        
        if not selected_columns:
            st.warning("📱 Please select at least one column to continue")
            return
        
        filtered_data = data[selected_columns].copy()
        
        # Quick filters for categorical columns
        categorical_cols = filtered_data.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) > 0:
            st.markdown("**🏷️ Quick Filters**")
            
            for col in categorical_cols[:3]:  # Limit to 3 for mobile
                unique_values = filtered_data[col].unique()
                
                if len(unique_values) <= 10:  # Only show filter if manageable number of options
                    selected_values = st.multiselect(
                        f"Filter {col}",
                        options=unique_values,
                        default=unique_values,
                        key=f"filter_{col}"
                    )
                    
                    if selected_values:
                        filtered_data = filtered_data[filtered_data[col].isin(selected_values)]
        
        # Numeric range filters
        numeric_cols = filtered_data.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            st.markdown("**🔢 Range Filters**")
            
            for col in numeric_cols[:2]:  # Limit to 2 for mobile
                col_min, col_max = filtered_data[col].min(), filtered_data[col].max()
                
                if col_min != col_max:  # Only show if there's a range
                    range_values = st.slider(
                        f"{col} range",
                        min_value=float(col_min),
                        max_value=float(col_max),
                        value=(float(col_min), float(col_max)),
                        key=f"range_{col}"
                    )
                    
                    filtered_data = filtered_data[
                        (filtered_data[col] >= range_values[0]) & 
                        (filtered_data[col] <= range_values[1])
                    ]
        
        # Show filtered results
        if len(filtered_data) != len(data):
            st.info(f"📊 Showing {len(filtered_data)} of {len(data)} rows after filtering")
        
        # Display filtered data
        with st.expander("📋 Filtered Data Preview", expanded=False):
            st.dataframe(filtered_data.head(100), use_container_width=True, height=200)
        
        # Quick visualization of filtered data
        if len(filtered_data) > 0:
            self.create_quick_viz(filtered_data)
        
        return filtered_data
    
    def create_quick_viz(self, data: pd.DataFrame):
        """Create quick visualization for filtered data"""
        st.markdown("**📊 Quick Visualization**")
        
        viz_type = st.selectbox(
            "Choose visualization",
            ["📊 Summary", "📈 Distribution", "🎯 Scatter", "📊 Bar Chart"],
            key="quick_viz_type"
        )
        
        if viz_type == "📊 Summary":
            # Summary statistics
            numeric_data = data.select_dtypes(include=['number'])
            if len(numeric_data.columns) > 0:
                st.dataframe(numeric_data.describe(), use_container_width=True)
            else:
                st.info("No numeric columns for summary statistics")
        
        elif viz_type == "📈 Distribution":
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                selected_col = st.selectbox("Select column", numeric_cols, key="dist_col")
                fig = px.histogram(data, x=selected_col, title=f"{selected_col} Distribution")
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No numeric columns for distribution plot")
        
        elif viz_type == "🎯 Scatter":
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="scatter_y")
                
                fig = px.scatter(data, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Need at least 2 numeric columns for scatter plot")
        
        else:  # Bar Chart
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                selected_col = st.selectbox("Select column", categorical_cols, key="bar_col")
                value_counts = data[selected_col].value_counts().head(10)
                
                fig = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f"{selected_col} Distribution"
                )
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No categorical columns for bar chart")
    
    def create_mobile_progress_bar(self, progress: float, message: str = ""):
        """Create mobile-friendly progress indicator"""
        progress_container = st.container()
        with progress_container:
            if message:
                st.markdown(f"**{message}**")
            
            # Create custom progress bar
            progress_html = f"""
            <div style="
                width: 100%;
                height: 20px;
                background-color: #e5e7eb;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            ">
                <div style="
                    width: {progress * 100}%;
                    height: 100%;
                    background: linear-gradient(90deg, {self.primary_color}, {self.success_color});
                    border-radius: 10px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            st.markdown(f"<center><small>{progress * 100:.1f}% complete</small></center>", unsafe_allow_html=True)
    
    def create_insight_card(self, title: str, description: str, confidence: float, trend_type: str = "info"):
        """Create mobile-optimized insight cards"""
        # Choose icon and color based on trend type
        icons = {
            'distribution': '📊',
            'correlation': '🔗',
            'time_trend': '📈',
            'outliers': '⚠️',
            'dominance': '👑',
            'diversity': '🌈',
            'info': 'ℹ️'
        }
        
        colors = {
            'distribution': self.primary_color,
            'correlation': self.success_color,
            'time_trend': '#8b5cf6',
            'outliers': self.warning_color,
            'dominance': '#ec4899',
            'diversity': '#06b6d4',
            'info': self.primary_color
        }
        
        icon = icons.get(trend_type, '📊')
        color = colors.get(trend_type, self.primary_color)
        
        # Create card HTML
        card_html = f"""
        <div style="
            background: linear-gradient(135deg, {color}15, {color}05);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 24px; margin-right: 12px;">{icon}</span>
                <h4 style="margin: 0; color: {color}; font-weight: 600;">{title}</h4>
            </div>
            <p style="margin: 8px 0; color: #374151; line-height: 1.5;">{description}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
                <small style="color: #6b7280;">Confidence: {confidence:.1%}</small>
                <div style="
                    width: 60px;
                    height: 6px;
                    background-color: #e5e7eb;
                    border-radius: 3px;
                    overflow: hidden;
                ">
                    <div style="
                        width: {confidence * 100}%;
                        height: 100%;
                        background-color: {color};
                        border-radius: 3px;
                    "></div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def create_mobile_tabs(self, tab_names: List[str], icons: List[str] = None) -> str:
        """Create mobile-optimized tab interface"""
        if icons and len(icons) == len(tab_names):
            tab_labels = [f"{icon} {name}" for icon, name in zip(icons, tab_names)]
        else:
            tab_labels = tab_names
        
        # Use Streamlit's built-in tabs but with mobile-friendly styling
        return st.selectbox(
            "Navigation",
            options=tab_labels,
            label_visibility="collapsed"
        )
