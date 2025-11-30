"""Peak configuration frame"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from config.settings import PADDING


class PeakConfigFrame:
    """Frame for peak configuration"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=PADDING)
        self.peak_rows = []
        self.file_upload_frame = None  # Will be set later
        
        self.current_time_data = None
        self.current_signal_data = None
        
        self._create_widgets()
        self._add_default_peaks()
    
    def set_file_upload_frame(self, frame):
        """Set reference to file upload frame"""
        self.file_upload_frame = frame
    
    def _create_widgets(self):
        """Create frame widgets"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Configuration (wider)
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right side: Visualization
        right_frame = ttk.Frame(main_container, width=450)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)  # Maintain fixed width
        
        # Title
        title_label = ttk.Label(
            left_frame, 
            text="Peak Configuration", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Correction methods
        correction_frame = ttk.LabelFrame(left_frame, text="Data Correction Methods", padding=10)
        correction_frame.pack(fill=tk.X, pady=10)
        
        # Baseline correction
        baseline_frame = ttk.Frame(correction_frame)
        baseline_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(baseline_frame, text="Baseline Correction:").pack(side=tk.LEFT, padx=5)
        self.baseline_var = tk.StringVar(value="None")
        baseline_combo = ttk.Combobox(
            baseline_frame,
            textvariable=self.baseline_var,
            values=["None", "Linear", "Polynomial", "Als (Asymmetric Least Squares)"],
            state='readonly',
            width=30
        )
        baseline_combo.pack(side=tk.LEFT, padx=5)
        baseline_combo.bind('<<ComboboxSelected>>', lambda e: self._safe_update_visualization())
        
        # Noise correction
        noise_frame = ttk.Frame(correction_frame)
        noise_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(noise_frame, text="Noise Correction:").pack(side=tk.LEFT, padx=5)
        self.noise_var = tk.StringVar(value="None")
        noise_combo = ttk.Combobox(
            noise_frame,
            textvariable=self.noise_var,
            values=["None", "Moving Average", "Savitzky-Golay", "Gaussian"],
            state='readonly',
            width=30
        )
        noise_combo.pack(side=tk.LEFT, padx=5)
        noise_combo.bind('<<ComboboxSelected>>', lambda e: self._safe_update_visualization())
        
        # Total calculation method
        total_frame = ttk.LabelFrame(left_frame, text="Total Calculation Method", padding=10)
        total_frame.pack(fill=tk.X, pady=10)
        
        self.total_method_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(
            total_frame,
            text="Sum of all defined peaks",
            variable=self.total_method_var,
            value="all",
            command=self._update_total_method_ui
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            total_frame,
            text="Sum of selected peaks only",
            variable=self.total_method_var,
            value="selected",
            command=self._update_total_method_ui
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            total_frame,
            text="User-defined total peak range (for comparison)",
            variable=self.total_method_var,
            value="custom",
            command=self._update_total_method_ui
        ).pack(anchor=tk.W, pady=2)
        
        # Custom total peak range frame
        self.custom_total_frame = ttk.Frame(total_frame)
        self.custom_total_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(self.custom_total_frame, text="Total Peak Name:").pack(side=tk.LEFT, padx=5)
        self.custom_total_name_var = tk.StringVar(value="Total_Peak")
        ttk.Entry(
            self.custom_total_frame,
            textvariable=self.custom_total_name_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.custom_total_frame, text="Start:").pack(side=tk.LEFT, padx=5)
        self.custom_total_start_var = tk.DoubleVar(value=10.0)
        ttk.Entry(
            self.custom_total_frame,
            textvariable=self.custom_total_start_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.custom_total_frame, text="End:").pack(side=tk.LEFT, padx=5)
        self.custom_total_end_var = tk.DoubleVar(value=14.0)
        ttk.Entry(
            self.custom_total_frame,
            textvariable=self.custom_total_end_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Info labels
        info_frame = ttk.Frame(total_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_label_1 = ttk.Label(
            info_frame,
            text="ℹ When 'selected peaks' is chosen, check the peaks to include in total",
            font=('Arial', 9, 'italic'),
            foreground='blue'
        )
        
        self.info_label_2 = ttk.Label(
            info_frame,
            text="ℹ With custom total peak: Both standard (sum of peaks) and custom total will be calculated",
            font=('Arial', 9, 'italic'),
            foreground='blue'
        )
        
        # Initially hide custom total frame
        self.custom_total_frame.pack_forget()
        
        # Peak configuration with better layout
        peak_config_frame = ttk.LabelFrame(left_frame, text="Peak Ranges", padding=10)
        peak_config_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Control buttons at top
        btn_frame = ttk.Frame(peak_config_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="+ Add Peak",
            command=self._add_peak_row
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self._reset_peaks
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="👁 Visualize Peaks",
            command=self._safe_update_visualization
        ).pack(side=tk.LEFT, padx=5)
        
        # Scrollable canvas for peaks
        canvas_frame = ttk.Frame(peak_config_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with both scrollbars
        canvas = tk.Canvas(canvas_frame, height=250)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Header with better spacing
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Peak Name", width=18).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="Start Time", width=12).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="End Time", width=12).grid(row=0, column=2, padx=5)
        self.include_header_label = ttk.Label(header_frame, text="Include", width=8)
        self.include_header_label.grid(row=0, column=3, padx=5)
        ttk.Label(header_frame, text="Actions", width=15).grid(row=0, column=4, padx=5)
        
        # Container for peak rows
        self.peaks_container = ttk.Frame(self.scrollable_frame)
        self.peaks_container.pack(fill=tk.BOTH, expand=True)
        
        # RIGHT SIDE: Visualization
        viz_label = ttk.Label(
            right_frame,
            text="Peak Visualization",
            font=('Arial', 14, 'bold')
        )
        viz_label.pack(pady=(0, 10))
        
        # Visualization plot
        viz_plot_frame = ttk.LabelFrame(right_frame, text="Peak Ranges on Chromatogram", padding=5)
        viz_plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.viz_fig = Figure(figsize=(5, 3.5), dpi=80)
        self.viz_ax = self.viz_fig.add_subplot(111)
        self.viz_ax.set_xlabel('Time (min)', fontsize=9)
        self.viz_ax.set_ylabel('Signal (AU)', fontsize=9)
        self.viz_ax.set_title('Load file to visualize peaks', fontsize=10)
        self.viz_ax.grid(True, alpha=0.3)
        self.viz_ax.tick_params(labelsize=8)
        
        self.viz_canvas = FigureCanvasTkAgg(self.viz_fig, master=viz_plot_frame)
        self.viz_canvas.draw()
        self.viz_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        toolbar_frame = ttk.Frame(viz_plot_frame)
        toolbar_frame.pack(fill=tk.X)
        self.viz_toolbar = NavigationToolbar2Tk(self.viz_canvas, toolbar_frame)
        self.viz_toolbar.update()
        
        # Custom zoom controls
        zoom_control_frame = ttk.Frame(viz_plot_frame)
        zoom_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            zoom_control_frame,
            text="Reset View",
            command=self._reset_viz_zoom,
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            zoom_control_frame,
            text="Fit Data",
            command=self._fit_viz_data,
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        # Compact axis range controls
        range_frame = ttk.LabelFrame(viz_plot_frame, text="Zoom Range", padding=3)
        range_frame.pack(fill=tk.X, pady=3)
        
        # X-axis
        x_frame = ttk.Frame(range_frame)
        x_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(x_frame, text="X:", font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        self.viz_xmin_var = tk.StringVar(value="auto")
        ttk.Entry(x_frame, textvariable=self.viz_xmin_var, width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        ttk.Label(x_frame, text="-", font=('Arial', 8)).pack(side=tk.LEFT)
        self.viz_xmax_var = tk.StringVar(value="auto")
        ttk.Entry(x_frame, textvariable=self.viz_xmax_var, width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        
        # Y-axis
        y_frame = ttk.Frame(range_frame)
        y_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(y_frame, text="Y:", font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        self.viz_ymin_var = tk.StringVar(value="auto")
        ttk.Entry(y_frame, textvariable=self.viz_ymin_var, width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        ttk.Label(y_frame, text="-", font=('Arial', 8)).pack(side=tk.LEFT)
        self.viz_ymax_var = tk.StringVar(value="auto")
        ttk.Entry(y_frame, textvariable=self.viz_ymax_var, width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            range_frame,
            text="Apply",
            command=self._apply_viz_zoom,
            width=10
        ).pack(pady=2)
        
        # Peak summary
        summary_frame = ttk.LabelFrame(right_frame, text="Peak Summary", padding=5)
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        summary_scroll = ttk.Scrollbar(summary_frame)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.summary_text = tk.Text(
            summary_frame, 
            height=6, 
            wrap=tk.WORD, 
            font=('Arial', 8),
            yscrollcommand=summary_scroll.set
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        summary_scroll.config(command=self.summary_text.yview)
        
        # Info
        info_label = ttk.Label(
            right_frame,
            text="💡 Use toolbar or range inputs to zoom",
            font=('Arial', 8, 'italic'),
            foreground='blue',
            wraplength=400
        )
        info_label.pack(pady=5)
    
    def _reset_viz_zoom(self):
        """Reset visualization zoom"""
        if self.current_time_data is not None and self.current_signal_data is not None:
            self.viz_ax.set_xlim(self.current_time_data.min(), self.current_time_data.max())
            self.viz_ax.set_ylim(self.current_signal_data.min(), self.current_signal_data.max())
            self.viz_canvas.draw()
            
            # Update entry fields
            self.viz_xmin_var.set(f"{self.current_time_data.min():.2f}")
            self.viz_xmax_var.set(f"{self.current_time_data.max():.2f}")
            self.viz_ymin_var.set(f"{self.current_signal_data.min():.2f}")
            self.viz_ymax_var.set(f"{self.current_signal_data.max():.2f}")
    
    def _fit_viz_data(self):
        """Fit data with padding"""
        if self.current_time_data is not None and self.current_signal_data is not None:
            x_margin = (self.current_time_data.max() - self.current_time_data.min()) * 0.05
            y_margin = (self.current_signal_data.max() - self.current_signal_data.min()) * 0.1
            
            self.viz_ax.set_xlim(
                self.current_time_data.min() - x_margin,
                self.current_time_data.max() + x_margin
            )
            self.viz_ax.set_ylim(
                self.current_signal_data.min() - y_margin,
                self.current_signal_data.max() + y_margin
            )
            self.viz_canvas.draw()
    
    def _apply_viz_zoom(self):
        """Apply custom zoom"""
        try:
            xmin = self.viz_xmin_var.get()
            xmax = self.viz_xmax_var.get()
            ymin = self.viz_ymin_var.get()
            ymax = self.viz_ymax_var.get()
            
            if xmin != "auto" and xmax != "auto":
                self.viz_ax.set_xlim(float(xmin), float(xmax))
            
            if ymin != "auto" and ymax != "auto":
                self.viz_ax.set_ylim(float(ymin), float(ymax))
            
            self.viz_canvas.draw()
        except ValueError:
            messagebox.showerror("Error", "Invalid range values. Use numbers or 'auto'")
    
    def _add_peak_row(self, name="", start=0.0, end=0.0, include_in_total=True):
        """Add a peak configuration row with grid layout"""
        row_frame = ttk.Frame(self.peaks_container)
        row_frame.pack(fill=tk.X, pady=3)
        
        name_var = tk.StringVar(value=name if name else f"Peak_{len(self.peak_rows)+1}")
        start_var = tk.DoubleVar(value=start)
        end_var = tk.DoubleVar(value=end)
        include_var = tk.BooleanVar(value=include_in_total)
        
        # Use grid for better alignment
        name_entry = ttk.Entry(row_frame, textvariable=name_var, width=18)
        name_entry.grid(row=0, column=0, padx=5, sticky='w')
        
        start_entry = ttk.Entry(row_frame, textvariable=start_var, width=12)
        start_entry.grid(row=0, column=1, padx=5, sticky='w')
        
        end_entry = ttk.Entry(row_frame, textvariable=end_var, width=12)
        end_entry.grid(row=0, column=2, padx=5, sticky='w')
        
        # Checkbox for including in total
        include_check = ttk.Checkbutton(
            row_frame,
            variable=include_var,
            width=8
        )
        include_check.grid(row=0, column=3, padx=5, sticky='w')
        
        # Initially disable if "all peaks" mode
        if self.total_method_var.get() != "selected":
            include_check.config(state=tk.DISABLED)
        
        peak_data = {
            'frame': row_frame,
            'name': name_var,
            'start': start_var,
            'end': end_var,
            'include_in_total': include_var,
            'include_checkbox': include_check
        }
        
        # Button frame for actions
        btn_frame = ttk.Frame(row_frame)
        btn_frame.grid(row=0, column=4, padx=5, sticky='w')
        
        remove_btn = ttk.Button(
            btn_frame,
            text="✕ Remove",
            command=lambda: self._remove_peak_row(peak_data),
            width=12
        )
        remove_btn.pack(side=tk.LEFT)
        
        self.peak_rows.append(peak_data)
    
    def _update_total_method_ui(self):
        """Update UI based on total calculation method"""
        method = self.total_method_var.get()
        
        # Clear existing info labels
        self.info_label_1.pack_forget()
        self.info_label_2.pack_forget()
        
        if method == "all":
            self.custom_total_frame.pack_forget()
            for peak_data in self.peak_rows:
                peak_data['include_checkbox'].config(state=tk.DISABLED)
                peak_data['include_in_total'].set(True)
            self.include_header_label.grid_forget()
                
        elif method == "selected":
            self.custom_total_frame.pack_forget()
            for peak_data in self.peak_rows:
                peak_data['include_checkbox'].config(state=tk.NORMAL)
            self.include_header_label.grid(row=0, column=3, padx=5)
            self.info_label_1.pack(anchor=tk.W, pady=2)
                
        elif method == "custom":
            self.custom_total_frame.pack(fill=tk.X, padx=20, pady=5)
            for peak_data in self.peak_rows:
                peak_data['include_checkbox'].config(state=tk.DISABLED)
                peak_data['include_in_total'].set(True)
            self.include_header_label.grid_forget()
            self.info_label_2.pack(anchor=tk.W, pady=2)
        
        self._safe_update_visualization()
    
    def _safe_update_visualization(self):
        """Safely update visualization with error handling"""
        try:
            self._update_visualization()
        except Exception as e:
            print(f"Visualization error: {e}")
            self._update_summary()
    
    def _update_visualization(self):
        """Update the visualization with current settings"""
        if not self.file_upload_frame:
            self._show_no_file_message()
            return
        
        selected_files = self.file_upload_frame.get_selected_files()
        if not selected_files:
            self._show_no_file_message()
            return
        
        try:
            from utils.file_handler import FileHandler
            from core.baseline_correction import apply_baseline_correction
            from core.noise_correction import apply_noise_correction
            
            file_handler = FileHandler()
            
            # Load first file
            filepath = selected_files[0]
            df = file_handler.read_file(filepath, self.file_upload_frame.has_header())
            
            time_col, signal_col = file_handler.detect_columns(
                df,
                self.file_upload_frame.get_time_column_index(),
                self.file_upload_frame.get_signal_column_index()
            )
            
            time_data = df[time_col].values
            signal_data = df[signal_col].values
            
            # Apply corrections
            noise_method = self.noise_var.get()
            if noise_method != "None":
                signal_data = apply_noise_correction(signal_data, noise_method)
            
            baseline_method = self.baseline_var.get()
            if baseline_method != "None":
                signal_data = apply_baseline_correction(time_data, signal_data, baseline_method)
            
            # Store data
            self.current_time_data = time_data
            self.current_signal_data = signal_data
            
            # Plot
            self.viz_ax.clear()
            self.viz_ax.plot(time_data, signal_data, 'b-', linewidth=1.5, label='Signal', alpha=0.7)
            
            # Plot peak ranges
            peaks = self.get_peaks()
            colors = ['red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta']
            
            for idx, peak in enumerate(peaks):
                color = colors[idx % len(colors)]
                start = peak['start']
                end = peak['end']
                
                # Draw vertical lines
                self.viz_ax.axvline(start, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
                self.viz_ax.axvline(end, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
                
                # Shade region
                mask = (time_data >= start) & (time_data <= end)
                if np.any(mask):
                    self.viz_ax.fill_between(
                        time_data[mask],
                        0,
                        signal_data[mask],
                        alpha=0.2,
                        color=color,
                        label=peak['name']
                    )
            
            # Custom total peak
            if self.total_method_var.get() == "custom":
                custom_start = self.custom_total_start_var.get()
                custom_end = self.custom_total_end_var.get()
                self.viz_ax.axvline(custom_start, color='blue', linestyle=':', linewidth=2, alpha=0.7)
                self.viz_ax.axvline(custom_end, color='blue', linestyle=':', linewidth=2, alpha=0.7)
                self.viz_ax.axvspan(custom_start, custom_end, alpha=0.1, color='blue', 
                                   label=self.custom_total_name_var.get())
            
            self.viz_ax.set_xlabel('Time (min)', fontsize=9)
            self.viz_ax.set_ylabel('Signal (AU)', fontsize=9)
            self.viz_ax.set_title('Peak Ranges Visualization', fontsize=10, fontweight='bold')
            self.viz_ax.grid(True, alpha=0.3)
            self.viz_ax.tick_params(labelsize=8)
            
            # Only show legend if not too many peaks
            if len(peaks) <= 8:
                self.viz_ax.legend(loc='best', fontsize=7, ncol=2)
            
            self.viz_fig.tight_layout()
            self.viz_canvas.draw()
            
            # Update zoom entry fields
            self.viz_xmin_var.set(f"{time_data.min():.2f}")
            self.viz_xmax_var.set(f"{time_data.max():.2f}")
            self.viz_ymin_var.set(f"{signal_data.min():.2f}")
            self.viz_ymax_var.set(f"{signal_data.max():.2f}")
            
            # Update summary
            self._update_summary()
            
        except Exception as e:
            print(f"Error in visualization: {e}")
            self.viz_ax.clear()
            self.viz_ax.text(0.5, 0.5, f'Error: {str(e)[:50]}...', 
                           ha='center', va='center', transform=self.viz_ax.transAxes,
                           fontsize=9, color='red', wrap=True)
            self.viz_ax.set_title('Visualization Error')
            self.viz_canvas.draw()
            self._update_summary()
    
    def _show_no_file_message(self):
        """Show message when no file is loaded"""
        self.viz_ax.clear()
        self.viz_ax.text(0.5, 0.5, 'Please load a file in\n"File Upload" tab first', 
                       ha='center', va='center', transform=self.viz_ax.transAxes,
                       fontsize=11, style='italic')
        self.viz_ax.set_title('No File Loaded', fontsize=10)
        self.viz_ax.grid(True, alpha=0.3)
        self.viz_canvas.draw()
        self._update_summary()
    
    def _update_summary(self):
        """Update peak summary text"""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        peaks = self.get_peaks()
        
        self.summary_text.insert(tk.END, f"Total Peaks: {len(peaks)}\n", 'bold')
        self.summary_text.insert(tk.END, f"Baseline: {self.baseline_var.get()}\n")
        self.summary_text.insert(tk.END, f"Noise: {self.noise_var.get()}\n")
        
        method = self.total_method_var.get()
        method_text = {
            'all': 'Sum of all peaks',
            'selected': 'Sum of selected peaks',
            'custom': 'Custom total peak'
        }
        self.summary_text.insert(tk.END, f"Total: {method_text.get(method, method)}\n\n")
        
        self.summary_text.insert(tk.END, "Peaks:\n", 'bold')
        self.summary_text.insert(tk.END, "─" * 35 + "\n")
        
        for peak in peaks:
            if method == 'selected':
                include = "✓" if peak['include_in_total'] else "✗"
                self.summary_text.insert(tk.END, f"{include} ")
            
            self.summary_text.insert(tk.END, f"{peak['name']}: ", 'peak_name')
            self.summary_text.insert(tk.END, f"{peak['start']:.2f}-{peak['end']:.2f}\n")
        
        if self.total_method_var.get() == "custom":
            self.summary_text.insert(tk.END, "\n" + "─" * 35 + "\n")
            self.summary_text.insert(tk.END, f"Custom: {self.custom_total_name_var.get()}\n", 'bold')
            self.summary_text.insert(tk.END, 
                f"{self.custom_total_start_var.get():.2f}-{self.custom_total_end_var.get():.2f}\n")
        
        self.summary_text.tag_configure('bold', font=('Arial', 8, 'bold'))
        self.summary_text.tag_configure('peak_name', font=('Arial', 8, 'bold'), foreground='blue')
        self.summary_text.config(state=tk.DISABLED)
    
    def _remove_peak_row(self, peak_data):
        """Remove a peak row"""
        if len(self.peak_rows) <= 1:
            messagebox.showwarning("Warning", "At least one peak must be configured")
            return
        
        peak_data['frame'].destroy()
        self.peak_rows.remove(peak_data)
        self._safe_update_visualization()
    
    def _add_default_peaks(self):
        """Add default peak configuration"""
        defaults = [
            ("Acid", 10, 11, True),
            ("Main", 11, 12, True),
            ("Base1", 12, 13, True),
            ("Base2", 13, 14, True)
        ]
        
        for name, start, end, include in defaults:
            self._add_peak_row(name, start, end, include)
    
    def _reset_peaks(self):
        """Reset to default peaks"""
        # Remove all peaks
        for peak_data in self.peak_rows[:]:
            peak_data['frame'].destroy()
        self.peak_rows.clear()
        
        # Add defaults
        self._add_default_peaks()
        self._safe_update_visualization()
    
    def get_peaks(self):
        """Get configured peaks with include_in_total flag"""
        peaks = []
        for peak_data in self.peak_rows:
            try:
                peaks.append({
                    'name': peak_data['name'].get(),
                    'start': peak_data['start'].get(),
                    'end': peak_data['end'].get(),
                    'include_in_total': peak_data['include_in_total'].get()
                })
            except Exception as e:
                print(f"Error getting peak data: {e}")
        return peaks
    
    def get_total_calculation_method(self):
        """Get the total calculation method"""
        return self.total_method_var.get()
    
    def get_custom_total_peak(self):
        """Get custom total peak configuration"""
        return {
            'name': self.custom_total_name_var.get(),
            'start': self.custom_total_start_var.get(),
            'end': self.custom_total_end_var.get()
        }
    
    def get_baseline_method(self):
        """Get baseline correction method"""
        return self.baseline_var.get()
    
    def get_noise_method(self):
        """Get noise correction method"""
        return self.noise_var.get()
    
    def validate(self):
        """Validate peak configuration"""
        peaks = self.get_peaks()
        
        if not peaks:
            messagebox.showerror("Error", "At least one peak must be configured")
            return False
        
        # Check if at least one peak is included in total when using "selected" mode
        if self.total_method_var.get() == "selected":
            if not any(p['include_in_total'] for p in peaks):
                messagebox.showerror("Error", "At least one peak must be included in total calculation")
                return False
        
        # Validate custom total peak if that mode is selected
        if self.total_method_var.get() == "custom":
            custom_total = self.get_custom_total_peak()
            if not custom_total['name']:
                messagebox.showerror("Error", "Custom total peak must have a name")
                return False
            if custom_total['start'] >= custom_total['end']:
                messagebox.showerror("Error", "Invalid range for custom total peak")
                return False
        
        for peak in peaks:
            if not peak['name']:
                messagebox.showerror("Error", "All peaks must have a name")
                return False
            
            if peak['start'] >= peak['end']:
                messagebox.showerror("Error", f"Invalid range for peak '{peak['name']}'")
                return False
        
        return True