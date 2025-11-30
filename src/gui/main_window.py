"""Main application window"""
import tkinter as tk
from tkinter import ttk
from gui.file_upload_frame import FileUploadFrame
from gui.peak_config_frame import PeakConfigFrame
from gui.processing_frame import ProcessingFrame
from gui.results_frame import ResultsFrame
from gui.manual_analysis_frame import ManualAnalysisFrame
import os
from tkinter import messagebox


class MainWindow(ttk.Frame):
    """Main application window with tabbed interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frames for each tab
        self.file_upload_frame = FileUploadFrame(self.notebook)
        self.peak_config_frame = PeakConfigFrame(self.notebook)
        self.results_frame = ResultsFrame(self.notebook)
        
        # Set file upload frame reference in peak config frame
        self.peak_config_frame.set_file_upload_frame(self.file_upload_frame)
        
        # Create processing frame with references
        self.processing_frame = ProcessingFrame(
            self.notebook,
            self.file_upload_frame,
            self.peak_config_frame,
            self.results_frame
        )
        
        self.manual_analysis_frame = ManualAnalysisFrame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.file_upload_frame.frame, text="📁 File Upload")
        self.notebook.add(self.peak_config_frame.frame, text="⚙️ Peak Configuration")
        self.notebook.add(self.processing_frame.frame, text="▶️ Processing")
        self.notebook.add(self.results_frame.frame, text="📊 Results")
        self.notebook.add(self.manual_analysis_frame.frame, text="🔬 Manual Analysis")
        
        # Status bar
        self.status_bar = ttk.Label(
            self,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Update status bar with application info
        self.status_bar.config(text="HPLC AUC Analyzer v1.0 | Ready")
    
    # Add debug output at the start of batch processing
    def start_batch_processing(self):
        """Start batch processing"""
        # Get selected files/folder
        selected_files = self.file_upload_frame.get_selected_files()
        
        print(f"\n{'='*60}")
        print(f"DEBUG - start_batch_processing called")
        print(f"DEBUG - Number of selected files: {len(selected_files)}")
        print(f"DEBUG - Selected files list:")
        for i, f in enumerate(selected_files):
            print(f"  [{i}] {f}")
            print(f"      Is file: {os.path.isfile(f)}")
            print(f"      Is dir: {os.path.isdir(f)}")
        print(f"{'='*60}\n")
        
        if not selected_files:
            messagebox.showwarning("No Files", "Please select files or folder to process")
            return
        
        # If in folder mode, get the folder path (parent directory of first file)
        if self.file_upload_frame.is_folder_mode():
            folder_path = os.path.dirname(selected_files[0])
            print(f"DEBUG - Folder mode detected")
            print(f"DEBUG - Using folder path: {folder_path}")
        else:
            # For individual files, we'll process them directly
            folder_path = None
            print(f"DEBUG - Individual file mode detected")