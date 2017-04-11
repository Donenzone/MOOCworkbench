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

# Create your tests here.
class build_managerTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)
        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', version='1.0', owner=self.workbench_user, git_repo=self.git_repo)
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
