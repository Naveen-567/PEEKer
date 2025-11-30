import unittest
from src.core.file_processor import FileProcessor

class TestFileProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = FileProcessor()

    def test_read_csv_with_headers(self):
        result = self.processor.read_file('tests/test_data_with_headers.csv')
        self.assertIsNotNone(result)
        self.assertIn('time', result.columns)
        self.assertIn('signal', result.columns)

    def test_read_csv_without_headers(self):
        result = self.processor.read_file('tests/test_data_without_headers.csv')
        self.assertIsNotNone(result)
        self.assertEqual(result.shape[1], 2)  # Assuming two columns for time and signal

    def test_process_data(self):
        data = self.processor.read_file('tests/test_data_with_headers.csv')
        processed_data = self.processor.process_data(data)
        self.assertIsNotNone(processed_data)
        self.assertGreater(len(processed_data), 0)

    def test_noise_correction(self):
        data = self.processor.read_file('tests/test_data_with_headers.csv')
        corrected_data = self.processor.apply_noise_correction(data)
        self.assertIsNotNone(corrected_data)

    def test_baseline_correction(self):
        data = self.processor.read_file('tests/test_data_with_headers.csv')
        corrected_data = self.processor.apply_baseline_correction(data)
        self.assertIsNotNone(corrected_data)

if __name__ == '__main__':
    unittest.main()