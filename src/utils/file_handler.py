"""File handling utilities"""
import os
import pandas as pd
import numpy as np
import csv


class FileHandler:
    """Handles file reading and format detection"""
    
    SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.txt']
    
    @staticmethod
    def detect_delimiter(filepath, num_lines=5):
        """
        Detect the delimiter used in a CSV/TXT file
        
        Args:
            filepath: Path to file
            num_lines: Number of lines to analyze
        
        Returns:
            Detected delimiter
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sample = []
                for _ in range(num_lines):
                    line = f.readline()
                    if line:
                        sample.append(line)
                    else:
                        break
                
                if not sample:
                    return ','
                
                # Use csv.Sniffer to detect delimiter
                sniffer = csv.Sniffer()
                sample_text = '\n'.join(sample)
                
                try:
                    delimiter = sniffer.sniff(sample_text).delimiter
                    return delimiter
                except:
                    # Fallback: count occurrences of common delimiters
                    delimiters = [',', ';', '\t', '|', ' ']
                    counts = {}
                    
                    for delimiter in delimiters:
                        count = sum(line.count(delimiter) for line in sample)
                        counts[delimiter] = count
                    
                    # Return the most common delimiter
                    most_common = max(counts.items(), key=lambda x: x[1])
                    
                    # If space is most common and count is high, use regex for multiple spaces
                    if most_common[0] == ' ' and most_common[1] > 10:
                        return r'\s+'
                    
                    return most_common[0] if most_common[1] > 0 else ','
        
        except Exception as e:
            print(f"Warning: Could not detect delimiter, using comma. Error: {e}")
            return ','
    
    @staticmethod
    def read_file(filepath, has_header=True):
        """Read data file and return DataFrame"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext not in FileHandler.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {ext}")
        
        try:
            if ext == '.csv':
                # Detect delimiter automatically
                delimiter = FileHandler.detect_delimiter(filepath)
                
                if has_header:
                    df = pd.read_csv(filepath, sep=delimiter, engine='python')
                else:
                    df = pd.read_csv(filepath, sep=delimiter, header=None, engine='python')
            
            elif ext in ['.xlsx', '.xls']:
                if has_header:
                    df = pd.read_excel(filepath, engine='openpyxl' if ext == '.xlsx' else None)
                else:
                    df = pd.read_excel(filepath, header=None, engine='openpyxl' if ext == '.xlsx' else None)
            
            elif ext == '.txt':
                # Detect delimiter for text files
                delimiter = FileHandler.detect_delimiter(filepath)
                
                if has_header:
                    df = pd.read_csv(filepath, sep=delimiter, engine='python')
                else:
                    df = pd.read_csv(filepath, sep=delimiter, header=None, engine='python')
            
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            return df
        
        except Exception as e:
            raise Exception(f"Error reading file {filepath}: {str(e)}")
    
    @staticmethod
    def detect_columns(df, time_col_idx=1, signal_col_idx=2):
        """
        Detect time and signal columns
        
        Args:
            df: DataFrame
            time_col_idx: Default time column index (1-based, will be converted to 0-based)
            signal_col_idx: Default signal column index (1-based, will be converted to 0-based)
        
        Returns:
            Tuple of (time_column, signal_column)
        """
        time_keywords = ['time', 'retention', 'rt', 'min', 'minutes', 'x']
        signal_keywords = ['signal', 'intensity', 'absorbance', 'au', 'mau', 'y', 'response']
        
        time_col = None
        signal_col = None
        
        # If columns have names (not integers), try to match by keyword
        if not all(isinstance(col, int) for col in df.columns):
            for col in df.columns:
                col_lower = str(col).lower().strip()
                
                if time_col is None:
                    if any(keyword in col_lower for keyword in time_keywords):
                        time_col = col
                
                if signal_col is None:
                    if any(keyword in col_lower for keyword in signal_keywords):
                        signal_col = col
        
        # Convert 1-based indices to 0-based
        time_idx_0based = time_col_idx - 1 if time_col_idx > 0 else 0
        signal_idx_0based = signal_col_idx - 1 if signal_col_idx > 0 else 1
        
        # Fallback to index-based detection
        if time_col is None:
            if len(df.columns) > time_idx_0based:
                time_col = df.columns[time_idx_0based]
            else:
                time_col = df.columns[0]
        
        if signal_col is None:
            if len(df.columns) > signal_idx_0based:
                signal_col = df.columns[signal_idx_0based]
            elif len(df.columns) > 1:
                signal_col = df.columns[1]
            else:
                raise ValueError("DataFrame must have at least 2 columns")
        
        return time_col, signal_col
    
    @staticmethod
    def get_files_from_folder(folder_path, extensions=None):
        """Get all supported files from a folder"""
        if extensions is None:
            extensions = FileHandler.SUPPORTED_EXTENSIONS
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise ValueError(f"Not a directory: {folder_path}")
        
        files = []
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(folder_path, file))
        
        return sorted(files)
    
    @staticmethod
    def validate_file(filepath):
        """Validate that file exists and has supported format"""
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        if not os.path.isfile(filepath):
            return False, "Path is not a file"
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in FileHandler.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format: {ext}"
        
        return True, "Valid"
    
    @staticmethod
    def preview_file(filepath, num_rows=5, has_header=True):
        """
        Preview first few rows of a file
        
        Args:
            filepath: Path to file
            num_rows: Number of rows to preview
            has_header: Whether file has header
        
        Returns:
            DataFrame with preview data
        """
        try:
            df = FileHandler.read_file(filepath, has_header)
            return df.head(num_rows)
        except Exception as e:
            raise Exception(f"Error previewing file: {str(e)}")