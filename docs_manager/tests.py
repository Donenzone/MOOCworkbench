from unittest.mock import patch
from collections import namedtuple
import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from helpers.helper import ExperimentPackageTypeMixin


class DocsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', owner=self.workbench_user, git_repo=self.git_repo)

        self.client = Client()
        self.client.login(username='test', password='test')
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

    @patch('docs_manager.views.GitHubHelper')
    @patch('docs_manager.views.SphinxHelper')
    def test_doc_experiment_view(self, mock_gh_helper, mock_sphinx_helper):
        response = self.client.get(reverse('docs_view', kwargs={'object_id': 1, 'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        mock_gh_helper = None
        mock_sphinx_helper = None
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['document'])

    @patch('docs_manager.views.GitHubHelper')
    @patch('docs_manager.views.SphinxHelper')
    def test_doc_experiment_view_with_page_slug(self, mock_gh_helper, mock_sphinx_helper):
        response = self.client.get(reverse('docs_view', kwargs={'object_id': 1,
                                                                'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE,
                                                                'page_slug': 'test'}))
        mock_gh_helper = None
        mock_sphinx_helper = None
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['document'])