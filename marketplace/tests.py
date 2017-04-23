from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from unittest.mock import patch
from django.core.management import call_command

from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from marketplace.models import ExternalPackage, InternalPackage, PackageLanguage


class MarketplaceTestCase(TestCase):
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

