import os
from unittest.mock import patch

from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.management import call_command

from experiments_manager.models import Experiment
from git_manager.helpers.github_helper import GitHubHelper
from ..tasks import task_create_package_from_experiment, \
    task_create_package, task_publish_update_package
from ..models import InternalPackage
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser


class MarketplaceTasksTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        random_string = get_random_string(5)
        self.package_name = 'package{0}'.format(random_string)
        self.internal_package = InternalPackage.objects.create(name=self.package_name,
                                                               description='Package',
                                                               language_id=2,
                                                               category_id=1,
                                                               owner_id=1,
                                                               template_id=1)

        self.git_repo = GitRepository.objects.create(name='Workbench-Acceptence-Experiment',
                                                     owner=self.workbench_user,
                                                     github_url='https://github.com/jlmdegoede/Workbench-Acceptence-Experiment.git')

        self.experiment = Experiment.objects.create(title='Workbench-Acceptence-Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=2,
                                                    template_id=2)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_empty_package(self, mock_social_token):
        """Test if an empty package can be initialized"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        task_create_package(self.internal_package.pk)
        self.internal_package.refresh_from_db()
        self.assertIsNotNone(self.internal_package)
        github_helper = GitHubHelper('test', self.package_name)
        self.assertTrue(github_helper.view_file('requirements.txt'))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_existing_package(self, mock_social_token):
        """Test if an existing package can be added"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        task_create_package(self.internal_package.pk)
        self.internal_package.refresh_from_db()
        self.internal_package.delete()

        new_internal_package = InternalPackage.objects.create(name=self.package_name,
                                                              description='Package',
                                                              language_id=2,
                                                              category_id=1,
                                                              owner_id=1,
                                                              template_id=1)

        task_create_package(new_internal_package.pk)
        new_internal_package.refresh_from_db()
        self.assertIsNotNone(new_internal_package)
        github_helper = GitHubHelper('test', self.package_name)
        self.assertTrue(github_helper.view_file('requirements.txt'))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_create_package_from_experiment(self, mock_social_token):
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        task_create_package_from_experiment(self.internal_package.pk,
                                            self.experiment.pk,
                                            '/src/data/')

        self.assertIsNotNone(self.internal_package)
        github_helper = GitHubHelper('test', self.package_name)
        self.assertTrue(github_helper.view_file('requirements.txt'))
        self.assertTrue(github_helper.view_file('{0}/make_dataset.py'.format(self.package_name)))

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_task_publish_package(self, mock_social_token):
        self.test_create_empty_package()
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        task_publish_update_package(self.internal_package.pk)
        path = os.path.exists('packages/{0}/dist/{0}-0.0.1.tar.gz'.format(self.package_name))
        self.assertTrue(path)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def tearDown(self, mock_social_token):
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        github_helper = GitHubHelper('test', self.package_name)
        github_helper._delete_repository()
