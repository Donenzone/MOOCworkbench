from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser

from .models import DataSchemaField
from .forms import DataSchemaFieldForm


class DataSchemaManagerTestCase(TestCase):
    """Test cases for the DataSchema Manager views"""
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

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

    def test_dataschema_new_post(self):
        """Test adding a new dataschema field with a valid and complete form"""
        data = {'name': 'new_field', 'datatype': 'string', 'primary_key': False, 'title': 'New field',
                'description': 'My new field'}
        response = self.client.post(reverse('dataschemafield_new', kwargs={'experiment_id': self.experiment.pk}), data=data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.experiment.schema.fields.filter(name='new_field'))

    def test_dataschema_new_invalid(self):
        """Test adding a new dataschema field with an invalid form"""
        data = {'name': 'new_field', 'primary_key': False, 'title': 'New field',
                'description': 'My new field'}
        response = self.client.post(reverse('dataschemafield_new', kwargs={'experiment_id': self.experiment.pk}),
                                    data=data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.experiment.schema.fields.count() == 1)

    def test_dataschema_new_valid_no_desc(self):
        """Test adding a new dataschema field with an invalid form"""
        data = {'name': 'new_field', 'datatype': 'string', 'primary_key': False, 'title': 'New field'}
        response = self.client.post(reverse('dataschemafield_new', kwargs={'experiment_id': self.experiment.pk}),
                                    data=data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.experiment.schema.fields.filter(name='new_field'))

    def test_dataschema_edit_get(self):
        """Test getting the add data schema form"""
        response = self.client.get(reverse('dataschemafield_edit', kwargs={'pk': self.first_field.pk,
                                                                           'experiment_id': self.experiment.pk}))
        self.assertTrue(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertTrue(isinstance(response.context['form'], DataSchemaFieldForm))

    def test_dataschema_edit_post(self):
        """Test editing a dataschema field with a valid and complete form"""
        data = {'name': 'edit_field', 'datatype': 'string', 'primary_key': False, 'title': 'New field',
                'description': 'My new field'}
        response = self.client.post(reverse('dataschemafield_edit', kwargs={'pk': self.first_field.pk,
                                                                            'experiment_id': self.experiment.pk}),
                                    data=data)
        self.assertTrue(response.status_code, 302)
        self.first_field.refresh_from_db()
        self.assertTrue(self.first_field.name == 'edit_field')

    def test_dataschema_edit_invalid_form(self):
        """Test editing a dataschema field with a valid and complete form"""
        data = {'name': 'edit_field', 'datatype': 'string', 'primary_key': False, 'title': 'New field',
                'description': 'My new field'}
        response = self.client.post(reverse('dataschemafield_edit', kwargs={'pk': self.first_field.pk,
                                                                            'experiment_id': self.experiment.pk}),
                                    data=data)
        self.assertTrue(response.status_code, 302)
        self.first_field.refresh_from_db()
        self.assertTrue(self.first_field.name == 'edit_field')

    @patch('dataschema_manager.views.task_write_data_schema')
    def test_dataschema_write(self, mock_write_schema):
        """"Test if the view for writing a dataschema loads"""
        response = self.client.get(reverse('dataschema_write', kwargs={'experiment_id': self.experiment.pk}))
        self.assertTrue(response.status_code == 200)

    @patch('dataschema_manager.views.task_write_data_schema')
    def test_dataschema_write_someone_else(self, mock_write_schema):
        """Test if another user can start writing a data schema for an experiment"""
        second_client = Client()
        second_client.login(username='test2', password='test2')
        args = [reverse('dataschema_write', kwargs={'experiment_id': self.experiment.pk})]
        self.assertRaises(AssertionError, second_client.get, *args)


