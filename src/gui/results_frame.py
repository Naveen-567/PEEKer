"""Results display frame"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from config.settings import PADDING


class ResultsFrame:
    """Frame for displaying results"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=PADDING)
        self.current_results = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create frame widgets"""
        # Title
        title_label = ttk.Label(
            self.frame, 
            text="Results", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame,
            text="Export Results",
            command=self._export_results
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Clear Results",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Results frame with treeview
        results_container = ttk.Frame(self.frame)
        results_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(results_container)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(results_container, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            results_container,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No results to display")
        self.status_label.pack(pady=5)
    
    def display_results(self, results):
        """Display results in treeview"""
        self.current_results = results
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        if not results:
            self.status_label.config(text="No results to display")
            return
        
        # Get column names from first result
        columns = list(results[0].keys())
        
        # Configure treeview
        self.tree['columns'] = columns
        self.tree.column('#0', width=0, stretch=tk.NO)
        
        for col in columns:
            self.tree.column(col, anchor=tk.CENTER, width=100)
            self.tree.heading(col, text=col, anchor=tk.CENTER)
        
        # Insert data
        for idx, result in enumerate(results):
            values = [result.get(col, '') for col in columns]
            self.tree.insert('', tk.END, text=str(idx), values=values)
        
        self.status_label.config(text=f"Displaying {len(results)} result(s)")
    
    def clear_results(self):
        """Clear displayed results"""
        if not self.current_results:
            messagebox.showinfo("Info", "No results to clear")
            return
        
        if messagebox.askyesno("Clear Results", "Are you sure you want to clear the results?"):
            self.tree.delete(*self.tree.get_children())
            self.current_results = []
            self.status_label.config(text="No results to display")
    
    def _export_results(self):
        """Export current results"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.current_results)
                
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False)
                else:
                    # Export to Excel with formatting
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Results', index=False)
                        
                        try:
                            from openpyxl.styles import Font, Alignment
                            
                            # Format worksheet
                            workbook = writer.book
                            worksheet = writer.sheets['Results']
                            
                            # Format header
                            for cell in worksheet[1]:
                                cell.font = Font(bold=True)
                                cell.alignment = Alignment(horizontal='center')
                            
                            # Auto-adjust column widths
                            for column in worksheet.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    try:
                                        if len(str(cell.value)) > max_length:
                                            max_length = len(str(cell.value))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                worksheet.column_dimensions[column_letter].width = adjusted_width
                        except ImportError:
                            pass  # Skip formatting if openpyxl not available
                
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def get_results(self):
        """Get current results"""
        return self.current_results
