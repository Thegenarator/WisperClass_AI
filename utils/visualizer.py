import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class Visualizer:
    """Create mobile-optimized visualizations for design insights"""
    
    def __init__(self):
        # Mobile-friendly color palette for designers
        self.color_palette = [
            '#6366f1',  # Indigo
            '#ec4899',  # Pink
            '#10b981',  # Emerald
            '#f59e0b',  # Amber
            '#ef4444',  # Red
            '#8b5cf6',  # Violet
            '#06b6d4',  # Cyan
            '#84cc16',  # Lime
        ]
        
        # Mobile-optimized layout defaults
        self.mobile_layout = {
            'height': 350,
            'margin': dict(l=30, r=30, t=50, b=30),
            'font': dict(size=12),
            'template': 'plotly_white'
        }
    
    def create_distribution_plot(self, data: pd.DataFrame, column: str) -> go.Figure:
        """Create mobile-friendly distribution plot"""
        col_data = data[column].dropna()
        
        # Create histogram with density curve
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=col_data,
                nbinsx=20,
                name="Distribution",
                marker_color=self.color_palette[0],
                opacity=0.7
            )
        )
        
        # Add density curve if enough data points
        if len(col_data) > 50:
            try:
                from scipy import stats
                density = stats.gaussian_kde(col_data)
                xs = np.linspace(col_data.min(), col_data.max(), 100)
                fig.add_trace(
                    go.Scatter(
                        x=xs,
                        y=density(xs) * len(col_data) * (col_data.max() - col_data.min()) / 20,
                        mode='lines',
                        name='Density',
                        line=dict(color=self.color_palette[1], width=2)
                    ),
                    secondary_y=True
                )
            except:
                pass
        
        fig.update_layout(
            title=f"📊 {column.title()} Distribution",
            xaxis_title=column.title(),
            yaxis_title="Count",
            **self.mobile_layout
        )
        
        return fig
    
    def create_bar_chart(self, data: pd.Series, title: str) -> go.Figure:
        """Create mobile-optimized bar chart"""
        fig = px.bar(
            x=data.values,
            y=data.index,
            orientation='h',
            title=f"📊 {title}",
            color=data.values,
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(
            **self.mobile_layout,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame) -> go.Figure:
        """Create mobile-friendly correlation heatmap"""
        fig = px.imshow(
            correlation_matrix,
            aspect='auto',
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1,
            title="🔗 Correlation Matrix"
        )
        
        # Add correlation values as text
        annotations = []
        for i, row in enumerate(correlation_matrix.index):
            for j, col in enumerate(correlation_matrix.columns):
                value = correlation_matrix.iloc[i, j]
                annotations.append(
                    dict(
                        x=j, y=i,
                        text=f"{value:.2f}",
                        showarrow=False,
                        font=dict(color="white" if abs(value) > 0.5 else "black", size=10)
                    )
                )
        
        fig.update_layout(
            annotations=annotations,
            **self.mobile_layout,
            height=min(400, len(correlation_matrix) * 40 + 100)
        )
        
        return fig
    
    def create_group_comparison(self, data: pd.DataFrame, group_col: str, value_col: str) -> go.Figure:
        """Create group comparison visualization"""
        # Box plot for comparing groups
        fig = px.box(
            data,
            x=group_col,
            y=value_col,
            title=f"📊 {value_col.title()} by {group_col.title()}",
            color=group_col,
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            **self.mobile_layout,
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        return fig
    
    def create_time_series(self, data: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
        """Create time series visualization"""
        # Sort data by date
        data_sorted = data.sort_values(date_col)
        
        fig = px.line(
            data_sorted,
            x=date_col,
            y=value_col,
            title=f"📈 {value_col.title()} Over Time",
            markers=True
        )
        
        fig.update_traces(
            line_color=self.color_palette[0],
            line_width=3,
            marker_size=5
        )
        
        # Add trend line
        try:
            from sklearn.linear_model import LinearRegression
            
            # Prepare data for trend line
            x_numeric = pd.to_numeric(data_sorted[date_col].values, errors='coerce')
            y_values = data_sorted[value_col].values
            
            # Remove NaN values
            mask = ~(np.isnan(x_numeric) | np.isnan(y_values))
            if mask.sum() > 2:
                x_clean = x_numeric[mask].reshape(-1, 1)
                y_clean = y_values[mask]
                
                lr = LinearRegression()
                lr.fit(x_clean, y_clean)
                
                trend_y = lr.predict(x_clean)
                
                fig.add_trace(
                    go.Scatter(
                        x=data_sorted[date_col][mask],
                        y=trend_y,
                        mode='lines',
                        name='Trend',
                        line=dict(color=self.color_palette[1], width=2, dash='dash')
                    )
                )
        except:
            pass
        
        fig.update_layout(
            **self.mobile_layout,
            hovermode='x unified'
        )
        
        return fig
    
    def create_scatter_plot(self, data: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
        """Create scatter plot with optional color coding"""
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"🎯 {y_col.title()} vs {x_col.title()}",
            color_discrete_sequence=self.color_palette,
            trendline="ols" if color_col is None else None
        )
        
        fig.update_layout(
            **self.mobile_layout,
            showlegend=bool(color_col)
        )
        
        return fig
    
    def create_pie_chart(self, data: pd.Series, title: str, max_categories: int = 8) -> go.Figure:
        """Create mobile-optimized pie chart"""
        # Limit categories for mobile display
        if len(data) > max_categories:
            top_categories = data.head(max_categories - 1)
            others_sum = data.iloc[max_categories - 1:].sum()
            if others_sum > 0:
                top_categories = pd.concat([top_categories, pd.Series([others_sum], index=['Others'])])
            data = top_categories
        
        fig = px.pie(
            values=data.values,
            names=data.index,
            title=f"🥧 {title}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=10
        )
        
        fig.update_layout(
            **self.mobile_layout,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    def create_multi_metric_dashboard(self, metrics: Dict[str, float]) -> go.Figure:
        """Create a mobile-friendly metrics dashboard"""
        # Create subplots for metrics
        n_metrics = len(metrics)
        cols = min(2, n_metrics)
        rows = (n_metrics + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=list(metrics.keys()),
            specs=[[{"type": "indicator"}] * cols for _ in range(rows)]
        )
        
        for i, (metric_name, value) in enumerate(metrics.items()):
            row = i // cols + 1
            col = i % cols + 1
            
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=value,
                    title={"text": metric_name},
                    number={'font': {'size': 20, 'color': self.color_palette[i % len(self.color_palette)]}},
                    domain={'row': row-1, 'column': col-1}
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            height=150 * rows,
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(size=12)
        )
        
        return fig
