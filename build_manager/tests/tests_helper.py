"""Build_manager test modules for helper modules"""
import os
from django.test import TestCase

from ..travis_ci_helper import TravisCiHelper


class TravisCiHelperTestCases(TestCase):
    """Tests for the TravisCiHelper in the build_manager app
    Make sure that the env contains a valid GITHUB_TOKEN for a GitHub repository"""
    def setUp(self):
        socialtoken = os.environ.get('GITHUB_TOKEN')
        self.github_helper = GitHubHelperReplacement(socialtoken, 'Workbench-Python-Experiment')
        self.travis_ci_helper = TravisCiHelper(self.github_helper)

    def test_enable_travis(self):  # pylint: disable=unused-argument
        """Test if Travis CI can be enabled for repository"""
        self.assertTrue(self.travis_ci_helper.enable_travis_for_repository())

    def test_disable_travis(self):
        """Test if Travis CI can be disabled for repository"""
        self.assertTrue(self.travis_ci_helper.disable_travis_for_repository())

    def test_trigger_build(self):
        """Test if Travis CI build can be triggered for repository"""
        self.assertTrue(self.travis_ci_helper.trigger_build_for_repo())

    def test_get_last_log(self):
        """Test if last log can be retrieved for repository"""
        log = self.travis_ci_helper.get_log_for_last_build()
        self.assertNotEqual(log, 'Log not found')


class GitHubHelperReplacement(object):
    def __init__(self, socialtoken, repository_name):
        self.socialtoken = socialtoken
        self.github_repository = GitHubHelperRepository(repository_name)


class GitHubHelperRepository(object):
    def __init__(self, repository_name):
        self.name = repository_name
