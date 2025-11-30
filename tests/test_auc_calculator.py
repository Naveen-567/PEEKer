import unittest
from src.core.auc_calculator import AUCCalculator

class TestAUCCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = AUCCalculator()

    def test_auc_calculation(self):
        # Sample data for testing
        time_data = [0, 1, 2, 3, 4, 5]
        signal_data = [0, 1, 0, 1, 0, 0]
        peaks = [(1, 2), (3, 4)]  # Define peak ranges

        # Calculate AUC for the defined peaks
        auc_results = self.calculator.calculate_auc(time_data, signal_data, peaks)

        # Expected results (manually calculated or based on known values)
        expected_results = {
            'peak_1_auc': 1.0,  # Example expected AUC for peak 1
            'peak_2_auc': 1.0,  # Example expected AUC for peak 2
            'total_auc': 2.0    # Example total AUC
        }

        self.assertEqual(auc_results, expected_results)

    def test_auc_with_no_peaks(self):
        time_data = [0, 1, 2, 3, 4, 5]
        signal_data = [0, 0, 0, 0, 0, 0]
        peaks = []  # No peaks defined

        # Calculate AUC for the defined peaks
        auc_results = self.calculator.calculate_auc(time_data, signal_data, peaks)

        # Expected results when no peaks are defined
        expected_results = {
            'peak_1_auc': 0.0,
            'peak_2_auc': 0.0,
            'total_auc': 0.0
        }

        self.assertEqual(auc_results, expected_results)

    def test_auc_with_invalid_data(self):
        time_data = [0, 1, 2, 3, 4, 5]
        signal_data = [1, 2, 3, 4, 5]  # Mismatched lengths
        peaks = [(1, 2)]

        with self.assertRaises(ValueError):
            self.calculator.calculate_auc(time_data, signal_data, peaks)

if __name__ == '__main__':
    unittest.main()