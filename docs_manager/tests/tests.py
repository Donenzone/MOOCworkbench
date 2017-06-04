from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from dataschema_manager.models import DataSchema
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from helpers.helper import ExperimentPackageTypeMixin
from user_manager.models import WorkbenchUser


class DocsManagerTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        schema = DataSchema(name='main')
        schema.save()
        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=2,
                                                    template_id=2,
                                                    schema=schema)

        self.client = Client()
        self.client.login(username='test', password='test')

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    @patch('git_manager.helpers.language_helper.SphinxHelper')
    def test_doc_experiment_view(self, mock_gh_helper, mock_sphinx_helper):
        """
        Test if the DocExperimentView loads, for the default documentation view.
        :param mock_gh_helper: Autoloaded by the mock framework
        :param mock_sphinx_helper: Autoloaded by the mock framework
        :return: 
        """
        response = self.client.get(reverse('docs_view', kwargs={'object_id': 1,
                                                                'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 302)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    @patch('git_manager.helpers.language_helper.SphinxHelper')
    def test_doc_experiment_view_with_page_slug(self, mock_gh_helper, mock_sphinx_helper):
        """
        Test if the DocExperimentView loads, given a pageslug to load.
        :param mock_gh_helper: Autoloaded by the mock framework
        :param mock_sphinx_helper:  Autoloaded by the mock framework
        :return: 
        """
        response = self.client.get(reverse('docs_view', kwargs={'object_id': 1,
                                                                'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE,
                                                                'page_slug': 'test'}))
        self.assertEqual(response.status_code, 302)

    def test_doc_status_view(self):
        """
        Test if the doc status view loads successfully.
        :return: 
        """
        response = self.client.get(reverse('docs_status', kwargs={'object_id': 1,
                                                                  'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.context['object'], self.experiment)
        self.assertEqual(response.context['docs'], self.experiment.docs)

    def test_toggle_doc_status_true_to_false(self):
        """
        Test if the documentation status is toggled from True to False.
        :return: 
        """
        docs = self.experiment.docs
        docs.enabled = True
        docs.save()

        response = self.client.get(reverse('toggle_docs_status', kwargs={'object_id': 1,
                                                                  'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 302)
        docs.refresh_from_db()
        self.assertFalse(docs.enabled)

    @patch('docs_manager.views.GitHubHelper')
    @patch('docs_manager.views.GitHelper')
    def test_toggle_doc_status_false_to_true(self, mock_gh_helper, mock_git_helper):
        """
        Test if the documentation status is toggled from True to False.
        :return: 
        """
        docs = self.experiment.docs
        docs.enabled = False
        docs.save()

        response = self.client.get(reverse('toggle_docs_status', kwargs={'object_id': 1,
                                                                  'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 302)
        docs.refresh_from_db()
        self.assertTrue(docs.enabled)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    @patch('docs_manager.views.GitHelper')
    @patch('git_manager.helpers.language_helper.SphinxHelper')
    def test_docs_generate_enabled(self, mock_gh_helper, mock_git_helper, mock_sphinx_helper):
        """
        Test if the documentation view can be loaded.
        :return: 
        """
        response = self.client.get(reverse('docs_generate', kwargs={'object_id': 1,
                                                                  'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 200)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    @patch('docs_manager.views.GitHelper')
    @patch('git_manager.helpers.language_helper.SphinxHelper')
    def test_docs_generate_disabled(self, mock_gh_helper, mock_git_helper, mock_sphinx_helper):
        """
        Test if the documentation view can be loaded.
        :return: 
        """
        docs = self.experiment.docs
        docs.enabled = False
        docs.save()

        response = self.client.get(reverse('docs_generate', kwargs={'object_id': 1,
                                                                  'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 200)
