"""File processor for HPLC data"""
import os
from utils.file_handler import FileHandler
from utils.data_validator import DataValidator
from core.auc_calculator import AUCCalculator


class FileProcessor:
    """Process HPLC data files"""
    
    def __init__(self, has_header=True, time_col_idx=1, signal_col_idx=2,
                 baseline_method='None', noise_method='None',
                 baseline_params=None, noise_params=None):
        """
        Initialize FileProcessor
        
        Args:
            has_header: Whether files have header row
            time_col_idx: Time column index (1-based)
            signal_col_idx: Signal column index (1-based)
            baseline_method: Baseline correction method
            noise_method: Noise correction method
            baseline_params: Parameters for baseline correction
            noise_params: Parameters for noise correction
        """
        self.has_header = has_header
        self.time_col_idx = time_col_idx  # Store as 1-based
        self.signal_col_idx = signal_col_idx  # Store as 1-based
        self.file_handler = FileHandler()
        self.validator = DataValidator()
        self.auc_calculator = AUCCalculator(
            baseline_method=baseline_method,
            noise_method=noise_method,
            baseline_params=baseline_params,
            noise_params=noise_params
        )
    
    def process_single_file(self, filepath, peak_ranges, peak_names, 
                           include_in_total=None, custom_total_range=None):
        """
        Process a single file
        
        Args:
            filepath: Path to file
            peak_ranges: List of (start, end) tuples
            peak_names: List of peak names
            include_in_total: List of boolean values for peaks to include in total
            custom_total_range: Tuple of (start, end, name) for custom total peak
        
        Returns:
            Dictionary with results
        """

        df = self.file_handler.read_file(filepath, self.has_header)

        time_col, signal_col = self.file_handler.detect_columns(
            df, self.time_col_idx, self.signal_col_idx
        )
        
        self.validator.validate_dataframe(df, time_col, signal_col)
        
        time = df[time_col].values
        signal = df[signal_col].values

        results = self.auc_calculator.calculate_multiple_peaks(
            time, signal, peak_ranges, peak_names, include_in_total, custom_total_range
        )
        
        results['filename'] = os.path.basename(filepath)
        
        return results
    
    def process_folder(self, folder_path, peak_ranges, peak_names, 
                      include_in_total=None, custom_total_range=None, progress_callback=None):
        """
        Process all files in a folder
        
        Args:
            folder_path: Path to folder or a single file
            peak_ranges: List of (start, end) tuples
            peak_names: List of peak names
            include_in_total: List of boolean values for peaks to include in total
            custom_total_range: Tuple of (start, end, name) for custom total peak
            progress_callback: Callback function for progress updates
        
        Returns:
            List of result dictionaries
        """
        print(f"\nDEBUG process_folder - Input path: {folder_path}")
        print(f"DEBUG process_folder - Is file: {os.path.isfile(folder_path)}")
        print(f"DEBUG process_folder - Is dir: {os.path.isdir(folder_path)}")
        
        if os.path.isfile(folder_path):
            print(f"DEBUG - File detected, extracting parent directory")
            original_file = folder_path
            folder_path = os.path.dirname(folder_path)
            print(f"DEBUG - Original file: {original_file}")
            print(f"DEBUG - New folder path: {folder_path}")
            
            if not os.path.isdir(folder_path):
                raise ValueError(f"Invalid path: {folder_path}")
    
        if not os.path.isdir(folder_path):
            raise ValueError(f"Not a valid directory: {folder_path}")
        
        files = self.file_handler.get_files_from_folder(folder_path)
        print(f"DEBUG - Found {len(files)} files in folder: {folder_path}")
        for f in files:
            print(f"  - {os.path.basename(f)}")
        
        if not files:
            raise ValueError(f"No supported files found in {folder_path}")
        
        results = []
        total_files = len(files)
        
        for idx, filepath in enumerate(files):
            try:
                print(f"\nDEBUG - Processing file {idx+1}/{total_files}: {os.path.basename(filepath)}")
                result = self.process_single_file(
                    filepath, peak_ranges, peak_names, include_in_total, custom_total_range
                )
                results.append(result)
                
                if progress_callback:
                    progress_callback(idx + 1, total_files, os.path.basename(filepath), True)
            
            except Exception as e:
                print(f"DEBUG - Error processing {os.path.basename(filepath)}: {str(e)}")
                error_result = {
                    'filename': os.path.basename(filepath),
                    'error': str(e)
                }
                results.append(error_result)
                
                if progress_callback:
                    progress_callback(idx + 1, total_files, os.path.basename(filepath), False)
        
        print(f"\nDEBUG - Completed processing {len(results)} files")
        return results