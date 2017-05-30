import unittest

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from coverage_manager.helpers.coveralls_helper import CoverallsHelper


class CoverallsHelperTest(unittest.TestCase):
    def setUp(self):
        self.coveralls = CoverallsHelper('jlmdegoede', 'MOOCworkbench')
        self.non_existent_coveralls = CoverallsHelper('jlmdegoede', 'NON_EXISTENT_REPOSITORY')

    def test_init(self):
        self.assertIsNotNone(self.coveralls)

    def test_code_coverage_data(self):
        self.assertIsInstance(self.coveralls.code_coverage_data(), float)

    def test_code_coverage_data_non_existent(self):
        self.assertIsNone(self.non_existent_coveralls.code_coverage_data())

    def test_coverage_enabled_check(self):
        self.assertTrue(self.coveralls.coverage_enabled_check())

    def test_coverage_enabled_check_not_enabled(self):
        self.assertFalse(self.non_existent_coveralls.coverage_enabled_check())

    def test_get_badge_url(self):
        badge_url = self.coveralls.get_badge_url()
        val = URLValidator()
        val(badge_url)

    def test_get_badge_url_invalid(self):
        badge_url = self.non_existent_coveralls.get_badge_url()
        val = URLValidator()
        self.assertRaises(ValidationError, val, badge_url)
