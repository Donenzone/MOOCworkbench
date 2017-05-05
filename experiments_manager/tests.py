import json
from collections import namedtuple

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from unittest.mock import patch
from django.core.management import call_command

from experiments_manager.models import Experiment, ChosenExperimentSteps
from experiments_manager.models import ExperimentStep
from user_manager.models import WorkbenchUser
from git_manager.models import GitRepository


class ExperimentTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=1,
                                                    template_id=2)
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_index_not_signed_in(self):
        c = Client()
        response = c.get(reverse('experiments_index'))
        self.assertEqual(response.status_code, 302)

    def test_index_signed_in(self):
        response = self.client.get(reverse('experiments_index'))
        self.assertIsNotNone(response.context['table'])

    def test_create_new_experiment_get(self):
        response = self.client.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 302)

    def test_create_new_experiment_get_not_signed_in(self):
        c = Client()
        response = c.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 302)

    @patch('experiments_manager.views.get_user_repositories')
    def test_create_new_experiment_get_mock(self, mock_get_user_repositories):
        mock_get_user_repositories.return_value = [('My First Experiment', 'https://test')]
        response = self.client.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['experiment_id'], 0)

    #@patch('experiments_manager.views.init_git_repo_for_experiment')
    #def test_create_new_experiment_post(self, mock_create_new_github_repo):
    #    git_repo = GitRepository(name='Sandbox-Research', owner=self.workbench_user, github_url='https://github')
    #    git_repo.save()

    #    data = {'title': 'Sandbox Research', 'description': 'My first experiment', 'language': 1, 'template': 2}
    #    response = self.client.post(reverse('experiment_new'), data=data)

    #    self.assertEqual(response.status_code, 302)
    #    self.assertEqual(response.url, reverse('experimentsteps_choose', kwargs={'experiment_id': 2}))

    @patch('experiments_manager.views.get_user_repositories')
    def test_create_new_experiment_post_missing_title(self, mock_get_user_repositories):
        mock_get_user_repositories.return_value = [('My First Experiment', 'https://test')]

        data = {'description': 'My first experiment', 'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('experiments_manager.views.get_user_repositories')
    def test_create_new_experiment_post_missing_description(self, mock_get_user_repositories):
        mock_get_user_repositories.return_value = [('My First Experiment', 'https://test')]

        data = {'title': 'Sandbox Research', 'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('experiments_manager.views.get_user_repositories')
    def test_create_new_experiment_post_missing_title_and_desc(self, mock_get_user_repositories):
        mock_get_user_repositories.return_value = [('My First Experiment', 'https://test')]

        data = {'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('experiments_manager.views.get_user_repositories')
    def test_create_new_experiment_post_empty(self, mock_get_user_repositories):
        mock_get_user_repositories.return_value = [('My First Experiment', 'https://test')]

        data = {}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_choose_experiment_steps_get(self):
        response = self.client.get(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}))
        self.assertIsNotNone(response.context['steps'])
        self.assertEqual(len(response.context['steps']), 5)
        self.assertEqual(response.context['experiment'].id, 1)

    def test_choose_experiment_steps_post(self):
        data = {'steplist': '["1","2","3","4","5"]'}
        response = self.client.post(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}), data=data)
        self.assertEqual(response.status_code, 200)
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        self.assertEqual(chosen_experiment_steps.count(), 5)

    def test_choose_experiment_steps_double_post(self):
        data = {'steplist': '["1","2","3","4","5"]'}
        response = self.client.post(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}), data=data)
        self.assertEqual(response.status_code, 200)
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        self.assertEqual(chosen_experiment_steps.count(), 5)

        new_data = {'steplist': '["5","4","3","2"]'}
        response = self.client.post(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}), data=new_data)
        self.assertEqual(response.status_code, 200)
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        first_step = ExperimentStep.objects.get(id=5)
        FIRST_STEP_NR = 1
        self.assertEqual(chosen_experiment_steps.count(), 4)
        self.assertEqual(chosen_experiment_steps.get(step=first_step).step_nr, FIRST_STEP_NR)

    def test_choose_experiment_steps_post_1_step(self):
        data = {'steplist': '["1"]'}
        response = self.client.post(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}), data=data)
        self.assertEqual(response.status_code, 200)
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        self.assertEqual(chosen_experiment_steps.count(), 1)

    def test_choose_experiment_steps_post_no_steps(self):
        data = {'steplist': '[]'}
        response = self.client.post(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}), data=data)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertIsNotNone(response_json['message'])

    @patch('experiments_manager.views.GitHubHelper')
    @patch('git_manager.mixins.repo_file_list.GitHubHelper.list_files_in_folder')
    @patch('experiments_manager.views.RepoFileListMixin._get_files_in_repository')
    @patch('experiments_manager.views.RepoFileListMixin.get_context_data')
    def test_experiment_detail_view(self, mock_context_data, mock_get_files_in_repository, mock_github_helper_file_list, mock_github_helper):
        self.test_choose_experiment_steps_post()
        mock_context_data.return_value = {'git_list': self.get_mock_files()}
        mock_github_helper.return_value = None
        mock_github_helper_file_list.return_value = ['file']
        mock_get_files_in_repository.return_value = self.get_mock_files()

        response = self.client.get(reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'}))
        chosen_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment).count()
        self.assertEqual(response.context['steps'].count(), chosen_steps)

    def test_experiment_detail_view_wrong_user(self):
        c = Client()
        c.login(username='test2', password='test2')
        args = [reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'})]
        self.assertRaises(AssertionError, c.get, *args)

    def test_experiment_detail_view_anon_user(self):
        c = Client()
        response = c.get(reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'}))
        self.assertEqual(response.status_code, 302)

    @patch('experiments_manager.views.GitHubHelper')
    @patch('experiments_manager.views.RepoFileListMixin._get_files_in_repository')
    def test_get_file_list_for_exp_step(self, mock_get_files_in_repository, mock_github_helper):
        self.test_choose_experiment_steps_post()
        mock_github_helper.return_value = None
        mock_get_files_in_repository.return_value = self.get_mock_files()

        response = self.client.get(reverse('file_list_for_step'), {'experiment_id': 1, 'step_id': 2})
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_json['files'], [['main.py', 'file'], ['tests.py', 'file']])

    def test_get_file_list_for_exp_non_exist_step(self):
        response = self.client.get(reverse('file_list_for_step'), {'experiment_id': 1, 'step_id': 1})
        self.assertEqual(response.status_code, 404)

    def get_mock_files(self):
        Foo = namedtuple('Foo', ['name', 'path', 'type'])
        main = Foo(name='main.py', path='/src/main.py', type='file')
        test = Foo(name='tests.py', path='/sr/tests.py', type='file')
        return [main, test]
