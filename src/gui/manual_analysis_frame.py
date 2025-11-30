"""Manual peak analysis frame with interactive plotting"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import os
from scipy.signal import find_peaks
from config.settings import PADDING
from utils.file_handler import FileHandler
from core.auc_calculator import AUCCalculator


class ManualAnalysisFrame:
    """Frame for manual peak analysis with interactive plotting"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=PADDING)
        self.current_file = None
        self.time_data = None
        self.signal_data = None
        self.original_signal = None
        self.picked_peaks = []
        self.peak_markers = []
        self.file_handler = FileHandler()
        self.zoom_enabled = False
        self.peak_aucs = {}  # Store calculated AUCs
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create frame widgets"""
        # Main container with two columns
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
    
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        title_label = ttk.Label(
            left_frame,
            text="Manual Peak Analysis",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        control_frame = ttk.LabelFrame(left_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        file_row = ttk.Frame(control_frame)
        file_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            file_row,
            text="Load File",
            command=self._load_file
        ).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(file_row, text="No file loaded", foreground='gray')
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        settings_row = ttk.Frame(control_frame)
        settings_row.pack(fill=tk.X, pady=5)
        
        self.has_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_row,
            text="Has Header",
            variable=self.has_header_var
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_row, text="Time Col:").pack(side=tk.LEFT, padx=5)
        self.time_col_var = tk.IntVar(value=1)
        ttk.Spinbox(
            settings_row,
            from_=1,
            to=50,
            textvariable=self.time_col_var,
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_row, text="Signal Col:").pack(side=tk.LEFT, padx=5)
        self.signal_col_var = tk.IntVar(value=2)
        ttk.Spinbox(
            settings_row,
            from_=1,
            to=50,
            textvariable=self.signal_col_var,
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
        correction_row = ttk.Frame(control_frame)
        correction_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(correction_row, text="Baseline:").pack(side=tk.LEFT, padx=5)
        self.baseline_var = tk.StringVar(value="None")
        ttk.Combobox(
            correction_row,
            textvariable=self.baseline_var,
            values=["None", "Linear", "Polynomial", "Als (Asymmetric Least Squares)"],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(correction_row, text="Noise:").pack(side=tk.LEFT, padx=5)
        self.noise_var = tk.StringVar(value="None")
        ttk.Combobox(
            correction_row,
            textvariable=self.noise_var,
            values=["None", "Moving Average", "Savitzky-Golay", "Gaussian"],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            correction_row,
            text="Apply Corrections",
            command=self._apply_corrections
        ).pack(side=tk.LEFT, padx=10)
        
        peak_row = ttk.Frame(control_frame)
        peak_row.pack(fill=tk.X, pady=5)
        
        self.peak_pick_var = tk.BooleanVar(value=False)
        self.peak_pick_btn = ttk.Checkbutton(
            peak_row,
            text="Enable Manual Picking",
            variable=self.peak_pick_var,
            command=self._toggle_peak_picking
        )
        self.peak_pick_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            peak_row,
            text="🔍 Auto Detect Peaks",
            command=self._auto_detect_peaks
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            peak_row,
            text="Clear All",
            command=self._clear_peaks
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            peak_row,
            text="Calculate AUC",
            command=self._calculate_picked_peaks
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            peak_row,
            text="Export",
            command=self._export_manual_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Auto-detect
        auto_row = ttk.Frame(control_frame)
        auto_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(auto_row, text="Auto-detect settings:").pack(side=tk.LEFT, padx=5)
        ttk.Label(auto_row, text="Height %:").pack(side=tk.LEFT, padx=5)
        self.peak_height_var = tk.DoubleVar(value=5.0)
        ttk.Spinbox(
            auto_row,
            from_=0.1,
            to=50.0,
            increment=0.5,
            textvariable=self.peak_height_var,
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(auto_row, text="Min Distance:").pack(side=tk.LEFT, padx=5)
        self.peak_distance_var = tk.IntVar(value=50)
        ttk.Spinbox(
            auto_row,
            from_=10,
            to=500,
            increment=10,
            textvariable=self.peak_distance_var,
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(auto_row, text="Width:").pack(side=tk.LEFT, padx=5)
        self.peak_width_var = tk.IntVar(value=20)
        ttk.Spinbox(
            auto_row,
            from_=5,
            to=200,
            increment=5,
            textvariable=self.peak_width_var,
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        # Plot area
        plot_frame = ttk.LabelFrame(left_frame, text="Chromatogram", padding=5)
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Time (min)')
        self.ax.set_ylabel('Signal (AU)')
        self.ax.set_title('Click "Load File" to start')
        self.ax.grid(True, alpha=0.3)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbar for zoom/pan
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Connect click event
        self.canvas.mpl_connect('button_press_event', self._on_plot_click)
        
        # Info label
        info_label = ttk.Label(
            left_frame,
            text="💡 Tip: Use 'Auto Detect' for automatic peak finding or enable manual picking to click on the plot",
            font=('Arial', 9, 'italic'),
            foreground='blue',
            wraplength=700
        )
        info_label.pack(pady=5)
        
        
        # Summary frame
        summary_frame = ttk.LabelFrame(right_frame, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=5)
        
        # Total AUC
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, pady=2)
        ttk.Label(total_frame, text="Total AUC:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.total_auc_label = ttk.Label(total_frame, text="0.00", font=('Arial', 10))
        self.total_auc_label.pack(side=tk.LEFT, padx=10)
        
        # Number of peaks
        peaks_frame = ttk.Frame(summary_frame)
        peaks_frame.pack(fill=tk.X, pady=2)
        ttk.Label(peaks_frame, text="Peaks Detected:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.num_peaks_label = ttk.Label(peaks_frame, text="0", font=('Arial', 10))
        self.num_peaks_label.pack(side=tk.LEFT, padx=10)
        
        # Separator
        ttk.Separator(summary_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Peak info display
        info_text_frame = ttk.Frame(summary_frame)
        info_text_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_text_frame, text="Peak Details:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        # Scrollable text for peak info
        info_scroll = ttk.Scrollbar(info_text_frame)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.peak_info_text = tk.Text(
            info_text_frame,
            height=8,
            width=30,
            font=('Arial', 9),
            yscrollcommand=info_scroll.set,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.peak_info_text.pack(fill=tk.BOTH, expand=True)
        info_scroll.config(command=self.peak_info_text.yview)
        
        # Picked peaks table
        table_frame = ttk.LabelFrame(right_frame, text="Peaks Table", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar and treeview
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.peaks_tree = ttk.Treeview(
            table_frame,
            columns=('Peak', 'Start', 'End', 'AUC', 'Percent'),
            show='headings',
            height=12,
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=self.peaks_tree.yview)
        
        self.peaks_tree.heading('Peak', text='Peak')
        self.peaks_tree.heading('Start', text='Start')
        self.peaks_tree.heading('End', text='End')
        self.peaks_tree.heading('AUC', text='AUC')
        self.peaks_tree.heading('Percent', text='%')
        
        self.peaks_tree.column('Peak', width=80)
        self.peaks_tree.column('Start', width=60)
        self.peaks_tree.column('End', width=60)
        self.peaks_tree.column('AUC', width=80)
        self.peaks_tree.column('Percent', width=60)
        
        self.peaks_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to remove peak
        self.peaks_tree.bind('<Double-Button-1>', self._remove_selected_peak)
        
        # Help label
        help_label = ttk.Label(
            right_frame,
            text="Double-click to remove peak",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        )
        help_label.pack(pady=2)
    
    def _load_file(self):
        """Load a data file"""
        filepath = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("All Supported", "*.csv *.txt *.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            # Read file
            df = self.file_handler.read_file(filepath, self.has_header_var.get())
            
            # Detect columns
            time_col, signal_col = self.file_handler.detect_columns(
                df, self.time_col_var.get(), self.signal_col_var.get()
            )
            
            # Get data
            self.time_data = df[time_col].values
            self.signal_data = df[signal_col].values
            self.original_signal = self.signal_data.copy()
            self.current_file = filepath
            
            # Update label
            self.file_label.config(
                text=os.path.basename(filepath),
                foreground='green'
            )
            
            # Plot
            self._plot_data()
            
            # Clear peaks
            self._clear_peaks()
            
            messagebox.showinfo("Success", f"Loaded {len(self.time_data)} data points")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def _plot_data(self):
        """Plot the current data"""
        if self.time_data is None:
            return
        
        self.ax.clear()
        self.ax.plot(self.time_data, self.signal_data, 'b-', linewidth=1.5, label='Signal')
        self.ax.set_xlabel('Time (min)', fontsize=11)
        self.ax.set_ylabel('Signal (AU)', fontsize=11)
        self.ax.set_title(f'Chromatogram: {os.path.basename(self.current_file) if self.current_file else ""}', 
                         fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Redraw peak markers
        self._redraw_peak_markers()
        
        self.canvas.draw()
    
    def _apply_corrections(self):
        """Apply baseline and noise corrections"""
        if self.signal_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            from core.baseline_correction import apply_baseline_correction
            from core.noise_correction import apply_noise_correction
            
            # Start with original signal
            corrected_signal = self.original_signal.copy()
            
            # Apply noise correction
            noise_method = self.noise_var.get()
            if noise_method != "None":
                corrected_signal = apply_noise_correction(corrected_signal, noise_method)
            
            # Apply baseline correction
            baseline_method = self.baseline_var.get()
            if baseline_method != "None":
                corrected_signal = apply_baseline_correction(
                    self.time_data, corrected_signal, baseline_method
                )
            
            # Update signal
            self.signal_data = corrected_signal
            
            # Replot
            self._plot_data()
            
            messagebox.showinfo("Success", "Corrections applied successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply corrections:\n{str(e)}")
    
    def _toggle_peak_picking(self):
        """Toggle peak picking mode"""
        if self.peak_pick_var.get():
            self.ax.set_title(f'Click on plot to pick peaks (Start → End)', fontsize=12, fontweight='bold')
            self.canvas.draw()
        else:
            self._plot_data()
    
    def _auto_detect_peaks(self):
        """Automatically detect peaks in the signal"""
        if self.signal_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            # Get parameters
            height_percent = self.peak_height_var.get()
            min_distance = self.peak_distance_var.get()
            min_width = self.peak_width_var.get()
            
            # Calculate height threshold
            height_threshold = np.max(self.signal_data) * (height_percent / 100.0)
            
            # Find peaks
            peak_indices, properties = find_peaks(
                self.signal_data,
                height=height_threshold,
                distance=min_distance,
                width=min_width
            )
            
            if len(peak_indices) == 0:
                messagebox.showinfo("Info", "No peaks detected. Try adjusting the parameters.")
                return
            
            # Clear existing peaks
            self.picked_peaks.clear()
            
            # For each detected peak, estimate boundaries
            widths = properties.get('widths', [min_width] * len(peak_indices))
            
            for idx, peak_idx in enumerate(peak_indices):
                # Estimate peak boundaries (using width information)
                half_width = int(widths[idx] / 2) if idx < len(widths) else min_width
                
                start_idx = max(0, peak_idx - half_width)
                end_idx = min(len(self.time_data) - 1, peak_idx + half_width)
                
                # Find local minimum before peak
                for i in range(peak_idx, start_idx, -1):
                    if i > 0 and self.signal_data[i] > self.signal_data[i-1]:
                        break
                    start_idx = i
                
                # Find local minimum after peak
                for i in range(peak_idx, end_idx):
                    if i < len(self.signal_data) - 1 and self.signal_data[i] > self.signal_data[i+1]:
                        break
                    end_idx = i
                
                start_time = self.time_data[start_idx]
                end_time = self.time_data[end_idx]
                
                self.picked_peaks.append([start_time, end_time])
            
            # Update plot
            self._plot_data()
            
            # Auto calculate
            self._calculate_picked_peaks()
            
            messagebox.showinfo("Success", f"Detected {len(peak_indices)} peaks")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect peaks:\n{str(e)}")
    
    def _on_plot_click(self, event):
        """Handle plot click for peak picking"""
        if not self.peak_pick_var.get() or event.inaxes != self.ax:
            return
        
        if self.time_data is None:
            return
        
        clicked_time = event.xdata
        
        # Find closest data point
        idx = np.argmin(np.abs(self.time_data - clicked_time))
        time_point = self.time_data[idx]
        signal_point = self.signal_data[idx]
        
        # Check if we're starting a new peak or ending one
        if len(self.picked_peaks) == 0 or len(self.picked_peaks[-1]) == 2:
            # Start new peak
            self.picked_peaks.append([time_point])
            
            # Draw marker
            marker = self.ax.plot(time_point, signal_point, 'go', markersize=10, 
                                 label=f'Peak {len(self.picked_peaks)} Start')[0]
            self.peak_markers.append(marker)
            
        else:
            # End current peak
            start_time = self.picked_peaks[-1][0]
            
            if time_point <= start_time:
                messagebox.showwarning("Warning", "End time must be greater than start time")
                return
            
            self.picked_peaks[-1].append(time_point)
            
            # Draw end marker
            marker = self.ax.plot(time_point, signal_point, 'ro', markersize=10,
                                 label=f'Peak {len(self.picked_peaks)} End')[0]
            self.peak_markers.append(marker)
            
            # Draw shaded region
            mask = (self.time_data >= start_time) & (self.time_data <= time_point)
            fill = self.ax.fill_between(self.time_data[mask], 0, self.signal_data[mask],
                                        alpha=0.3, label=f'Peak {len(self.picked_peaks)}')
            self.peak_markers.append(fill)
        
        self.ax.legend()
        self.canvas.draw()
    
    def _redraw_peak_markers(self):
        """Redraw all peak markers"""
        self.peak_markers.clear()
        
        for idx, peak in enumerate(self.picked_peaks):
            if len(peak) == 2:
                start_time, end_time = peak
                
                # Find signal values at these times
                start_idx = np.argmin(np.abs(self.time_data - start_time))
                end_idx = np.argmin(np.abs(self.time_data - end_time))
                
                # Draw markers
                self.ax.plot(start_time, self.signal_data[start_idx], 'go', markersize=10)
                self.ax.plot(end_time, self.signal_data[end_idx], 'ro', markersize=10)
                
                # Draw shaded region
                mask = (self.time_data >= start_time) & (self.time_data <= end_time)
                self.ax.fill_between(self.time_data[mask], 0, self.signal_data[mask],
                                    alpha=0.3, label=f'Peak {idx+1}')
    
    def _clear_peaks(self):
        """Clear all picked peaks"""
        self.picked_peaks.clear()
        self.peak_markers.clear()
        self.peak_aucs.clear()
        self.peaks_tree.delete(*self.peaks_tree.get_children())
        
        # Update summary
        self.total_auc_label.config(text="0.00")
        self.num_peaks_label.config(text="0")
        self._update_peak_info()
        
        if self.time_data is not None:
            self._plot_data()
    
    def _remove_selected_peak(self, event):
        """Remove selected peak from list"""
        selection = self.peaks_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.peaks_tree.item(item)['values']
        
        # Don't remove total row
        if values[0] == 'TOTAL':
            return
        
        peak_name = values[0]
        
        # Extract peak number
        try:
            peak_idx = int(peak_name.split('_')[1]) - 1
            
            if 0 <= peak_idx < len(self.picked_peaks):
                del self.picked_peaks[peak_idx]
                self._calculate_picked_peaks()
                self._plot_data()
        except:
            pass
    
    def _calculate_picked_peaks(self):
        """Calculate AUC for picked peaks"""
        if not self.picked_peaks or self.time_data is None:
            return
        
        # Filter complete peaks
        complete_peaks = [p for p in self.picked_peaks if len(p) == 2]
        
        if not complete_peaks:
            return
        
        try:
            # Create AUC calculator
            calculator = AUCCalculator(
                baseline_method=self.baseline_var.get(),
                noise_method=self.noise_var.get()
            )
            
            # Clear tree and aucs
            self.peaks_tree.delete(*self.peaks_tree.get_children())
            self.peak_aucs.clear()
            
            # Calculate each peak
            total_auc = 0
            for idx, (start, end) in enumerate(complete_peaks):
                auc = calculator.calculate_auc(self.time_data, self.signal_data, start, end)
                total_auc += auc
                peak_name = f'Peak_{idx+1}'
                self.peak_aucs[peak_name] = {
                    'auc': auc,
                    'start': start,
                    'end': end
                }
            
            # Insert peaks with percentages
            for peak_name, data in self.peak_aucs.items():
                percent = (data['auc'] / total_auc * 100) if total_auc > 0 else 0
                self.peaks_tree.insert('', tk.END, values=(
                    peak_name,
                    f"{data['start']:.3f}",
                    f"{data['end']:.3f}",
                    f"{data['auc']:.2f}",
                    f"{percent:.2f}%"
                ))
            
            # Add total
            self.peaks_tree.insert('', tk.END, values=(
                'TOTAL',
                '-',
                '-',
                f'{total_auc:.2f}',
                '100.00%'
            ), tags=('total',))
            
            # Style total row
            self.peaks_tree.tag_configure('total', font=('Arial', 10, 'bold'), background='#e8f4f8')
            
            # Update summary
            self.total_auc_label.config(text=f"{total_auc:.2f}")
            self.num_peaks_label.config(text=str(len(complete_peaks)))
            
            # Update peak info text
            self._update_peak_info()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate AUC:\n{str(e)}")
    
    def _update_peak_info(self):
        """Update the peak information text display"""
        self.peak_info_text.config(state=tk.NORMAL)
        self.peak_info_text.delete(1.0, tk.END)
        
        if not self.peak_aucs:
            self.peak_info_text.insert(tk.END, "No peaks calculated yet.\n\n")
            self.peak_info_text.insert(tk.END, "Pick peaks manually or use\nauto-detect, then click\n'Calculate AUC'.")
        else:
            total = sum(data['auc'] for data in self.peak_aucs.values())
            
            for peak_name, data in self.peak_aucs.items():
                percent = (data['auc'] / total * 100) if total > 0 else 0
                self.peak_info_text.insert(tk.END, f"{peak_name}:\n", 'bold')
                self.peak_info_text.insert(tk.END, f"  Range: {data['start']:.3f} - {data['end']:.3f}\n")
                self.peak_info_text.insert(tk.END, f"  AUC: {data['auc']:.2f}\n")
                self.peak_info_text.insert(tk.END, f"  Percentage: {percent:.2f}%\n\n")
            
            self.peak_info_text.insert(tk.END, "─" * 30 + "\n", 'separator')
            self.peak_info_text.insert(tk.END, f"Total AUC: {total:.2f}\n", 'bold')
        
        # Configure tags
        self.peak_info_text.tag_configure('bold', font=('Arial', 9, 'bold'))
        self.peak_info_text.tag_configure('separator', foreground='gray')
        
        self.peak_info_text.config(state=tk.DISABLED)
    
    def _export_manual_results(self):
        """Export manual analysis results"""
        if not self.peaks_tree.get_children():
            messagebox.showwarning("Warning", "No results to export")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            import pandas as pd
            
            # Collect data
            data = []
            for item in self.peaks_tree.get_children():
                values = self.peaks_tree.item(item)['values']
                data.append({
                    'Peak': values[0],
                    'Start_Time': values[1],
                    'End_Time': values[2],
                    'AUC': values[3],
                    'Percentage': values[4]
                })
            
            df = pd.DataFrame(data)
            
            # Add metadata
            metadata = {
                'File': [os.path.basename(self.current_file) if self.current_file else 'N/A'],
                'Baseline_Correction': [self.baseline_var.get()],
                'Noise_Correction': [self.noise_var.get()]
            }
            metadata_df = pd.DataFrame(metadata)
            
            if filepath.endswith('.csv'):
                with open(filepath, 'w') as f:
                    f.write("# Metadata\n")
                    metadata_df.to_csv(f, index=False)
                    f.write("\n# Peak Data\n")
                    df.to_csv(f, index=False)
            else:
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                    df.to_excel(writer, sheet_name='Peaks', index=False)
            
            messagebox.showinfo("Success", f"Results exported to:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")