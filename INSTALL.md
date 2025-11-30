# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install pandas numpy scipy openpyxl matplotlib
```

### 2. Run the Application

```bash
python run_app.py
```

## Features

### Batch Processing Mode
1. **File Upload**: Load single or multiple files
2. **Peak Configuration**: Define peaks and correction methods
3. **Processing**: Batch process all files
4. **Results**: View and export results

### Manual Analysis Mode
1. **Load File**: Load a single chromatogram
2. **Apply Corrections**: Baseline and noise correction
3. **Interactive Peak Picking**: Click to define peak ranges
4. **Real-time Visualization**: Zoom and pan capabilities
5. **Calculate & Export**: Get AUC values for picked peaks

## Manual Analysis Instructions

1. Switch to the "🔬 Manual Analysis" tab
2. Click "Load File" to select your data file
3. Configure file settings (header, columns) if needed
4. Apply corrections if desired (optional)
5. Check "Enable Peak Picking"
6. Click on the plot:
   - First click: Peak start point (green marker)
   - Second click: Peak end point (red marker)
   - Repeat for multiple peaks
7. Click "Calculate AUC" to compute areas
8. Export results if needed

## Tips

- Use the zoom/pan tools in the toolbar for precise peak selection
- Double-click on a peak in the table to remove it
- Apply corrections before picking peaks for better accuracy
- The shaded regions show your selected peak areas