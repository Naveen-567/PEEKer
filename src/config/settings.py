import os

"""Configuration settings"""

# GUI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
PADDING = 10

# Supported file formats
SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls', '.txt']

# File format options for dialog
SUPPORTED_FILE_FORMATS = [
    ('CSV files', '*.csv'),
    ('Excel files', '*.xlsx *.xls'),
    ('Text files', '*.txt'),
    ('All files', '*.*')
]

# Default peak names
DEFAULT_PEAK_NAMES = ['Peak1', 'Peak2', 'Peak3', 'Peak4']

# Default retention time ranges
DEFAULT_RETENTION_TIMES = [
    (10, 11),
    (11, 12),
    (12, 13),
    (13, 14)
]

# Export settings
DEFAULT_OUTPUT_NAME = 'Peaks_results'
EXPORT_FORMATS = ['xlsx', 'csv']

# Baseline correction methods incorporated
BASELINE_METHODS = ['None', 'Linear', 'Polynomial', 'Als (Asymmetric Least Squares)']

# Noise correction methods
NOISE_METHODS = ['None', 'Moving Average', 'Savitzky-Golay', 'Gaussian']

# Column detection
DEFAULT_TIME_COLUMN_INDEX = 1  # First column
DEFAULT_SIGNAL_COLUMN_INDEX = 2  # Second column
DEFAULT_TIME_COLUMN_NAMES = ['time', 'Time', 'TIME', 'Retention Time', 'RT', 'x'] #optional
DEFAULT_SIGNAL_COLUMN_NAMES = ['signal', 'Signal', 'SIGNAL', 'Intensity', 'Absorbance', 'AU', 'y', 'response']

# Supported delimiters for CSV/TXT files
SUPPORTED_DELIMITERS = [',', ';', '\t', '|', ' ']

# Processing settings
DEFAULT_NOISE_WINDOW = 5
DEFAULT_BASELINE_LAMBDA = 1e5
DEFAULT_BASELINE_P = 0.01
DEFAULT_BASELINE_ITERATIONS = 10
DEFAULT_SAVGOL_WINDOW = 11
DEFAULT_SAVGOL_POLYORDER = 3
DEFAULT_GAUSSIAN_SIGMA = 2.0

# Data validation
MIN_DATA_POINTS = 2
MAX_COLUMN_INDEX = 100

class Settings:
    def __init__(self):
        self.default_input_folder = os.path.join(os.getcwd(), 'input_files')
        self.default_output_folder = os.path.join(os.getcwd(), 'output_files')
        self.allowed_file_types = ['.csv', '.xlsx', '.xls', '.txt']
        self.export_format = 'csv'  # Options: 'csv', 'excel'
        self.enable_logging = True
        self.log_file_path = os.path.join(os.getcwd(), 'processing_log.csv')
        self.noise_correction_enabled = True
        self.baseline_correction_enabled = True
        self.default_peak_ranges = [(10, 11), (11, 12), (12, 13), (13, 14)]
        self.max_peak_count = 10  # Maximum number of peaks user can configure (working on more peaks)

    def get_settings(self):
        return {
            'default_input_folder': self.default_input_folder,
            'default_output_folder': self.default_output_folder,
            'allowed_file_types': self.allowed_file_types,
            'export_format': self.export_format,
            'enable_logging': self.enable_logging,
            'log_file_path': self.log_file_path,
            'noise_correction_enabled': self.noise_correction_enabled,
            'baseline_correction_enabled': self.baseline_correction_enabled,
            'default_peak_ranges': self.default_peak_ranges,
            'max_peak_count': self.max_peak_count
        }