from unittest.mock import patch

import requirements
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser


class RequirementsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment',
                                                     owner=self.workbench_user,
                                                     github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment', description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo)

        self.client = Client()
        self.client.login(username='test', password='test')

        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_detail_profile_view(self):
        response = self.client.get(reverse('view_my_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['workbench_user'], self.workbench_user)

    def test_sign_out(self):
        response = self.client.get(reverse('sign_out'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['user']), 'AnonymousUser')

    def test_sign_out_without_signed_in(self):
        c = Client()
        response = c.get(reverse('sign_out'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['user']), 'AnonymousUser')

    def test_sign_in(self):
        c = Client()
        data = {'username': 'test', 'password': 'test'}
        response = c.post(reverse('sign_in'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)

    def test_edit_profile_view_get(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_edit_profile_view_post(self):
        data = {'netid': '123456789'}
        response = self.client.post(reverse('edit_profile'), data=data)
        self.assertEqual(response.status_code, 302)
        self.workbench_user.refresh_from_db()
        self.assertEqual(self.workbench_user.netid, '123456789')

    def test_edit_profile_view_post_none(self):
        data = {}
        response = self.client.post(reverse('edit_profile'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

