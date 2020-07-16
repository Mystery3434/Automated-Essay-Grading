import unittest

# (Optional) surpress the warning on loading tensorflow package
import warnings
warnings.filterwarnings('ignore')

from main import process_text

class TestProcessText(unittest.TestCase):
    def test_process_text(self):
        input_text = "Hello"

        result = process_text(input_text)

        self.assertEqual(result, "This is the result by yourapp with: Hello")

if __name__ == '__main__':
    unittest.main()
