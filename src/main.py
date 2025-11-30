"""Main entry point for HPLC AUC Analyzer"""
import sys
import os

# Ensure the parent directory is in the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now add src to path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import tkinter as tk
from tkinter import ttk

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('TkAgg')

# Import with explicit path handling
try:
    from gui.main_window import MainWindow
except ImportError:
    import gui.main_window
    MainWindow = gui.main_window.MainWindow

def main():
    """Main application entry point"""
    root = tk.Tk()
    root.title("HPLC AUC Analyzer")
    root.geometry("1400x900")
    
    # Set minimum window size
    root.minsize(1000, 700)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Create and pack main window
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()