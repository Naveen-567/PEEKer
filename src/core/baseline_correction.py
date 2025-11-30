"""Baseline correction algorithms"""
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import spsolve

class BaselineCorrector:
    """Applies various baseline correction methods"""
    
    @staticmethod
    def apply_correction(time, signal, method='None', **kwargs):
        """
        Apply baseline correction
        
        Args:
            time: Time array
            signal: Signal array
            method: Correction method
            **kwargs: Method-specific parameters
        
        Returns:
            Corrected signal
        """
        if method == 'None' or method is None:
            return signal
        elif method == 'Linear':
            return BaselineCorrector.linear_baseline(time, signal)
        elif method == 'Polynomial':
            degree = kwargs.get('degree', 2)
            return BaselineCorrector.polynomial_baseline(time, signal, degree)
        elif method == 'Als (Asymmetric Least Squares)':
            lam = kwargs.get('lam', 1e5)
            p = kwargs.get('p', 0.01)
            niter = kwargs.get('niter', 10)
            return BaselineCorrector.als_baseline(signal, lam, p, niter)
        else:
            return signal
    
    @staticmethod
    def linear_baseline(time, signal):
        """Linear baseline correction"""
        time_arr = np.array(time)
        signal_arr = np.array(signal)
        
        slope = (signal_arr[-1] - signal_arr[0]) / (time_arr[-1] - time_arr[0])
        intercept = signal_arr[0] - slope * time_arr[0]
        baseline = slope * time_arr + intercept
        
        return signal_arr - baseline
    
    @staticmethod
    def polynomial_baseline(time, signal, degree=2):
        """Polynomial baseline correction"""
        time_arr = np.array(time)
        signal_arr = np.array(signal)
        
        coeffs = np.polyfit(time_arr, signal_arr, degree)
        baseline = np.polyval(coeffs, time_arr)
        
        return signal_arr - baseline
    
    @staticmethod
    def als_baseline(signal, lam=1e5, p=0.01, niter=10):
        """Asymmetric Least Squares baseline correction"""
        signal_arr = np.array(signal)
        L = len(signal_arr)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2))
        D = lam * D.dot(D.transpose())
        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)
        
        for i in range(niter):
            W.setdiag(w)
            Z = W + D
            z = spsolve(Z, w * signal_arr)
            w = p * (signal_arr > z) + (1 - p) * (signal_arr < z)
        
        return signal_arr - z


def apply_baseline_correction(time, signal, method='None', **kwargs):
    """
    Convenience function for baseline correction
    
    Args:
        time: Time array
        signal: Signal array
        method: Correction method
        **kwargs: Method-specific parameters
    
    Returns:
        Corrected signal
    """
    return BaselineCorrector.apply_correction(time, signal, method, **kwargs)

def correct_baseline_from_file(file_path, method='linear'):
    df = pd.read_csv(file_path, header=None)
    signal = df.iloc[:, 0].values  # Assuming the signal is in the first column
    corrected_signal = baseline_correction(signal, method)
    return corrected_signal