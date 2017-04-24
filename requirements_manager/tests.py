from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from requirements_manager.models import Requirement
from marketplace.models import InternalPackage


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

        self.internal_package = InternalPackage.objects.create(package_name='Package',
                                                               description='Package',
                                                               git_repo=self.git_repo,
                                                               language_id=1,
                                                               category_id=1,
                                                               owner_id=1)

        self.requirement_one = Requirement.objects.create(package_name='django', version='1.11')
        self.requirement_two = Requirement.objects.create(package_name='pandas', version='1.23')
        self.requirement_three = Requirement.objects.create(package_name='numpy', version='0.42')

        self.client = Client()
        self.client.login(username='test', password='test')

        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

    def test_requirements_list_view(self):
        response = self.client.get(reverse('requirements_list', kwargs={'pk': self.experiment.id,
                                                                        'object_type': self.experiment.get_object_type()}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['requirements_form'])
        self.assertEqual(response.context['object_id'], str(self.experiment.id))

    def test_requirements_list_view_with_requirements(self):
        self.experiment.requirements.add(self.requirement_one)
        self.experiment.requirements.add(self.requirement_two)
        response = self.client.get(reverse('requirements_list', kwargs={'pk': self.experiment.id,
                                                                        'object_type': self.experiment.get_object_type()}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['object_list']), [self.requirement_one, self.requirement_two])

    def test_requirement_create_view_post_experiment(self):
        data = {'package_name': 'My New Pakage', 'version': '54.0'}
        response = self.client.post(reverse('requirement_add', kwargs={'object_id': self.experiment.id,
                                                                        'object_type': self.experiment.get_object_type()}),
                                                                data=data)
        self.assertEqual(response.status_code, 302)
        requirement_added = Requirement.objects.filter(package_name=data['package_name'], version=data['version'])
        self.assertTrue(requirement_added)
        requirement_added = requirement_added[0]
        self.assertEqual(self.experiment.requirements.all()[0], requirement_added)

    def test_requirement_create_view_post_package(self):
        data = {'package_name': 'My New Pakage', 'version': '54.0'}
        response = self.client.post(reverse('requirement_add', kwargs={'object_id': self.internal_package.id,
                                                                        'object_type': self.internal_package.get_object_type()}),
                                                                data=data)
        self.assertEqual(response.status_code, 302)
        requirement_added = Requirement.objects.filter(package_name=data['package_name'], version=data['version'])
        self.assertTrue(requirement_added)
        requirement_added = requirement_added[0]
        self.assertEqual(self.internal_package.requirements.all()[0], requirement_added)

    def test_remove_requirement_from_experiment(self):
        self.experiment.requirements.add(self.requirement_one)
        self.experiment.requirements.add(self.requirement_two)

        data = {'requirement_id': 1}
        response = self.client.post(reverse('requirement_delete', kwargs={'object_id': self.experiment.id,
                                                                        'object_type': self.experiment.get_object_type()}),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        requirement_one = Requirement.objects.filter(package_name=self.requirement_one.package_name)
        self.assertFalse(requirement_one)
        self.experiment.refresh_from_db()
        self.assertFalse(requirement_one in self.experiment.requirements.all())



