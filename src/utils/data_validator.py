"""Data validation utilities"""
import os
import pandas as pd
import numpy as np

class DataValidator:
    """Validates data quality and integrity"""
    
    @staticmethod
    def validate_dataframe(df, time_col, signal_col):
        """Validate that DataFrame has required columns and valid data"""
        if df is None or df.empty:
            raise ValueError("DataFrame is empty")
        
        if time_col not in df.columns:
            raise ValueError(f"Time column '{time_col}' not found")
        
        if signal_col not in df.columns:
            raise ValueError(f"Signal column '{signal_col}' not found")
        
        # Check for numeric data
        if not pd.api.types.is_numeric_dtype(df[time_col]):
            try:
                df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
            except:
                raise ValueError(f"Time column '{time_col}' must contain numeric data")
        
        if not pd.api.types.is_numeric_dtype(df[signal_col]):
            try:
                df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
            except:
                raise ValueError(f"Signal column '{signal_col}' must contain numeric data")
        
        # Remove NaN values
        df = df.dropna(subset=[time_col, signal_col])
        
        if df.empty:
            raise ValueError("No valid data points after removing NaN values")
        
        return True
    
    @staticmethod
    def validate_peak_range(df, time_col, xi, xf):
        """Validate peak range is within data bounds"""
        min_time = df[time_col].min()
        max_time = df[time_col].max()
        
        if xi < min_time or xf > max_time:
            raise ValueError(f"Peak range ({xi}, {xf}) is outside data range ({min_time}, {max_time})")
        
        if xi >= xf:
            raise ValueError(f"Start time ({xi}) must be less than end time ({xf})")
        
        return True
    
    @staticmethod
    def check_data_quality(df, time_col, signal_col):
        """Check data quality and return warnings"""
        warnings = []
        
        # Check for duplicate time values
        if df[time_col].duplicated().any():
            warnings.append("Duplicate time values detected")
        
        # Check for negative signals
        if (df[signal_col] < 0).any():
            warnings.append("Negative signal values detected")
        
        # Check data density
        time_range = df[time_col].max() - df[time_col].min()
        num_points = len(df)
        avg_spacing = time_range / num_points if num_points > 1 else 0
        
        if avg_spacing > 0.1:  # Arbitrary threshold
            warnings.append(f"Low data density: avg spacing = {avg_spacing:.3f}")
        
        return warnings

def validate_file_format(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file does not exist: {file_path}")
    
    if file_path.lower().endswith(('.csv', '.xlsx', '.xls', '.txt')):
        return True
    else:
        raise ValueError("Unsupported file format. Please upload a CSV, Excel, or text file.")

def validate_data_integrity(dataframe):
    if dataframe.empty:
        raise ValueError("The data frame is empty. Please check the input file.")
    
    if dataframe.isnull().values.any():
        raise ValueError("The data frame contains NaN values. Please clean the input data.")

def validate_column_headers(dataframe, expected_columns):
    if not all(col in dataframe.columns for col in expected_columns):
        raise ValueError(f"The data frame is missing required columns: {expected_columns}")

def validate_peak_ranges(peak_ranges):
    if not isinstance(peak_ranges, list) or len(peak_ranges) < 1:
        raise ValueError("Peak ranges must be provided as a non-empty list.")
    
    for peak in peak_ranges:
        if not isinstance(peak, tuple) or len(peak) != 2:
            raise ValueError("Each peak range must be a tuple with start and end values.")
        if peak[0] >= peak[1]:
            raise ValueError(f"Invalid peak range: {peak}. Start must be less than end.")

def validate_input_file(file_path, expected_columns=None):
    validate_file_format(file_path)
    
    if file_path.lower().endswith('.csv'):
        dataframe = pd.read_csv(file_path, header=None)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        dataframe = pd.read_excel(file_path, header=None)
    elif file_path.lower().endswith('.txt'):
        dataframe = pd.read_csv(file_path, delimiter='\t', header=None)
    
    validate_data_integrity(dataframe)
    
    if expected_columns:
        validate_column_headers(dataframe, expected_columns)
    
    return dataframe