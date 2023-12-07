import unittest
from casting_decoder import get_search_terms, main

class TestCastingDecoder(unittest.TestCase):
    def test_main(self):
        # Test if the search_terms function returns the expected results
        result = main(search_terms='3C3E FORD 2l3e 6.8L')
        self.assertIsNotNone(result)  # Assert that the result is not None
        self.assertIsInstance(result, dict)  # Assert that the result is a list


if __name__ == '__main__':
    unittest.main()