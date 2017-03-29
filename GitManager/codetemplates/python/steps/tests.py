import unittest
from {0}.main import main

class TestMain(unittest.TestCase):

    def test_main_runs(self):
        self.assertEqual(main(), True)
