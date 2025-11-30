#!/usr/bin/env python3
"""Test script to verify all imports work correctly"""
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

print("Testing imports...")
print(f"Python version: {sys.version}")
print(f"Src directory: {src_dir}")
print()

try:
    print("1. Testing config imports...")
    from config import settings
    print("   ✓ config.settings")
    
    print("\n2. Testing utils imports...")
    from utils.file_handler import FileHandler
    print("   ✓ utils.file_handler.FileHandler")
    
    from utils.data_validator import DataValidator
    print("   ✓ utils.data_validator.DataValidator")
    
    from utils.export_manager import ExportManager
    print("   ✓ utils.export_manager.ExportManager")
    
    print("\n3. Testing core imports...")
    from core.baseline_correction import apply_baseline_correction
    print("   ✓ core.baseline_correction.apply_baseline_correction")
    
    from core.noise_correction import apply_noise_correction
    print("   ✓ core.noise_correction.apply_noise_correction")
    
    from core.auc_calculator import AUCCalculator
    print("   ✓ core.auc_calculator.AUCCalculator")
    
    from core.file_processor import FileProcessor
    print("   ✓ core.file_processor.FileProcessor")
    
    print("\n4. Testing gui imports...")
    from gui.file_upload_frame import FileUploadFrame
    print("   ✓ gui.file_upload_frame.FileUploadFrame")
    
    from gui.peak_config_frame import PeakConfigFrame
    print("   ✓ gui.peak_config_frame.PeakConfigFrame")
    
    from gui.results_frame import ResultsFrame
    print("   ✓ gui.results_frame.ResultsFrame")
    
    from gui.processing_frame import ProcessingFrame
    print("   ✓ gui.processing_frame.ProcessingFrame")
    
    from gui.main_window import MainWindow
    print("   ✓ gui.main_window.MainWindow")
    
    print("\n✓ All imports successful!")
    print("\nYou can now run the application with: python run_app.py")
    
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)