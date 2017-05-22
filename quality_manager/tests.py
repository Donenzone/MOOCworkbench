import json
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from dataschema_manager.models import DataSchema
from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment, ChosenExperimentSteps
from git_manager.models import GitRepository


class QualityManagerTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

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
                                                    template_id=2,
                                                    schema=schema)
        self.chosen_experiment_step = ChosenExperimentSteps.objects.create(step_id=1,
                                                experiment=self.experiment,
                                                                      step_nr=1,
                                                                      active=True,
                                                                      location='/src/main/')

        self.client = Client()
        self.client.login(username='test', password='test')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['messages'])

    @patch('quality_manager.views.DashboardView._get_recent_measurements_for_all_types')
    def test_dashboard_view_with_messages(self, mock_messages):
        mock_messages.return_value = [MeasurementMockClass(), MeasurementMockClass(), MeasurementMockClass()]
        response = self.client.get(reverse('dashboard', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['dashboard_messages'])
        self.assertIsNotNone(response.context['dashboard_messages']['test_slug'])

    def test_vcs_overview(self):
        response = self.client.get(reverse('vcs_overview', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)

    @patch('quality_manager.views.get_recent_measurements_for_type')
    def test_nr_of_commits_view(self, mock_recent_measurements):
        mock_recent_measurements.return_value = [MeasurementMockClass(), MeasurementMockClass(), MeasurementMockClass()]
        response = self.client.get(reverse('nr_of_commits', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(json_response['values'], ['5', '5', '5'])

    @patch('quality_manager.views.task_version_control_quality_check')
    @patch('quality_manager.views.task_test_quality_check')
    @patch('quality_manager.views.task_requirements_quality_check')
    @patch('quality_manager.views.task_ci_quality_check')
    @patch('quality_manager.views.task_docs_coverage_check')
    def test_refresh_measurements(self, mock_vcs, mock_test, mock_req, mock_ci, mock_docs):
        response = self.client.get(reverse('measurements_refresh', kwargs={'step_id': self.chosen_experiment_step.id}))
        self.assertEqual(response.status_code, 200)


class MeasurementMockClass(object):
    def __init__(self):
        self.measurement = MeasurementMessageMockClass()
        self.created = datetime.now()
        self.raw_values = MeasurementRawValue()

    def get_message(self):
        return 'Get to work fool!'

    def slug(self):
        return 'test_slug'


class MeasurementMessageMockClass(object):
    def __init__(self):
        self.name = 'My First Measurement'


class MeasurementRawValue(object):
    def all(self):
        return [RawValue()]


class RawValue(object):
    def __init__(self):
        self.value = '5'
