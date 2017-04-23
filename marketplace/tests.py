from unittest.mock import patch
from collections import namedtuple


from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment, ChosenExperimentSteps
from git_manager.models import GitRepository
from marketplace.models import ExternalPackage, InternalPackage, PackageLanguage
from helpers.helper import ExperimentPackageTypeMixin


class MarketplaceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', owner=self.workbench_user, git_repo=self.git_repo)
        self.chosen_step = ChosenExperimentSteps.objects.create(step_id=1, experiment_id=1, step_nr=1)

        self.client = Client()
        self.client.login(username='test', password='test')
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

    def test_marketplace_index_not_signed_in(self):
        c = Client()
        response = c.get(reverse('marketplace_index'))
        self.assertEqual(response.status_code, 302)

    def test_marketplace_index(self):
        response = self.client.get(reverse('marketplace_index'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['new_packages'])
        self.assertIsNotNone(response.context['new_internal_packages'])
        self.assertIsNotNone(response.context['recent_updates'])
        self.assertIsNotNone(response.context['recent_resources'])

    def test_empty_package_list_view(self):
        response = self.client.get(reverse('package_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['object_list'])

    def test_create_external_package_get(self):
        response = self.client.get(reverse('package_new'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_create_external_package_post(self):
        external_package_data = {'package_name': 'My new package',
                                 'description': 'Desc.',
                                 'project_page': 'http://test.test',
                                 'category': '1',
                                 'language': '1'}
        response = self.client.post(reverse('package_new'), data=external_package_data)
        self.assertEqual(response.status_code, 302)
        external_package = ExternalPackage.objects.filter(id=1)
        self.assertTrue(external_package)

    def test_create_external_package_post_invalid_url(self):
        external_package_data = {'package_name': 'My new package',
                                 'description': 'Desc.',
                                 'project_page': 'http://test',
                                 'category': '1',
                                 'language': '1'}
        response = self.client.post(reverse('package_new'), data=external_package_data)
        self.assertEqual(response.status_code, 200)
        external_package = ExternalPackage.objects.filter(id=1)
        self.assertFalse(external_package)

    def test_create_internal_package_get(self):
        response = self.client.get(reverse('internal_package_new', kwargs={'experiment_id': 1, 'step_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('marketplace.views.PackageGitRepoInit')
    def test_create_internal_package_post(self, mock_package_repo_init):
        internal_package_data = {'package_name': 'My new package',
                                 'description': 'Desc',
                                 'category': '1',
                                 'language': '1'
                                 }
        mock_package_repo_init.return_value = RepoInitMock(self.git_repo)
        response = self.client.post(reverse('internal_package_new', kwargs={'experiment_id': 1, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 302)
        internal_package = InternalPackage.objects.filter(id=1)
        self.assertTrue(internal_package)

    def test_create_internal_package_post_missing_data(self):
        internal_package_data = {'package_name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internal_package_new', kwargs={'experiment_id': 1, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=1)
        self.assertFalse(internal_package)

    def test_create_internal_package_post_missing_experiment_id(self):
        internal_package_data = {'package_name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internal_package_new', kwargs={'experiment_id': 0, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=1)
        self.assertFalse(internal_package)

    def test_create_internal_package_post_missing_step_id(self):
        internal_package_data = {'package_name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internal_package_new', kwargs={'experiment_id': 1, 'step_id': 0}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=1)
        self.assertFalse(internal_package)

    def test_internal_package_dashboard(self):
        self.test_create_internal_package_post()
        response = self.client.get(reverse('internalpackage_dashboard', kwargs={'pk': 1}))
        package = InternalPackage.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['docs'])
        self.assertEqual(response.context['object'], package)
        self.assertEqual(response.context['object_type'], ExperimentPackageTypeMixin.PACKAGE_TYPE)
        self.assertIsNotNone(response.context['edit_form'])

    def test_internal_package_detail(self):
        self.test_create_internal_package_post()
        response = self.client.get(reverse('package_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['version_history'])
        self.assertIsNotNone(response.context['resources'])

    def test_packageversion_create(self):
        pass


class RepoInitMock(object):
    def __init__(self, git_repo):
        self.git_repo = git_repo

    def init_repo_boilerplate(self):
        return self.git_repo