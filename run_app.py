#!/usr/bin/env python3
"""
Launcher Script
"""
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')

# Add src directory
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


if __name__ == "__main__":
    try:
        import tkinter as tk
        from tkinter import ttk
        from gui.main_window import MainWindow
        
        root = tk.Tk()
        root.title("HPLC AUC Analyzer")
        root.geometry("1200x800")

        root.minsize(800, 600)
        
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        app = MainWindow(root)
        app.pack(fill=tk.BOTH, expand=True)
        
        print("=" * 60)
        print("HPLC AUC Analyzer - Starting Application")
        print("=" * 60)
        print("Python version:", sys.version)
        print("Working directory:", os.getcwd())
        print("Src directory:", src_dir)
        print("=" * 60)
        root.mainloop()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print(f"\nPython path:")
        for path in sys.path:
            print(f"  {path}")
        print(f"\nCurrent directory: {os.getcwd()}")
        print(f"Src directory: {src_dir}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)