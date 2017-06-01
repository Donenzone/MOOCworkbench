import os
from unittest.mock import patch

from github.GithubException import GithubException

from django.contrib.auth.models import User
from django.test import TestCase

from ..helpers.github_helper import GitHubHelper
from ..helpers.git_helper import GitHelper


class GitHubHelperTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_github_helper_owner(self, mock_social_token):
        """Test if the correct owner is returned by the GitHub helper"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper(self.user, 'Workbench-Acceptence-Experiment')
        self.assertTrue(github_helper.owner == 'jlmdegoede')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_github_helper_create_with_existing(self, mock_social_token):
        """Test creating a repository that already exists"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        args = [self.user, 'Workbench-Acceptence-Experiment', True]
        self.assertRaises(GithubException, GitHubHelper, *args)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_clone_with_github(self, mock_social_token):
        """Test cloning a repository with the GitHubHelper"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper(self.user, 'Workbench-Acceptence-Experiment')
        git_helper = GitHelper(github_helper)
        git_helper.clone_or_pull_repository()
        self.assertTrue(os.path.exists(git_helper.repo_dir))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_view_files_in_dir(self, mock_social_token):
        """Test viewing files in a repo"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper(self.user, 'Workbench-Acceptence-Experiment')
        content_files = github_helper.list_files_in_folder()
        self.assertIsNotNone(content_files)
        file_names = [x.name for x in content_files]
        self.assertTrue('requirements.txt' in file_names)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_view_files_in_dir_src_data(self, mock_social_token):
        """Test viewing files in a directory of repo"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper(self.user, 'Workbench-Acceptence-Experiment')
        content_files = github_helper.list_files_in_folder('/src/data')
        self.assertIsNotNone(content_files)
        file_names = [x.name for x in content_files]
        self.assertTrue('make_dataset.py' in file_names)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_view_files_in_non_existent_dir(self, mock_social_token):
        """Test viewing files in a directory of repo"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper(self.user, 'Workbench-Acceptence-Experiment')
        content_files = github_helper.list_files_in_folder('/src/IDONOTEXIST')
        self.assertIsNotNone(content_files)



