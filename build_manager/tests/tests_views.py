"""Build_manager test modules for views.py"""
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from build_manager.models import TravisInstance
from dataschema_manager.models import DataSchema
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser


class BuildManagerViewsTestCases(TestCase):
    """Tests for views.py in build_manager app"""
    def setUp(self):
        """Prepare for running tests:
        Load data from fixtures
        Create a new user
        Create a second user
        Create a git repo, data schema and experiment
        Sign in the user"""
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user,
                                                     github_url='https://github')
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

    @patch('build_manager.views.enable_travis')
    def test_enable_ci_builds(self, mock_enable_travis):  # pylint: disable=unused-argument
        """Test enable CI build for experiment"""
        data = {'object_id': self.experiment.id, 'object_type': self.experiment.get_object_type()}

        response = self.client.post(reverse('enable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        travis = TravisInstance.objects.filter(experiment=self.experiment)

        self.assertTrue(response_json['enabled'])
        self.assertEqual(travis.count(), 1)

    def test_enable_ci_builds_missing_id(self):
        """Test enable CI build for experiment without object_id and object_type"""
        args = [reverse('enable_ci_builds')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_disable_ci_builds(self, mock_get_github, mock_travis_ci):  # pylint: disable=unused-argument
        """Test to disable CI builds, after having them enabled"""
        self.test_enable_ci_builds()

        data = {'object_id': self.experiment.id, 'object_type': self.experiment.get_object_type()}
        response = self.client.post(reverse('disable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        travis = TravisInstance.objects.get(experiment=self.experiment)

        self.assertTrue(response_json['disabled'])
        self.assertFalse(travis.enabled)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_disable_ci_builds_never_enabled(self, mock_get_github, mock_travis_ci):  # pylint: disable=unused-argument
        """Test to disable CI builds, when builds are never enabled"""
        data = {'object_id': self.experiment.id, 'object_type': self.experiment.get_object_type()}
        response = self.client.post(reverse('disable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['disabled'])

    def test_disable_ci_builds_missing_id(self):
        """Test to disable CI builds when object_id and object_type are missing"""
        args = [reverse('disable_ci_builds')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_build_experiment_now(self, mock_get_github, mock_travis_ci):  # pylint: disable=unused-argument
        """Test to force the start of a build now"""
        self.test_enable_ci_builds()
        data = {'object_id': self.experiment.id, 'object_type': self.experiment.get_object_type()}
        response = self.client.post(reverse('build_experiment_now'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['build_started'])

    def test_build_experiment_now_missing_id(self):
        """Test to force the start of a build now, with missing object_id and object_type"""
        args = [reverse('build_experiment_now')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    def test_build_status(self, mock_get_github):  # pylint: disable=unused-argument
        """Test to get the last status of a CI build"""
        self.test_enable_ci_builds()
        response = self.client.get(
            reverse('build_status', kwargs={'object_id': 1,
                                            'object_type': self.experiment.get_object_type()}))
        travis = TravisInstance.objects.get(experiment=self.experiment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_config'], travis)

    @patch('build_manager.views.get_github_helper')
    def test_build_status_disabled(self, mock_get_github):  # pylint: disable=unused-argument
        """Test to get the last status of a CI build when CI builds are disabled"""
        self.test_enable_ci_builds()
        self.test_disable_ci_builds()
        response = self.client.get(
            reverse('build_status', kwargs={'object_id': 1,
                                            'object_type': self.experiment.get_object_type()}))
        self.assertEqual(response.status_code, 200)
        travis = TravisInstance.objects.get(experiment=self.experiment)
        self.assertEqual(response.context['current_config'], travis)
        self.assertFalse(response.context['configured'])
