"""Processing frame for executing AUC calculations"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from datetime import datetime
from core.file_processor import FileProcessor
from utils.export_manager import ExportManager
from config.settings import PADDING


class ProcessingFrame:
    """Frame for processing controls"""
    
    def __init__(self, parent, file_upload_frame, peak_config_frame, results_frame):
        self.frame = ttk.Frame(parent, padding=PADDING)
        self.file_upload_frame = file_upload_frame
        self.peak_config_frame = peak_config_frame
        self.results_frame = results_frame
        
        self.processing = False
        self.export_manager = ExportManager()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create frame widgets"""
        # Title
        title_label = ttk.Label(
            self.frame, 
            text="Processing", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Export settings
        export_frame = ttk.LabelFrame(self.frame, text="Export Settings", padding=10)
        export_frame.pack(fill=tk.X, pady=10)
        
        # Output filename
        filename_frame = ttk.Frame(export_frame)
        filename_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filename_frame, text="Output Filename:").pack(side=tk.LEFT, padx=5)
        self.output_name_var = tk.StringVar(value="hplc_results")
        ttk.Entry(
            filename_frame,
            textvariable=self.output_name_var,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Logging option
        self.enable_logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            export_frame,
            text="Enable continuous logging (single file mode)",
            variable=self.enable_logging_var
        ).pack(anchor=tk.W, pady=5)
        
        # Processing button
        self.process_btn = ttk.Button(
            self.frame,
            text="▶ Start Processing",
            command=self._start_processing
        )
        self.process_btn.pack(pady=20)
        
        # Progress
        progress_frame = ttk.LabelFrame(self.frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to process")
        self.status_label.pack(pady=5)
        
        # Log text
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    def _log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _start_processing(self):
        """Start processing"""
        # Validate
        if not self.file_upload_frame.get_selected_files():
            messagebox.showwarning("Warning", "Please select files to process")
            return
        
        if not self.peak_config_frame.validate():
            return
        
        # Start processing thread
        self.processing = True
        self.process_btn.config(state=tk.DISABLED, text="Processing...")
        self.progress_bar.start()
        self.status_label.config(text="Processing...")
        
        thread = threading.Thread(target=self._process, daemon=True)
        thread.start()
    
    def _process(self):
        """Process files in background"""
        try:
            # Get settings
            files = self.file_upload_frame.get_selected_files()
            is_folder = self.file_upload_frame.is_folder_mode()
            has_header = self.file_upload_frame.has_header()
            time_col = self.file_upload_frame.get_time_column_index()
            signal_col = self.file_upload_frame.get_signal_column_index()
            
            peaks = self.peak_config_frame.get_peaks()
            baseline_method = self.peak_config_frame.get_baseline_method()
            noise_method = self.peak_config_frame.get_noise_method()
            total_method = self.peak_config_frame.get_total_calculation_method()
            
            # Prepare custom total range if selected
            custom_total_range = None
            if total_method == "custom":
                custom_total = self.peak_config_frame.get_custom_total_peak()
                custom_total_range = (
                    custom_total['start'], 
                    custom_total['end'], 
                    custom_total['name']
                )
                self._log(f"Custom total peak: {custom_total['name']} ({custom_total['start']}-{custom_total['end']})")
                self._log("Both standard (sum of peaks) and custom total will be calculated")
            elif total_method == "all":
                self._log("Total calculation: Sum of ALL peaks")
            else:
                included_peaks = [p['name'] for p in peaks if p['include_in_total']]
                self._log(f"Total calculation: Sum of SELECTED peaks: {', '.join(included_peaks)}")
            
            # Create processor
            processor = FileProcessor(
                has_header=has_header,
                time_col_idx=time_col,
                signal_col_idx=signal_col,
                baseline_method=baseline_method,
                noise_method=noise_method
            )
            
            peak_ranges = [(p['start'], p['end']) for p in peaks]
            peak_names = [p['name'] for p in peaks]
            include_in_total = [p['include_in_total'] for p in peaks]
            
            results = []
            
            if is_folder:
                folder = files[0]
                self._log(f"Processing folder: {folder}")
                
                def progress_callback(current, total, filename, success):
                    status = "✓" if success else "✗"
                    self.frame.after(0, self._log, f"{status} [{current}/{total}] {filename}")
                
                results = processor.process_folder(
                    folder,
                    peak_ranges,
                    peak_names,
                    include_in_total,
                    custom_total_range,
                    progress_callback
                )
                
                # Export
                output_format = self.file_upload_frame.get_export_format()
                output_file = self.export_manager.generate_output_filename(
                    self.output_name_var.get(),
                    output_format
                )
                
                self.export_manager.export_results(results, output_file, output_format)
                self._log(f"\n✓ Results exported to: {output_file}")
                
            else:
                for idx, file in enumerate(files):
                    self._log(f"Processing: {os.path.basename(file)}")
                    
                    try:
                        result = processor.process_single_file(
                            file, 
                            peak_ranges, 
                            peak_names,
                            include_in_total,
                            custom_total_range
                        )
                        results.append(result)
                        self._log(f"  ✓ Success")
                        
                        if self.enable_logging_var.get():
                            log_file = f"{self.output_name_var.get()}_log.csv"
                            self.export_manager.append_to_log(result, log_file)
                            self._log(f"  → Logged to: {log_file}")
                    
                    except Exception as e:
                        self._log(f"  ✗ Error: {str(e)}")
                
                # Export combined
                if results:
                    output_file = self.export_manager.generate_output_filename(
                        self.output_name_var.get(),
                        'xlsx'
                    )
                    self.export_manager.export_results(results, output_file, 'xlsx')
                    self._log(f"\n✓ Results exported to: {output_file}")
            
            # Update results
            if results:
                self.frame.after(0, self.results_frame.display_results, results)
            
            self._log(f"\n{'='*50}")
            self._log(f"Processing complete! {len(results)} file(s) processed")
            self._log(f"{'='*50}")
            
            self.frame.after(0, messagebox.showinfo, "Success", 
                           f"Processing complete!\n{len(results)} file(s) processed")
        
        except Exception as e:
            self._log(f"\n✗ Error: {str(e)}")
            self.frame.after(0, messagebox.showerror, "Error", f"Processing failed:\n{str(e)}")
        
        finally:
            self.processing = False
            self.frame.after(0, self._processing_complete)
    
    def _processing_complete(self):
        """Clean up after processing"""
        self.progress_bar.stop()
        self.process_btn.config(state=tk.NORMAL, text="▶ Start Processing")
        self.status_label.config(text="Ready to process")