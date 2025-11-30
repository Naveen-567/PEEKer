import unittest
from src.core.baseline_correction import baseline_correction_function
from src.core.noise_correction import noise_correction_function

class TestCorrections(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.signal_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.noisy_signal_data = [1, 2, 1, 4, 5, 3, 7, 8, 10, 9]
        self.baseline_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_baseline_correction(self):
        corrected_signal = baseline_correction_function(self.signal_data, self.baseline_data)
        expected_signal = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Assuming no baseline shift
        self.assertEqual(corrected_signal, expected_signal)

    def test_noise_correction(self):
        corrected_signal = noise_correction_function(self.noisy_signal_data)
        expected_signal = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Expected output after noise correction
        self.assertEqual(corrected_signal, expected_signal)

if __name__ == '__main__':
    unittest.main()