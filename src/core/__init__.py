"""Core processing package"""
from .file_processor import FileProcessor
from .auc_calculator import AUCCalculator
from .baseline_correction import BaselineCorrector, apply_baseline_correction
from .noise_correction import NoiseCorrector, apply_noise_correction

__all__ = [
    'FileProcessor',
    'AUCCalculator',
    'BaselineCorrector',
    'apply_baseline_correction',
    'NoiseCorrector',
    'apply_noise_correction'
]