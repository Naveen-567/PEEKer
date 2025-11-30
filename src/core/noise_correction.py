"""Noise correction algorithms"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

class NoiseCorrector:
    """Applies various noise correction methods"""
    
    @staticmethod
    def apply_correction(signal, method='None', **kwargs):
        """
        Apply noise correction
        
        Args:
            signal: Signal array
            method: Correction method
            **kwargs: Method-specific parameters
        
        Returns:
            Corrected signal
        """
        if method == 'None' or method is None:
            return signal
        elif method == 'Moving Average':
            window_size = kwargs.get('window_size', 5)
            return NoiseCorrector.moving_average(signal, window_size)
        elif method == 'Savitzky-Golay':
            window_size = kwargs.get('window_size', 11)
            poly_order = kwargs.get('poly_order', 3)
            return NoiseCorrector.savitzky_golay(signal, window_size, poly_order)
        elif method == 'Gaussian':
            sigma = kwargs.get('sigma', 2.0)
            return NoiseCorrector.gaussian_smooth(signal, sigma)
        else:
            return signal
    
    @staticmethod
    def moving_average(signal, window_size=5):
        """Moving average smoothing"""
        signal_arr = np.array(signal)
        if window_size < 1:
            return signal_arr
        
        window_size = min(window_size, len(signal_arr))
        if window_size % 2 == 0:
            window_size += 1
        
        return np.convolve(signal_arr, np.ones(window_size)/window_size, mode='same')
    
    @staticmethod
    def savitzky_golay(signal, window_size=11, poly_order=3):
        """Savitzky-Golay filter"""
        signal_arr = np.array(signal)
        
        if len(signal_arr) < window_size:
            window_size = len(signal_arr) if len(signal_arr) % 2 == 1 else len(signal_arr) - 1
        
        if window_size < poly_order + 2:
            poly_order = max(1, window_size - 2)
        
        if window_size % 2 == 0:
            window_size += 1
        
        try:
            return savgol_filter(signal_arr, window_size, poly_order)
        except:
            return signal_arr
    
    @staticmethod
    def gaussian_smooth(signal, sigma=2.0):
        """Gaussian smoothing"""
        return gaussian_filter1d(np.array(signal), sigma=sigma)


def apply_noise_correction(signal, method='None', **kwargs):
    """
    Convenience function for noise correction
    
    Args:
        signal: Signal array
        method: Correction method
        **kwargs: Method-specific parameters
    
    Returns:
        Corrected signal
    """
    return NoiseCorrector.apply_correction(signal, method, **kwargs)

def remove_noise_from_file(input_file, output_file, method='median', window_size=5):
    """Reads a file, applies noise correction, and saves the corrected signal."""
    df = pd.read_csv(input_file, header=None)
    signal = df.iloc[:, 0].to_numpy()
    corrected_signal = apply_noise_correction(signal, method, window_size)
    
    corrected_df = pd.DataFrame(corrected_signal)
    corrected_df.to_csv(output_file, index=False, header=False)