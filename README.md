# HPLC AUC Analyzer

## Overview
The HPLC AUC Analyzer is a Tkinter-based application designed to process various file types (CSV, Excel, and text files) for calculating the area under the curve (AUC) and respective percentages for multiple peaks. The application includes features for noise correction and baseline correction, making it a comprehensive tool for analyzing chromatographic data.

## Features
- Upload folders and files of various formats (CSV, Excel, text).
- Process files without headers.
- Calculate AUC and peak percentages based on user-defined configurations.
- Apply noise and baseline corrections to improve data quality.
- Export results directly to CSV or Excel with customizable filenames.
- Log processing results in CSV format with serial numbers.

## Project Structure
```
hplc-auc-analyzer
├── src
│   ├── main.py                  # Entry point of the application
│   ├── gui                      # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── file_upload_frame.py
│   │   ├── peak_config_frame.py
│   │   ├── processing_frame.py
│   │   └── results_frame.py
│   ├── core                     # Core processing logic
│   │   ├── __init__.py
│   │   ├── file_processor.py
│   │   ├── auc_calculator.py
│   │   ├── baseline_correction.py
│   │   └── noise_correction.py
│   ├── utils                    # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py
│   │   ├── data_validator.py
│   │   └── export_manager.py
│   └── config                   # Configuration settings
│       ├── __init__.py
│       └── settings.py
├── tests                        # Unit tests
│   ├── __init__.py
│   ├── test_auc_calculator.py
│   ├── test_file_processor.py
│   └── test_corrections.py
├── requirements.txt             # Project dependencies
├── .gitignore                   # Files to ignore in version control
└── README.md                    # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hplc-auc-analyzer.git
   ```
2. Navigate to the project directory:
   ```
   cd hplc-auc-analyzer
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/main.py
   ```
2. Use the GUI to upload files and configure peak settings.
3. Process the files to calculate AUC and view results.
4. Export results as needed.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.