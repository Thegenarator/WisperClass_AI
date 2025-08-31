import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import streamlit as st

class DataProcessor:
    """Handles data processing operations optimized for mobile usage"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json']
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate uploaded data and return summary statistics"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        try:
            # Basic validation
            if data.empty:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Dataset is empty")
                return validation_results
            
            # Check for minimum requirements
            if len(data.columns) < 2:
                validation_results['warnings'].append("Dataset has fewer than 2 columns - analysis options may be limited")
            
            # Check data quality
            missing_data = data.isnull().sum()
            if missing_data.sum() > 0:
                validation_results['warnings'].append(f"Dataset contains {missing_data.sum()} missing values")
            
            # Generate summary
            validation_results['summary'] = {
                'rows': len(data),
                'columns': len(data.columns),
                'numeric_columns': len(data.select_dtypes(include=[np.number]).columns),
                'categorical_columns': len(data.select_dtypes(include=['object']).columns),
                'memory_usage': data.memory_usage(deep=True).sum(),
                'missing_values': missing_data.sum()
            }
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def clean_data(self, data: pd.DataFrame, options: Dict[str, Any] = None) -> pd.DataFrame:
        """Clean data with mobile-friendly default options"""
        if options is None:
            options = {
                'remove_duplicates': True,
                'handle_missing': 'drop',
                'standardize_columns': True
            }
        
        cleaned_data = data.copy()
        
        try:
            # Standardize column names for mobile display
            if options.get('standardize_columns', True):
                cleaned_data.columns = [col.strip().replace(' ', '_').lower() for col in cleaned_data.columns]
            
            # Handle missing values
            missing_strategy = options.get('handle_missing', 'drop')
            if missing_strategy == 'drop':
                cleaned_data = cleaned_data.dropna()
            elif missing_strategy == 'fill_numeric':
                numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
                cleaned_data[numeric_cols] = cleaned_data[numeric_cols].fillna(cleaned_data[numeric_cols].median())
            
            # Remove duplicates
            if options.get('remove_duplicates', True):
                initial_rows = len(cleaned_data)
                cleaned_data = cleaned_data.drop_duplicates()
                removed_duplicates = initial_rows - len(cleaned_data)
                if removed_duplicates > 0:
                    st.info(f"ℹ️ Removed {removed_duplicates} duplicate rows")
            
        except Exception as e:
            st.error(f"❌ Error during data cleaning: {str(e)}")
            return data
        
        return cleaned_data
    
    def detect_data_types(self, data: pd.DataFrame) -> Dict[str, str]:
        """Detect and suggest optimal data types for analysis"""
        suggestions = {}
        
        for column in data.columns:
            col_data = data[column]
            
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(col_data):
                suggestions[column] = 'numeric'
                continue
            
            # Check if it's a date
            if self._is_date_column(col_data):
                suggestions[column] = 'datetime'
                continue
            
            # Check if it's categorical
            unique_ratio = col_data.nunique() / len(col_data)
            if unique_ratio < 0.1:  # Less than 10% unique values
                suggestions[column] = 'categorical'
            else:
                suggestions[column] = 'text'
        
        return suggestions
    
    def _is_date_column(self, col_data: pd.Series) -> bool:
        """Check if a column contains date-like data"""
        try:
            # Try to convert a sample to datetime
            sample_size = min(100, len(col_data))
            sample = col_data.dropna().head(sample_size)
            
            if len(sample) == 0:
                return False
            
            # Try parsing dates
            pd.to_datetime(sample, errors='raise')
            return True
        except:
            return False
    
    def get_sample_data(self, data: pd.DataFrame, sample_size: int = 1000) -> pd.DataFrame:
        """Get a sample of data optimized for mobile analysis"""
        if len(data) <= sample_size:
            return data
        
        # Stratified sampling if possible
        try:
            categorical_cols = data.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                # Use the first categorical column for stratification
                return data.groupby(categorical_cols[0]).apply(
                    lambda x: x.sample(min(len(x), sample_size // data[categorical_cols[0]].nunique()))
                ).reset_index(drop=True)
        except:
            pass
        
        # Random sampling as fallback
        return data.sample(n=sample_size, random_state=42).reset_index(drop=True)
    
    def prepare_for_analysis(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Prepare data for analysis with mobile-optimized preprocessing"""
        prep_info = {
            'original_shape': data.shape,
            'transformations': []
        }
        
        # Clean the data
        processed_data = self.clean_data(data)
        prep_info['transformations'].append('data_cleaning')
        
        # Convert data types
        type_suggestions = self.detect_data_types(processed_data)
        for column, suggested_type in type_suggestions.items():
            try:
                if suggested_type == 'datetime':
                    processed_data[column] = pd.to_datetime(processed_data[column])
                    prep_info['transformations'].append(f'converted_{column}_to_datetime')
                elif suggested_type == 'categorical':
                    processed_data[column] = processed_data[column].astype('category')
                    prep_info['transformations'].append(f'converted_{column}_to_category')
            except Exception as e:
                continue  # Skip problematic conversions
        
        # Sample data if too large for mobile processing
        if len(processed_data) > 10000:
            processed_data = self.get_sample_data(processed_data, 5000)
            prep_info['transformations'].append('data_sampling')
        
        prep_info['final_shape'] = processed_data.shape
        
        return processed_data, prep_info
