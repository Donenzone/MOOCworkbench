from django.test import TestCase
from unittest.mock import patch
from user_manager.models import WorkbenchUser
from django.contrib.auth.models import User
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from django.test import Client
from django.core.management import call_command
from django.shortcuts import reverse
import json
from build_manager.models import TravisInstance


class BuildManagerTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', owner=self.workbench_user, git_repo=self.git_repo)
        self.client = Client()
        self.client.login(username='test', password='test')
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)

    @patch('build_manager.views.enable_travis')
    def test_enable_ci_builds(self, mock_enable_travis):
        data = {'experiment_id': self.experiment.id}
        response = self.client.post(reverse('enable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['enabled'])
        travis = TravisInstance.objects.filter(experiment=self.experiment)
        self.assertEqual(travis.count(), 1)

    def test_enable_ci_builds_missing_id(self):
        args = [reverse('enable_ci_builds')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_disable_ci_builds(self, mock_get_github, mock_travis_ci):
        self.test_enable_ci_builds()
        data = {'experiment_id': self.experiment.id}
        response = self.client.post(reverse('disable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['disabled'])
        travis = TravisInstance.objects.get(experiment=self.experiment)
        self.assertFalse(travis.enabled)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_disable_ci_builds_never_enabled(self, mock_get_github, mock_travis_ci):
        data = {'experiment_id': self.experiment.id}
        response = self.client.post(reverse('disable_ci_builds'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['travis_does_not_exist'])

    def test_disable_ci_builds_missing_id(self):
        args = [reverse('disable_ci_builds')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    @patch('build_manager.views.TravisCiHelper')
    def test_build_experiment_now(self, mock_get_github, mock_travis_ci):
        self.test_enable_ci_builds()
        data = {'experiment_id': self.experiment.id}
        response = self.client.post(reverse('build_experiment_now'), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertTrue(response_json['build_started'])

    def test_build_experiment_now_missing_id(self):
        args = [reverse('build_experiment_now')]
        self.assertRaises(AssertionError, self.client.get, *args)

    @patch('build_manager.views.get_github_helper')
    def test_build_status(self, mock_get_github):
        self.test_enable_ci_builds()
        response = self.client.get(reverse('build_status', kwargs={'experiment_id': 1}))
        self.assertEqual(response.status_code, 200)
        travis = TravisInstance.objects.get(experiment=self.experiment)
        self.assertEqual(response.context['current_config'], travis)

    @patch('build_manager.views.get_github_helper')
    def test_build_status_disabled(self, mock_get_github):
        self.test_enable_ci_builds()
        self.test_disable_ci_builds()
        response = self.client.get(reverse('build_status', kwargs={'experiment_id': 1}))
        self.assertEqual(response.status_code, 200)
        travis = TravisInstance.objects.get(experiment=self.experiment)
        self.assertEqual(response.context['current_config'], travis)
        self.assertFalse(response.context['configured'])

    def test_build_status_non_existent(self):
        response = self.client.get(reverse('build_status', kwargs={'experiment_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['configured'])