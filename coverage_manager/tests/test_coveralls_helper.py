import unittest

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from coverage_manager.helpers.coveralls_helper import CoverallsHelper


class CoverallsHelperTest(unittest.TestCase):
    """Tests for the class that interacts with Coveralls API"""
    def setUp(self):
        self.coveralls = CoverallsHelper('jlmdegoede', 'MOOCworkbench')
        self.non_existent_coveralls = CoverallsHelper('jlmdegoede', 'NON_EXISTENT_REPOSITORY')

    def test_init(self):
        """Test if Coveralls was successfully initialized"""
        self.assertIsNotNone(self.coveralls)

    def test_code_coverage_data(self):
        """Test if general coverage data can be retrieved from the CoverallsHelper"""
        self.assertIsInstance(self.coveralls.code_coverage_data(), float)

    def test_code_coverage_data_non_existent(self):
        """Test to retrieve coverage data from non-existing repository"""
        self.assertIsNone(self.non_existent_coveralls.code_coverage_data())

    def test_coverage_enabled_check(self):
        """Test to retrieve enabled status for repository"""
        self.assertTrue(self.coveralls.coverage_enabled_check())

    def test_coverage_enabled_check_not_enabled(self):
        """Test to retrieve enabled status for non-existent repository"""
        self.assertFalse(self.non_existent_coveralls.coverage_enabled_check())

    def test_get_badge_url(self):
        """Test retrieving the badge URL from Coveralls"""
        badge_url = self.coveralls.get_badge_url()
        val = URLValidator()
        val(badge_url)

    def test_get_badge_url_invalid(self):
        """Test retrieving the badge URL from non-existent repository"""
        badge_url = self.non_existent_coveralls.get_badge_url()
        val = URLValidator()
        self.assertRaises(ValidationError, val, badge_url)
