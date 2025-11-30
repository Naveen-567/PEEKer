"""File upload frame"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from config.settings import PADDING, DEFAULT_TIME_COLUMN_INDEX, DEFAULT_SIGNAL_COLUMN_INDEX
from utils.file_handler import FileHandler

# Supported file formats
SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls', '.txt']


class FileUploadFrame:
    """Frame for file/folder upload"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=PADDING)
        self.selected_files = []
        self.folder_mode = False
        self.file_handler = FileHandler()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create frame widgets"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Controls
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right side: Preview
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Title
        title_label = ttk.Label(
            left_frame, 
            text="File Upload", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Upload mode selection
        mode_frame = ttk.LabelFrame(left_frame, text="Upload Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.mode_var = tk.StringVar(value="files")
        
        ttk.Radiobutton(
            mode_frame,
            text="Individual Files",
            variable=self.mode_var,
            value="files",
            command=self._mode_changed
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            mode_frame,
            text="Folder (Batch)",
            variable=self.mode_var,
            value="folder",
            command=self._mode_changed
        ).pack(side=tk.LEFT, padx=10)
        
        # File settings
        settings_frame = ttk.LabelFrame(left_frame, text="File Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Header checkbox
        self.has_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Files have header row",
            variable=self.has_header_var
        ).pack(anchor=tk.W, pady=2)
        
        # Info label about automatic delimiter detection
        info_label = ttk.Label(
            settings_frame,
            text="ℹ Delimiter (comma, semicolon, tab, etc.) will be detected automatically",
            font=('Arial', 9, 'italic'),
            foreground='blue'
        )
        info_label.pack(anchor=tk.W, pady=2)
        
        # Column indices (1-based for user friendliness)
        col_frame = ttk.Frame(settings_frame)
        col_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(col_frame, text="Time Column (1-based):").pack(side=tk.LEFT, padx=5)
        self.time_col_var = tk.IntVar(value=DEFAULT_TIME_COLUMN_INDEX)
        ttk.Spinbox(
            col_frame,
            from_=1,
            to=50,
            textvariable=self.time_col_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(col_frame, text="Signal Column (1-based):").pack(side=tk.LEFT, padx=15)
        self.signal_col_var = tk.IntVar(value=DEFAULT_SIGNAL_COLUMN_INDEX)
        ttk.Spinbox(
            col_frame,
            from_=1,
            to=50,
            textvariable=self.signal_col_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Helper text
        helper_label = ttk.Label(
            settings_frame,
            text="Note: Column 1 = First column, Column 2 = Second column, etc.",
            font=('Arial', 9, 'italic')
        )
        helper_label.pack(anchor=tk.W, pady=2)
        
        # Upload controls
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.upload_btn = ttk.Button(
            control_frame,
            text="Select Files",
            command=self._select_files
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Clear Selection",
            command=self._clear_selection
        ).pack(side=tk.LEFT, padx=5)
        
        # File list
        list_frame = ttk.LabelFrame(left_frame, text="Selected Files", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self._on_file_select)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        self.status_label = ttk.Label(left_frame, text="No files selected", foreground='gray')
        self.status_label.pack(pady=5)
        
        preview_frame = ttk.LabelFrame(right_frame, text="Data Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            preview_controls,
            text="Preview Selected File",
            command=self._preview_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            preview_controls,
            text="Fit Data",
            command=self._fit_preview_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            preview_controls,
            text="Reset Zoom",
            command=self._reset_preview_zoom
        ).pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        zoom_frame = ttk.Frame(preview_controls)
        zoom_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT, padx=2)
        
        self.zoom_start_var = tk.StringVar(value="")
        ttk.Entry(zoom_frame, textvariable=self.zoom_start_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(zoom_frame, text="to").pack(side=tk.LEFT, padx=2)
        
        self.zoom_end_var = tk.StringVar(value="")
        ttk.Entry(zoom_frame, textvariable=self.zoom_end_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            zoom_frame,
            text="Apply",
            command=self._apply_preview_zoom,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        self.preview_fig = Figure(figsize=(8, 6))
        self.preview_ax = self.preview_fig.add_subplot(111)
        self.preview_canvas = FigureCanvasTkAgg(self.preview_fig, preview_frame)
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_frame = ttk.Frame(preview_frame)
        toolbar_frame.pack(fill=tk.X)
        self.preview_toolbar = NavigationToolbar2Tk(self.preview_canvas, toolbar_frame)
        self.preview_toolbar.update()
        
        self.preview_time_data = None
        self.preview_signal_data = None
    
    def _reset_preview_zoom(self):
        """Reset preview zoom to show all data"""
        if self.preview_time_data is not None and self.preview_signal_data is not None:
            self.preview_ax.clear()
            self.preview_ax.plot(self.preview_time_data, self.preview_signal_data, 'b-', linewidth=1)
            self.preview_ax.set_xlabel('Time')
            self.preview_ax.set_ylabel('Signal')
            self.preview_ax.set_title('Data Preview')
            self.preview_ax.grid(True, alpha=0.3)
            self.preview_fig.tight_layout()
            self.preview_canvas.draw()
            self.zoom_start_var.set("")
            self.zoom_end_var.set("")
    
    def _fit_preview_data(self):
        """Fit preview to show all data"""
        self._reset_preview_zoom()
    
    def _apply_preview_zoom(self):
        """Apply zoom range to preview"""
        try:
            start = float(self.zoom_start_var.get())
            end = float(self.zoom_end_var.get())
            
            if start >= end:
                messagebox.showwarning("Invalid Range", "Start value must be less than end value")
                return
            
            self.preview_ax.set_xlim(start, end)
            self.preview_canvas.draw()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid numbers for zoom range")
    
    def _mode_changed(self):
        """Handle upload mode change"""
        self.folder_mode = (self.mode_var.get() == "folder")
        self.upload_btn.config(text="Select Folder" if self.folder_mode else "Select Files")
        self._clear_selection()
    
    def _select_files(self):
        """Handle file/folder selection"""
        if self.folder_mode:
            folder = filedialog.askdirectory(
                title="⚠️ SELECT THE FOLDER (not a file inside it)",
                mustexist=True
            )
            
            if not folder:
                return
            
            print(f"DEBUG - Selected path: {folder}")
            print(f"DEBUG - Is directory: {os.path.isdir(folder)}")
            print(f"DEBUG - Is file: {os.path.isfile(folder)}")
            
            # Verify the direc
            if not os.path.isdir(folder):
                messagebox.showerror(
                    "Error - File Selected Instead of Folder",
                    f"You selected a FILE, not a FOLDER:\n{folder}\n\n"
                    f"Please:\n"
                    f"1. Click 'Select Folder' again\n"
                    f"2. Navigate to the folder containing your CSV files\n"
                    f"3. Select the FOLDER (don't double-click to open it)\n"
                    f"4. Click 'Choose' or 'Open' button"
                )
                return
            
            files = []
            try:
                all_items = os.listdir(folder)
                print(f"DEBUG - Items in folder: {all_items}")
                
                for item in all_items:
                    full_path = os.path.join(folder, item)
                    if os.path.isfile(full_path):
                        if any(item.lower().endswith(ext.lower()) for ext in SUPPORTED_FORMATS):
                            files.append(full_path)
                            print(f"DEBUG - Found supported file: {item}")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Error reading folder:\n{str(e)}"
                )
                return
            
            print(f"DEBUG - Total files found: {len(files)}")
            
            if files:
                files.sort()
                self.selected_files = files
                self.file_listbox.delete(0, tk.END)
                for f in files:
                    self.file_listbox.insert(tk.END, os.path.basename(f))
                self.status_label.config(
                    text=f"✓ Folder: {os.path.basename(folder)} ({len(files)} file(s))",
                    foreground='green'
                )
                messagebox.showinfo(
                    "Success - Folder Selected",
                    f"Found {len(files)} supported file(s) in:\n\n{folder}\n\n"
                    f"Files:\n" + "\n".join([f"• {os.path.basename(f)}" for f in files[:10]]) +
                    (f"\n... and {len(files)-10} more" if len(files) > 10 else "")
                )
            else:
                messagebox.showwarning(
                    "No Files Found",
                    f"No supported files found in folder:\n{folder}\n\n"
                    f"Supported formats: {', '.join(SUPPORTED_FORMATS)}\n\n"
                    f"Items in folder: {len(all_items)}"
                )
        else:
            files = filedialog.askopenfilenames(
                title="Select Data Files",
                filetypes=[
                    ("All Supported", " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS)),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx *.xls"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if files:
                self.selected_files = list(files)
                self.file_listbox.delete(0, tk.END)
                for f in files:
                    self.file_listbox.insert(tk.END, os.path.basename(f))
                self.status_label.config(
                    text=f"Selected {len(files)} file(s)",
                    foreground='green'
                )
    
    def _clear_selection(self):
        """Clear selected files"""
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.status_label.config(text="No files selected", foreground='gray')
        self._clear_preview()
    
    def _on_file_select(self, event):
        """Handle file selection in listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            idx = selection[0]
            self._preview_file_by_index(idx)
    
    def _preview_file(self):
        """Preview currently selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file from the list to preview")
            return
        
        idx = selection[0]
        self._preview_file_by_index(idx)
    
    def _preview_file_by_index(self, idx):
        """Preview file by index"""
        if 0 <= idx < len(self.selected_files):
            filepath = self.selected_files[idx]
            
            try:
                # Read file
                df = self.file_handler.read_file(filepath, self.has_header_var.get())
                
                # Get column indices (convert from 1-based to 0-based)
                time_col_idx = self.time_col_var.get() - 1
                signal_col_idx = self.signal_col_var.get() - 1
                
                # Detect columns
                time_col, signal_col = self.file_handler.detect_columns(
                    df, self.time_col_var.get(), self.signal_col_var.get()
                )
                
                # Get data
                time_data = df[time_col].values
                signal_data = df[signal_col].values
                
                # Store for zoom reset
                self.preview_time_data = time_data
                self.preview_signal_data = signal_data
                
                # Plot
                self.preview_ax.clear()
                self.preview_ax.plot(time_data, signal_data, 'b-', linewidth=1)
                self.preview_ax.set_xlabel('Time')
                self.preview_ax.set_ylabel('Signal')
                self.preview_ax.set_title(f'Preview: {os.path.basename(filepath)}')
                self.preview_ax.grid(True, alpha=0.3)
                self.preview_fig.tight_layout()
                self.preview_canvas.draw()
                
            except Exception as e:
                messagebox.showerror("Preview Error", f"Error previewing file:\n{str(e)}")
                self._clear_preview()
    
    def _clear_preview(self):
        """Clear preview plot"""
        self.preview_ax.clear()
        self.preview_ax.text(0.5, 0.5, 'No preview available', 
                            ha='center', va='center', transform=self.preview_ax.transAxes)
        self.preview_canvas.draw()
        self.preview_time_data = None
        self.preview_signal_data = None
        self.zoom_start_var.set("")
        self.zoom_end_var.set("")
    
    def get_selected_files(self):
        """Get list of selected file paths"""
        return self.selected_files
    
    def is_folder_mode(self):
        """Check if in folder mode"""
        return self.folder_mode
    
    def get_export_format(self):
        """Get export format preference"""
        return self.export_format_var.get() if hasattr(self, 'export_format_var') else 'csv'
    
    def has_header(self):
        """Check if files have header"""
        return self.has_header_var.get()
    
    def get_time_column_index(self):
        """Get time column index (1-based)"""
        return self.time_col_var.get()
    
    def get_signal_column_index(self):
        """Get signal column index (1-based)"""
        return self.signal_col_var.get()

    def pack(self, *args, **kwargs):
        """Pack the frame"""
        self.frame.pack(*args, **kwargs)

    def forget(self):
        """Remove the frame"""
        self.frame.pack_forget()