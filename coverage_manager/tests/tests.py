import json
from collections import namedtuple
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from coverage_manager.models import CodeCoverage
from dataschema_manager.models import DataSchema
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from helpers.helper import ExperimentPackageTypeMixin
from user_manager.models import WorkbenchUser


class CoverageManagerTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)
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
                                                    language_id=1,
                                                    template_id=1,
                                                    schema=schema)

        self.client = Client()
        self.client.login(username='test', password='test')

    def enable_travis_for_experiment(self):
        enable_travis = self.experiment.travis
        enable_travis.enabled = True
        enable_travis.save()
        return enable_travis

    def test_enable_coverage_without_travis(self):
        """
        Try to enable code coverage without having an enabled travis instance.
        :return: 
        """
        coverage_data = {'object_id': 1}
        response = self.client.post(reverse('coveralls_enable'), data=coverage_data)
        json_response = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_response['enabled'])

    @patch('coverage_manager.views.get_github_helper')
    @patch('coverage_manager.views.CoverallsHelper.coverage_enabled_check')
    def test_enable_coverage_with_travis_true_coverage_enabled(self, mock_coverage_check, mock_github_helper):
        """
        Test if code coverage can be enabled when Travis builds are enabled
        and when CoverallsHelper checks for enabled and returns True
        :return: 
        """
        travis_instance = self.enable_travis_for_experiment()

        mock_coverage_check.return_value = True
        mock_github_helper.return_value = get_mock_github_owner_and_repo_name()

        coverage_data = {'object_id': 1}
        response = self.client.post(reverse('coveralls_enable'), data=coverage_data)
        self.assertEqual(response.status_code, 200)
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertTrue(code_coverage.enabled)

    @patch('coverage_manager.views.get_github_helper')
    @patch('coverage_manager.views.CoverallsHelper.coverage_enabled_check')
    def test_enable_coverage_with_travis_false_coverage_enabled(self, mock_coverage_check, mock_github_helper):
        """
        Test if code coverage can be enabled when Travis builds are enabled
        and when CoverallsHelper checks for enabled and returns False
        :return: 
        """
        travis_instance = self.enable_travis_for_experiment()

        mock_coverage_check.return_value = False
        mock_github_helper.return_value = get_mock_github_owner_and_repo_name()

        coverage_data = {'object_id': 1}
        response = self.client.post(reverse('coveralls_enable'), data=coverage_data)
        self.assertEqual(response.status_code, 200)
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertTrue(code_coverage.enabled)

    @patch('coverage_manager.views.get_github_helper')
    @patch('coverage_manager.views.CoverallsHelper.coverage_enabled_check')
    def test_enable_coverage_with_travis_true_existing_config(self, mock_coverage_check, mock_github_helper):
        """
        Test if code coverage can be enabled when Travis builds are enabled
        with existing CodeCoverage instance
        :return: 
        """
        self.enable_travis_for_experiment()
        code_coverage = CodeCoverage.objects.get(id=1)

        mock_coverage_check.return_value = True
        mock_github_helper.return_value = get_mock_github_owner_and_repo_name()

        coverage_data = {'object_id': 1}
        response = self.client.post(reverse('coveralls_enable'), data=coverage_data)
        self.assertEqual(response.status_code, 200)
        code_coverage.refresh_from_db()
        self.assertTrue(code_coverage.enabled)

    @patch('coverage_manager.views.get_github_helper')
    @patch('coverage_manager.views.CoverallsHelper.coverage_enabled_check')
    @patch('coverage_manager.views.CoverallsHelper.get_badge_url')
    def test_enable_coverage_with_travis_badge(self, mock_get_badge, mock_coverage_check, mock_github_helper):
        """
        Test if code coverage can be enabled when Travis builds are enabled
        :return: 
        """
        travis_instance = self.enable_travis_for_experiment()

        mock_get_badge.return_value = 'http://test.test'
        mock_coverage_check.return_value = True
        mock_github_helper.return_value = get_mock_github_owner_and_repo_name()

        coverage_data = {'object_id': 1}
        self.client.post(reverse('coveralls_enable'), data=coverage_data)
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertTrue(code_coverage.enabled)

    def test_disable_coverage(self):
        """
        Test if disabling code coverage works, by first enabling
        code coverage and then calling the view to disable it
        :return: 
        """
        travis_instance = self.enable_travis_for_experiment()
        self.test_enable_coverage_with_travis_true_coverage_enabled()
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertTrue(code_coverage.enabled)

        coverage_data = {'object_id': 1}
        self.client.post(reverse('coveralls_disable'), data=coverage_data)
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertFalse(code_coverage.enabled)

    def test_disable_coverage_never_enabled(self):
        """
        Test to disable code coverage, when it was never enabled.
        :return: 
        """
        self.enable_travis_for_experiment()
        coverage_data = {'object_id': 1}
        response = self.client.post(reverse('coveralls_disable'), data=coverage_data)
        json_response = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(json_response['disabled'])

    def test_coveralls_status(self):
        response = self.client.get(reverse('coveralls_status', kwargs={'object_id': 1,
                                                                       'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['travis'])
        self.assertFalse(response.context['coverage_configured'])

    def test_coveralls_status_enabled(self):
        travis_instance = self.enable_travis_for_experiment()
        self.test_enable_coverage_with_travis_true_coverage_enabled()

        response = self.client.get(reverse('coveralls_status', kwargs={'object_id': 1,
                                                                       'object_type': ExperimentPackageTypeMixin.EXPERIMENT_TYPE}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['travis'])
        self.assertTrue(response.context['coverage_configured'])
        code_coverage = CodeCoverage.objects.get(travis_instance=travis_instance)
        self.assertEqual(response.context['current_config'], code_coverage)


def get_mock_github_owner_and_repo_name():
    Foo = namedtuple('Foo', ['owner', 'repo_name'])
    return Foo(owner='test', repo_name='test')
