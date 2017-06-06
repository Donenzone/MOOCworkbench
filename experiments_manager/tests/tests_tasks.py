import os
from unittest.mock import patch

from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.management import call_command

from git_manager.helpers.github_helper import GitHubHelper
from cookiecutter_manager.models import CookieCutterTemplate
from ..tasks import initialize_repository
from ..models import Experiment
from user_manager.models import WorkbenchUser


class ExperimentTasksTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.python_cookiecutter = CookieCutterTemplate.objects.get(language_id=2, meant_for='e')
        self.r_cookiecutter = CookieCutterTemplate.objects.get(language_id=3, meant_for='e')

        random_string = get_random_string(5)
        self.python_experiment_name = 'python_experiment_{0}'.format(random_string)
        self.r_experiment_name = 'r_experiment_{0}'.format(random_string)

        self.python_experiment = Experiment.objects.create(title=self.python_experiment_name,
                                                           description='test',
                                                           owner=self.workbench_user,
                                                           language_id=2,
                                                           template_id=2)

        self.r_experiment = Experiment.objects.create(title=self.r_experiment_name,
                                                      description='test',
                                                      owner=self.workbench_user,
                                                      language_id=3,
                                                      template_id=3)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_new_python_experiment(self, mock_social_token):
        """Test if a Python experiment can be initialized"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        initialize_repository(self.python_experiment.pk, self.python_cookiecutter.pk)
        self.python_experiment.refresh_from_db()
        self.assertIsNotNone(self.python_experiment)
        github_helper = GitHubHelper('test', self.python_experiment_name)
        self.assertTrue(github_helper.view_file('requirements.txt'))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_new_r_experiment(self, mock_social_token):
        """Test if an R experiment can be initialized"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        initialize_repository(self.r_experiment.pk, self.r_cookiecutter.pk)
        self.r_experiment.refresh_from_db()
        self.assertIsNotNone(self.r_experiment)
        github_helper = GitHubHelper('test', self.r_experiment_name)
        self.assertTrue(github_helper.view_file('README.md'))
        self.assertTrue(github_helper.view_file('src/.gitignore'))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def tearDown(self, mock_social_token):
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        try:
            github_helper = GitHubHelper('test', self.python_experiment_name)
            github_helper._delete_repository()
        except Exception:
            pass

        try:
            github_helper = GitHubHelper('test', self.r_experiment_name)
            github_helper._delete_repository()
        except Exception:
            pass
