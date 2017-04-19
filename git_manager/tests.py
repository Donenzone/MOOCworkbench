import base64

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from unittest.mock import patch

from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from git_manager.helpers.github_helper import GitHubHelper
from user_manager.models import WorkbenchUser


class GitManagerTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', owner=self.workbench_user, git_repo=self.git_repo)
        self.client = Client()
        self.client.login(username='test', password='test')
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)

        if self._testMethodName is not 'test_init_github_helper_no_socialtoken':
            self.set_up_social()

    def set_up_social(self):
        self.social_app = SocialApp(provider='GitHub', name='GitHub', client_id='B', secret='A')
        self.social_app.save()

        self.social_account = SocialAccount(user=self.user, provider='github', uid='A')
        self.social_account.save()

        self.social_token = SocialToken(app=self.social_app, account=self.social_account, token='A', token_secret='B')
        self.social_token.save()

    def test_init_github_helper_no_socialtoken(self):
        github_helper = GitHubHelper
        args = [self.user, 'test']
        self.assertRaises(ValueError, github_helper, *args)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_init_github_helper(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_init_github_helper_create(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test', create=True)
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.github_repository.repo_name, 'newly_created_repo')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_github_owner(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.owner, 'test')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_init_github_helper(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.get_clone_url(), 'https://A@clone-url')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_github_list_folder(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.list_files_in_repo('test1'), GithubMockRepo.TEST1_LIST)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_github_list_folder_with_slash(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.list_files_in_repo('/test1'), GithubMockRepo.TEST1_LIST)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_github_list_folder_empty(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)
        self.assertEqual(github_helper.list_files_in_repo(), GithubMockRepo.TEST2_LIST)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_github_object')
    def test_view_file_in_repo(self, mock_github):
        mock_github.return_value = GithubMock()
        github_helper = GitHubHelper(self.user, 'test')
        self.assertIsNotNone(github_helper)


class GithubMock(object):
    def get_user(self):
        return GithubMockUser('test')


class GithubMockUser(object):

    def __init__(self, owner):
        self.owner = GithubMockRepo('repo', owner)

    def get_repo(self, repo_name):
        return self.owner

    def get_commits(self):
        return []

    def create_repo(self, repo_name):
        return GithubMockRepo('newly_created_repo', 'test')


class GithubMockRepo(object):
    TEST1_LIST = ['A', 'B', 'C']
    TEST2_LIST = ['X', 'Y', 'Z']

    def __init__(self, repo_name, owner):
        self.repo_name = repo_name
        self.owner = GithubMockOwner(owner)
        self.clone_url = 'https://clone-url'

    def get_contents(self, folder):
        if folder == '/test1':
            return self.TEST1_LIST
        return self.TEST2_LIST

    def get_file_contents(self, file_name):
        encoded = base64.b64decode('Test File')
        return encoded


class GithubMockOwner(object):
    def __init__(self, login):
        self.login = login
