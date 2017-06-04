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


class MarketplaceTasksTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.cookiecutter = CookieCutterTemplate.objects.get(language_id=2, meant_for='e')

        random_string = get_random_string(5)
        self.experiment_name = 'experiment_{0}'.format(random_string)

        self.experiment = Experiment.objects.create(title=self.experiment_name,
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    language_id=2,
                                                    template_id=2)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_new_experiment(self, mock_social_token):
        """Test if an empty package can be initialized"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        initialize_repository(self.experiment.pk, self.cookiecutter.pk)
        self.experiment.refresh_from_db()
        self.assertIsNotNone(self.experiment)
        github_helper = GitHubHelper('test', self.experiment_name)
        self.assertTrue(github_helper.view_file('requirements.txt'))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def tearDown(self, mock_social_token):
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper('test', self.experiment_name)
        github_helper._delete_repository()
