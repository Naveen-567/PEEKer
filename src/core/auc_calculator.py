#used trpz rule
import numpy as np
from core.baseline_correction import apply_baseline_correction
from core.noise_correction import apply_noise_correction


class AUCCalculator:
    """Calculate Area Under Curve"""
    
    def __init__(self, baseline_method='None', noise_method='None',
                 baseline_params=None, noise_params=None):
        self.baseline_method = baseline_method
        self.noise_method = noise_method
        self.baseline_params = baseline_params or {}
        self.noise_params = noise_params or {}
    
    def calculate_auc(self, time, signal, xi, xf):
        """
        Calculate AUC for given time range using trapez. rule
        
        Args:
            time: Time array
            signal: Signal array
            xi: Start time (target peak)
            xf: End time
        
        Returns:
            AUC value
        """
        # Convert to numpy arrays
        time_arr = np.array(time)
        signal_arr = np.array(signal)
        
        mask = (time_arr >= xi) & (time_arr <= xf)
        filtered_time = time_arr[mask]
        filtered_signal = signal_arr[mask]
        
        if len(filtered_time) < 2:
            raise ValueError(f"Insufficient data points between {xi} and {xf}")
        

        if self.noise_method != 'None':
            filtered_signal = apply_noise_correction(
                filtered_signal,
                self.noise_method,
                **self.noise_params
            )
        
        if self.baseline_method != 'None':
            filtered_signal = apply_baseline_correction(
                filtered_time,
                filtered_signal,
                self.baseline_method,
                **self.baseline_params
            )

        auc = np.trapz(filtered_signal, filtered_time)
        
        return max(0, auc)  # Ensure non-negative
    
    def calculate_multiple_peaks(self, time, signal, peak_ranges, peak_names, 
                                 include_in_total=None, custom_total_range=None):
        """
        Calculate AUC for multiple peaks
        
        Args:
            time: Time array
            signal: Signal array
            peak_ranges: List of (start, end) tuples
            peak_names: List of peak names
            include_in_total: List of boolean values indicating which peaks to include in total
                             If None, all peaks are included
            custom_total_range: Tuple of (start, end, name) for custom total peak
                               If provided, calculates both standard and custom total
        
        Returns:
            Dictionary with results
        """
        results = {}
        standard_total_auc = 0
        

        if include_in_total is None:
            include_in_total = [True] * len(peak_names)

        for idx, (peak_name, (xi, xf)) in enumerate(zip(peak_names, peak_ranges)):
            try:
                auc = self.calculate_auc(time, signal, xi, xf)
                results[peak_name] = auc
                
                if include_in_total[idx]:
                    standard_total_auc += auc
                    
            except Exception as e:
                results[peak_name] = 0
                results[f'{peak_name}_error'] = str(e)
        
        if custom_total_range:
            custom_start, custom_end, custom_name = custom_total_range
            try:
                custom_total_auc = self.calculate_auc(time, signal, custom_start, custom_end)
                results[f'{custom_name}'] = custom_total_auc
                
                for peak_name in peak_names:
                    if custom_total_auc > 0:
                        results[f'{peak_name}_%_Custom'] = (results.get(peak_name, 0) / custom_total_auc) * 100
                    else:
                        results[f'{peak_name}_%_Custom'] = 0
                
            except Exception as e:
                results[f'{custom_name}'] = 0
                results[f'{custom_name}_error'] = str(e)
                custom_total_auc = 0

        results['Total_Standard'] = standard_total_auc
        
        for idx, peak_name in enumerate(peak_names):
            if include_in_total[idx] and standard_total_auc > 0:
                results[f'{peak_name}_%_Standard'] = (results.get(peak_name, 0) / standard_total_auc) * 100
            else:
                results[f'{peak_name}_%_Standard'] = 0
        
        if not custom_total_range:
            results['Total'] = results.pop('Total_Standard')
            for peak_name in peak_names:
                if f'{peak_name}_%_Standard' in results:
                    results[f'{peak_name}_%'] = results.pop(f'{peak_name}_%_Standard')
        
        return results