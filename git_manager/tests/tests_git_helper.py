import os
import shutil
from unittest.mock import patch


from django.contrib.auth.models import User
from django.test import TestCase

from ..helpers.git_helper import GitHelper, clean_up_after_git_helper
from ..helpers.github_helper import GitHubHelper


class GitHelperTestCase(TestCase):

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def setUp(self, mock_social_token):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = self.github_token
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.github_helper = GitHubHelper(self.user, 'Workbench-Acceptance-Experiment')
        self.git_helper = GitHelper(self.github_helper)

    @patch('git_manager.helpers.github_helper.GitHubHelper.get_clone_url')
    def test_git_helper_repo_dir_and_clone(self, mock_clone_url):
        """Test to clone a repository"""
        mock_clone_url.return_value = "https://{0}@github.com/MOOCworkbench/{1}".format(self.github_token,
                                                                                        'Workbench-Acceptance-Experiment')
        self.git_helper.clone_or_pull_repository()
        self.assertTrue(os.path.exists(self.git_helper.repo_dir))
        shutil.rmtree(self.git_helper.repo_dir)

    def test_repo_dir_of_user(self):
        """Test if the right repo_dir of user is returned"""
        self.git_helper.clone_or_pull_repository()
        self.assertTrue(os.path.exists(self.git_helper.repo_dir_of_user()))
        self.assertTrue('jlmdegoede' in self.git_helper.repo_dir_of_user())

    @patch('git_manager.helpers.github_helper.GitHubHelper.get_clone_url')
    def test_clean_up_after_git_helper(self, mock_clone_url):
        """Test if clean-up removes the correct repository folder"""
        mock_clone_url.return_value = "https://{0}@github.com/MOOCworkbench/{1}".format(self.github_token,
                                                                                        'Workbench-Acceptance-Experiment')
        self.git_helper.clone_or_pull_repository()
        self.assertTrue(os.path.exists(self.git_helper.repo_dir))
        repo_dir = self.git_helper.repo_dir
        clean_up_after_git_helper(self.git_helper)
        self.assertFalse(os.path.exists(repo_dir))

    def test_pull_repository(self):
        """Test to pull in an existing repository"""
        self.git_helper.clone_or_pull_repository()
        self.assertTrue(os.path.exists(self.git_helper.repo_dir))
        self.git_helper.pull()

    @patch('git_manager.helpers.github_helper.GitHubHelper.get_clone_url')
    def test_commit(self, mock_clone_url):
        """Test to pull in an existing repository"""
        mock_clone_url.return_value = "https://{0}@github.com/MOOCworkbench/{1}".format(self.github_token,
                                                                                        'Workbench-Acceptance-Experiment')
        self.git_helper.clone_or_pull_repository()
        self.git_helper.commit("New commit")

    def test_push(self):
        """Test to pull in an existing repository"""
        self.git_helper.clone_or_pull_repository()
        self.git_helper.commit("New commit")
        self.git_helper.push()

    @patch('git_manager.helpers.github_helper.GitHubHelper.get_clone_url')
    def test_filter_and_checkout_subfolder(self, mock_clone_url):
        """Test to filter a directory and checkout the subfolder
        The repository contains the file make_dataset.py in the folder /src/data,
        that should now be at top level of this repository"""
        mock_clone_url.return_value = "https://{0}@github.com/MOOCworkbench/{1}".format(self.github_token,
                                                                                        'Workbench-Acceptance-Experiment')
        self.git_helper.clone_or_pull_repository()
        self.git_helper.filter_and_checkout_subfolder('/src/data')
        self.assertTrue(os.path.exists(self.git_helper.repo_dir))
        onlyfiles = [f for f in os.listdir(self.git_helper.repo_dir)
                     if os.path.isfile(os.path.join(self.git_helper.repo_dir, f))]
        self.assertTrue('make_dataset.py' in onlyfiles)

    @patch('git_manager.helpers.github_helper.GitHubHelper.get_clone_url')
    def test_move_repo_contents_to_folder(self, mock_clone_url):
        """Test to move the repo contents into a new folder"""
        mock_clone_url.return_value = "https://{0}@github.com/MOOCworkbench/{1}".format(self.github_token,
                                                                                        'Workbench-Acceptance-Experiment')
        self.git_helper.clone_or_pull_repository()
        self.git_helper.move_repo_contents_to_folder('my_new_awesome_folder')
        onlyfiles = [f for f in os.listdir(self.git_helper.repo_dir)
                     if os.path.isfile(os.path.join(self.git_helper.repo_dir, f))]
        self.assertFalse(onlyfiles)

    def tearDown(self):
        if os.path.exists(self.git_helper.repo_dir):
            shutil.rmtree(self.git_helper.repo_dir)
            shutil.rmtree(self.git_helper.repo_dir_of_user())
