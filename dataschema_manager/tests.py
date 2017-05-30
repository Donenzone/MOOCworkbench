import json

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser

from .models import DataSchema, DataSchemaField


class DataSchemaManagerTestCase(TestCase):
    """Test cases for the DataSchema Manager views"""
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user,
                                                     github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=1,
                                                    template_id=1)
        self.first_field = DataSchemaField.objects.create(name='test', datatype='string')
        self.experiment.schema.fields.add(self.first_field)
        self.experiment.schema.save()

        self.client = Client()
        self.client.login(username='test', password='test')

    def test_dataschema_overview(self):
        """Test if dataschema overview loads successfully"""
        response = self.client.get(reverse('experiment_schema', kwargs={'experiment_id': self.experiment.pk}))
        self.assertTrue(response.status_code, 200)

    def test_dataschema_overview_firstfield(self):
        """Test if dataschema overview contains the correct field"""
        response = self.client.get(reverse('experiment_schema', kwargs={'experiment_id': self.experiment.pk}))
        self.assertTrue(self.first_field in response.context['data_schema_list'])

