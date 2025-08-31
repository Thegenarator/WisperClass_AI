import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    """Automated trend detection optimized for designer insights"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.correlation_threshold = 0.5
    
    def detect_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect significant trends and patterns in the data"""
        trends = []
        
        # Numerical trends
        numeric_trends = self._analyze_numeric_trends(data)
        trends.extend(numeric_trends)
        
        # Categorical patterns
        categorical_trends = self._analyze_categorical_patterns(data)
        trends.extend(categorical_trends)
        
        # Time-based trends
        time_trends = self._analyze_time_trends(data)
        trends.extend(time_trends)
        
        # Correlation insights
        correlation_trends = self._analyze_correlations(data)
        trends.extend(correlation_trends)
        
        # Sort by confidence
        trends.sort(key=lambda x: x['confidence'], reverse=True)
        
        return trends[:10]  # Return top 10 trends for mobile
    
    def _analyze_numeric_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze trends in numerical columns"""
        trends = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            try:
                col_data = data[col].dropna()
                if len(col_data) < 10:
                    continue
                
                # Distribution analysis
                skewness = stats.skew(col_data)
                kurtosis = stats.kurtosis(col_data)
                
                # Outlier detection
                q1, q3 = np.percentile(col_data, [25, 75])
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)]
                outlier_ratio = len(outliers) / len(col_data)
                
                # Generate insights
                if abs(skewness) > 1:
                    direction = "right" if skewness > 0 else "left"
                    trends.append({
                        'title': f"{col.title()} Distribution",
                        'description': f"The {col} values are heavily skewed to the {direction} (skewness: {skewness:.2f})",
                        'confidence': min(abs(skewness) / 3, 1.0),
                        'type': 'distribution',
                        'column': col,
                        'visualization': self._create_distribution_viz(col_data, col)
                    })
                
                if outlier_ratio > 0.05:  # More than 5% outliers
                    trends.append({
                        'title': f"{col.title()} Outliers",
                        'description': f"{outlier_ratio:.1%} of {col} values are outliers, indicating potential data quality issues or interesting edge cases",
                        'confidence': min(outlier_ratio * 2, 1.0),
                        'type': 'outliers',
                        'column': col,
                        'visualization': self._create_outlier_viz(col_data, col, outliers)
                    })
                
            except Exception as e:
                continue
        
        return trends
    
    def _analyze_categorical_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze patterns in categorical columns"""
        trends = []
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            try:
                value_counts = data[col].value_counts()
                if len(value_counts) < 2:
                    continue
                
                # Dominance analysis
                top_value_ratio = value_counts.iloc[0] / len(data)
                
                if top_value_ratio > 0.8:
                    trends.append({
                        'title': f"{col.title()} Dominance",
                        'description': f"'{value_counts.index[0]}' represents {top_value_ratio:.1%} of all {col} values, showing strong dominance",
                        'confidence': top_value_ratio,
                        'type': 'dominance',
                        'column': col,
                        'visualization': self._create_category_viz(value_counts, col)
                    })
                
                # Diversity analysis
                elif len(value_counts) > 10 and value_counts.iloc[0] / value_counts.iloc[-1] > 10:
                    trends.append({
                        'title': f"{col.title()} Diversity",
                        'description': f"{col} shows high diversity with {len(value_counts)} unique values and uneven distribution",
                        'confidence': 0.7,
                        'type': 'diversity',
                        'column': col,
                        'visualization': self._create_category_viz(value_counts.head(10), col)
                    })
                
            except Exception as e:
                continue
        
        return trends
    
    def _analyze_time_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze time-based trends"""
        trends = []
        
        # Find date columns
        date_cols = data.select_dtypes(include=['datetime64']).columns
        
        for date_col in date_cols:
            try:
                # Sort by date
                data_sorted = data.sort_values(date_col)
                
                # Analyze numeric columns over time
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                
                for num_col in numeric_cols:
                    if len(data_sorted[num_col].dropna()) < 10:
                        continue
                    
                    # Calculate trend
                    x = np.arange(len(data_sorted))
                    y = data_sorted[num_col].values
                    
                    # Remove NaN values
                    mask = ~np.isnan(y)
                    if mask.sum() < 10:
                        continue
                    
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], y[mask])
                    
                    if abs(r_value) > 0.5 and p_value < 0.05:
                        direction = "increasing" if slope > 0 else "decreasing"
                        trends.append({
                            'title': f"{num_col.title()} Time Trend",
                            'description': f"{num_col} shows a {direction} trend over time (R² = {r_value**2:.3f})",
                            'confidence': abs(r_value),
                            'type': 'time_trend',
                            'columns': [date_col, num_col],
                            'visualization': self._create_time_trend_viz(data_sorted, date_col, num_col)
                        })
                
            except Exception as e:
                continue
        
        return trends
    
    def _analyze_correlations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze correlations between variables"""
        trends = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return trends
        
        try:
            correlation_matrix = data[numeric_cols].corr()
            
            # Find strong correlations
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    corr_value = correlation_matrix.loc[col1, col2]
                    
                    if abs(corr_value) > self.correlation_threshold:
                        relationship = "positive" if corr_value > 0 else "negative"
                        strength = "strong" if abs(corr_value) > 0.7 else "moderate"
                        
                        trends.append({
                            'title': f"{col1.title()} vs {col2.title()}",
                            'description': f"{strength.title()} {relationship} correlation between {col1} and {col2} (r = {corr_value:.3f})",
                            'confidence': abs(corr_value),
                            'type': 'correlation',
                            'columns': [col1, col2],
                            'visualization': self._create_correlation_viz(data, col1, col2, corr_value)
                        })
        
        except Exception as e:
            pass
        
        return trends
    
    def find_strong_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Find and rank strong correlations"""
        correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                value = correlation_matrix.iloc[i, j]
                
                if abs(value) >= threshold:
                    correlations.append({
                        'pair': f"{col1} ↔ {col2}",
                        'value': value,
                        'strength': 'Strong' if abs(value) > 0.7 else 'Moderate'
                    })
        
        return sorted(correlations, key=lambda x: abs(x['value']), reverse=True)
    
    def _create_distribution_viz(self, data: pd.Series, column: str) -> go.Figure:
        """Create mobile-friendly distribution visualization"""
        fig = px.histogram(
            x=data,
            title=f"{column.title()} Distribution",
            template="plotly_white"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    
    def _create_outlier_viz(self, data: pd.Series, column: str, outliers: pd.Series) -> go.Figure:
        """Create outlier visualization"""
        fig = px.box(
            y=data,
            title=f"{column.title()} Outliers",
            template="plotly_white"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    
    def _create_category_viz(self, value_counts: pd.Series, column: str) -> go.Figure:
        """Create categorical visualization"""
        fig = px.bar(
            x=value_counts.values,
            y=value_counts.index,
            orientation='h',
            title=f"{column.title()} Distribution",
            template="plotly_white"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    
    def _create_time_trend_viz(self, data: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
        """Create time trend visualization"""
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            title=f"{value_col.title()} Over Time",
            template="plotly_white"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    
    def _create_correlation_viz(self, data: pd.DataFrame, col1: str, col2: str, corr_value: float) -> go.Figure:
        """Create correlation scatter plot"""
        fig = px.scatter(
            data,
            x=col1,
            y=col2,
            title=f"{col1.title()} vs {col2.title()} (r = {corr_value:.3f})",
            template="plotly_white",
            trendline="ols"
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
