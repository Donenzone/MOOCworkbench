"""Build_manager test modules for helper modules"""
import os
from django.test import TestCase

from ..travis_ci_helper import TravisCiHelper


class TravisCiHelperTestCases(TestCase):
    """Tests for views.py in build_manager app"""
    def setUp(self):
        socialtoken = os.environ.get('GITHUB_TOKEN')
        self.github_helper = GitHubHelperReplacement(socialtoken, 'Workbench-Python-Experiment')
        self.travis_ci_helper = TravisCiHelper(self.github_helper)

    def test_enable_travis(self):  # pylint: disable=unused-argument
        self.assertTrue(self.travis_ci_helper.enable_travis_for_repository())

    def test_disable_travis(self):
        self.assertTrue(self.travis_ci_helper.disable_travis_for_repository())

    def test_trigger_build(self):
        self.assertTrue(self.travis_ci_helper.trigger_build_for_repo())

    def test_get_last_log(self):
        log = self.travis_ci_helper.get_log_for_last_build()
        self.assertNotEqual(log, 'Log not found')


class GitHubHelperReplacement(object):
    def __init__(self, socialtoken, repository_name):
        self.socialtoken = socialtoken
        self.github_repository = GitHubHelperRepository(repository_name)


class GitHubHelperRepository(object):
    def __init__(self, repository_name):
        self.name = repository_name
