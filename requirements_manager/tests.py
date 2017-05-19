from unittest.mock import patch

import requirements
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from dataschema_manager.models import DataSchema
from experiments_manager.models import Experiment
from git_manager.models import GitRepository
from marketplace.models import InternalPackage
from requirements_manager.models import Requirement
from user_manager.models import WorkbenchUser


class RequirementsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment',
                                                     owner=self.workbench_user,
                                                     github_url='https://github')
        schema = DataSchema(name='main')
        schema.save()
        self.experiment = Experiment.objects.create(title='Experiment', description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=2,
                                                    template_id=2,
                                                    schema=schema)

        self.internal_package = InternalPackage.objects.create(name='Package',
                                                               description='Package',
                                                               git_repo=self.git_repo,
                                                               language_id=2,
                                                               category_id=1,
                                                               owner_id=1,
                                                               template_id=1)

        self.requirement_one = Requirement.objects.create(package_name='django', version='1.11')
        self.requirement_two = Requirement.objects.create(package_name='pandas', version='1.23')
        self.requirement_three = Requirement.objects.create(package_name='numpy', version='0.42')

        self.client = Client()
        self.client.login(username='test', password='test')

        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

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

    @patch('requirements_manager.views.task_write_requirements_file')
    def test_write_requirements_file(self, mock_helper_task):
        response = self.client.get(reverse('requirements_write', kwargs={'object_id': self.experiment.id,
                                                                        'object_type': self.experiment.get_object_type()}))
        self.assertEqual(response.status_code, 200)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    def test_build_requirements_file_requirements_present(self, mock_gh_helper):
        self.experiment.requirements.add(self.requirement_two)
        self.experiment.requirements.add(self.requirement_three)
        language_helper = self.experiment.language_helper()
        requirements_txt = language_helper.build_requirements_file()
        self.assertFalse(self.requirement_one.package_name in requirements_txt)
        self.assertTrue(self.requirement_two.package_name in requirements_txt)
        self.assertTrue(self.requirement_three.package_name in requirements_txt)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    def test_build_requirements_file_valid_requirement(self, mock_gh_helper):
        self.experiment.requirements.add(self.requirement_one)
        self.experiment.requirements.add(self.requirement_two)
        self.experiment.requirements.add(self.requirement_three)
        requirements_list = [self.requirement_one, self.requirement_two, self.requirement_three]
        requirements_list_name = [x.package_name for x in requirements_list]
        language_helper = self.experiment.language_helper()
        requirements_txt = language_helper.build_requirements_file()
        for req in requirements.parse(requirements_txt):
            self.assertTrue(req.name in requirements_list_name)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    def test_parse_requirements_file_package_name(self, mock_gh_helper):
        self.experiment.requirements.add(self.requirement_one)
        self.experiment.requirements.add(self.requirement_two)
        self.experiment.requirements.add(self.requirement_three)
        language_helper = self.experiment.language_helper()
        requirements_txt = language_helper.build_requirements_file()
        language_helper_package = self.internal_package.language_helper()
        language_helper_package.parse_requirements(requirements_txt)
        self.assertTrue(self.internal_package.requirements)
        self.internal_package.refresh_from_db()
        package_req_list = [x.package_name for x in self.internal_package.requirements.all()]
        self.assertTrue(self.requirement_one.package_name in package_req_list)
        self.assertTrue(self.requirement_two.package_name in package_req_list)
        self.assertTrue(self.requirement_three.package_name in package_req_list)

    @patch('git_manager.helpers.language_helper.GitHubHelper')
    def test_parse_requirements_file_version(self, mock_gh_helper):
        self.experiment.requirements.add(self.requirement_one)
        self.experiment.requirements.add(self.requirement_two)
        self.experiment.requirements.add(self.requirement_three)
        language_helper = self.experiment.language_helper()
        requirements_txt = language_helper.build_requirements_file()
        language_helper_package = self.internal_package.language_helper()
        language_helper_package.parse_requirements(requirements_txt)
        self.assertTrue(self.internal_package.requirements)
        self.internal_package.refresh_from_db()
        package_req_version_list = [x.version for x in self.internal_package.requirements.all()]
        self.assertTrue(self.requirement_one.version in package_req_version_list)
        self.assertTrue(self.requirement_two.version in package_req_version_list)
        self.assertTrue(self.requirement_three.version in package_req_version_list)



