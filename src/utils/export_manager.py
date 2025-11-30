"""Export manager for results"""
import os
from pathlib import Path
from datetime import datetime
import pandas as pd


class ExportManager:
    """Manager for exporting results"""
    
    def __init__(self):
        self.serial_number = 1
    
    @staticmethod
    def get_default_save_directory():
        """Get default directory for saving results (user's Documents folder)"""
        # Get user's home directory
        home = Path.home()
        
        # Try Documents folder first, fall back to Downloads, then home
        docs_folder = home / "Documents"
        downloads_folder = home / "Downloads"
        
        if docs_folder.exists() and os.access(docs_folder, os.W_OK):
            return str(docs_folder)
        elif downloads_folder.exists() and os.access(downloads_folder, os.W_OK):
            return str(downloads_folder)
        else:
            return str(home)
    
    def export_results(self, results, output_path=None, file_format='xlsx'):
        """
        Export results to file
        
        Args:
            results: List of result dictionaries
            output_path: Output file path (optional, will use default location if not provided)
            file_format: File format ('csv' or 'xlsx')
            
        Returns:
            Path to saved file
        """
        if not results:
            raise ValueError("No results to export")
        
        # Determine the final output path
        if output_path is None:
            # No path provided, use default location
            save_dir = self.get_default_save_directory()
            filename = self.generate_output_filename("hplc_results", file_format)
            output_path = os.path.join(save_dir, filename)
        else:
            # Path provided, but check if it's writable
            # If path is just a filename (no directory), use default directory
            if os.path.dirname(output_path) == '':
                save_dir = self.get_default_save_directory()
                output_path = os.path.join(save_dir, output_path)
            else:
                # Check if the directory is writable
                directory = os.path.dirname(output_path)
                
                # Try to create directory if it doesn't exist
                try:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                except (OSError, PermissionError):
                    # Can't create directory, use default location
                    save_dir = self.get_default_save_directory()
                    filename = os.path.basename(output_path)
                    output_path = os.path.join(save_dir, filename)
                    print(f"Warning: Cannot create directory. Saving to: {output_path}")
                
                # Check if directory is writable
                if os.path.exists(directory) and not os.access(directory, os.W_OK):
                    # Directory not writable, use default location
                    save_dir = self.get_default_save_directory()
                    filename = os.path.basename(output_path)
                    output_path = os.path.join(save_dir, filename)
                    print(f"Warning: Directory not writable. Saving to: {output_path}")
        
        # Final check: ensure we can write to the location
        final_directory = os.path.dirname(output_path)
        if final_directory and not os.access(final_directory, os.W_OK):
            # Still not writable, use home directory as last resort
            home = str(Path.home())
            filename = os.path.basename(output_path)
            output_path = os.path.join(home, filename)
            print(f"Warning: Using home directory: {output_path}")
        
        # Create DataFrame and export
        df = pd.DataFrame(results)
        
        try:
            if file_format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                self._export_to_excel(df, output_path)
            
            print(f"✓ Results exported successfully to: {output_path}")
            return output_path
            
        except (OSError, PermissionError) as e:
            # Last resort: save to home directory
            home = str(Path.home())
            filename = os.path.basename(output_path)
            output_path = os.path.join(home, filename)
            print(f"Error: {e}")
            print(f"Attempting to save to home directory: {output_path}")
            
            if file_format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                self._export_to_excel(df, output_path)
            
            return output_path
    
    def _export_to_excel(self, df, output_path):
        """Export to Excel with formatting"""
        try:
            from openpyxl.styles import Font, Alignment
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
                
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
                
                # Format percentage columns
                for row_idx in range(2, len(df) + 2):
                    for col_idx, col_name in enumerate(df.columns, start=1):
                        if '%' in str(col_name):
                            cell = worksheet.cell(row=row_idx, column=col_idx)
                            cell.number_format = '0.00'
        except ImportError:
            # Fallback if openpyxl is not available
            df.to_excel(output_path, index=False)
    
    def append_to_log(self, result, log_path=None):
        """
        Append single result to log file
        
        Args:
            result: Result dictionary
            log_path: Log file path (optional, will use default location if not provided)
            
        Returns:
            Path to log file
        """
        # Always use default location for logs
        save_dir = self.get_default_save_directory()
        
        if log_path is None:
            log_path = os.path.join(save_dir, "hplc_analysis_log.csv")
        else:
            # If log_path provided but not writable, use default location
            if os.path.dirname(log_path) == '':
                log_path = os.path.join(save_dir, log_path)
            elif not os.access(os.path.dirname(log_path), os.W_OK):
                filename = os.path.basename(log_path)
                log_path = os.path.join(save_dir, filename)
                print(f"Warning: Log directory not writable. Saving to: {log_path}")
        
        result_copy = result.copy()
        result_copy['Serial'] = self.serial_number
        result_copy['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            if os.path.exists(log_path):
                df = pd.DataFrame([result_copy])
                df.to_csv(log_path, mode='a', header=False, index=False)
            else:
                df = pd.DataFrame([result_copy])
                df.to_csv(log_path, index=False)
            
            self.serial_number += 1
            return log_path
            
        except (OSError, PermissionError) as e:
            # Last resort: save to home directory
            home = str(Path.home())
            filename = os.path.basename(log_path)
            log_path = os.path.join(home, filename)
            print(f"Error: {e}")
            print(f"Saving log to home directory: {log_path}")
            
            if os.path.exists(log_path):
                df = pd.DataFrame([result_copy])
                df.to_csv(log_path, mode='a', header=False, index=False)
            else:
                df = pd.DataFrame([result_copy])
                df.to_csv(log_path, index=False)
            
            self.serial_number += 1
            return log_path
    
    def generate_output_filename(self, base_name, file_format='xlsx'):
        """Generate timestamped output filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{file_format}"
    
    def reset_serial(self):
        """Reset serial number counter"""
        self.serial_number = 1