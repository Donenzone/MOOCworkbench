import json
import os
from datetime import datetime
from collections import namedtuple
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import Client, TestCase

from dataschema_manager.models import DataSchema
from experiments_manager.models import (ChosenExperimentSteps, Experiment,
                                        ExperimentStep)
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser


class ExperimentTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user,
                                                     github_url='https://github')
        schema = DataSchema(name='main')
        schema.save()
        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=1,
                                                    template_id=2,
                                                    schema=schema)
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_index_not_signed_in(self):
        """Test index when not signed in"""
        c = Client()
        response = c.get(reverse('experiments_index'))
        self.assertEqual(response.status_code, 302)

    def test_index_signed_in(self):
        """Test if index loads while signed in"""
        response = self.client.get(reverse('experiments_index'))
        self.assertIsNotNone(response.context['table'])

    @patch('experiments_manager.views.views_create.SocialToken')
    def test_create_new_experiment_get(self, mock_social_token):
        """Test http get for creating a new experiment"""
        mock_social_token.return_value = 'socialtoken'
        response = self.client.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 200)

    def test_create_new_experiment_get_not_signed_in(self):
        """Test http get for creating a new experiment when not signed in"""
        c = Client()
        response = c.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 302)

    # @patch('experiments_manager.views.init_git_repo_for_experiment')
    # def test_create_new_experiment_post(self, mock_create_new_github_repo):
    #    git_repo = GitRepository(name='Sandbox-Research', owner=self.workbench_user, github_url='https://github')
    #    git_repo.save()

    #    data = {'title': 'Sandbox Research', 'description': 'My first experiment', 'language': 1, 'template': 2}
    #    response = self.client.post(reverse('experiment_new'), data=data)

    #    self.assertEqual(response.status_code, 302)
    #    self.assertEqual(response.url, reverse('experimentsteps_choose', kwargs={'experiment_id': 2}))

    def test_create_new_experiment_post_missing_title(self):
        """Test creating a new experiment with a missing title"""
        data = {'description': 'My first experiment', 'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_create_new_experiment_post_missing_description(self):
        """Test creating a new experiment with a missing description"""
        data = {'title': 'Sandbox Research', 'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_create_new_experiment_post_missing_title_and_desc(self):
        """Test creating a new experiment with a missing title and description"""
        data = {'language': 1, 'template': 2}
        response = self.client.post(reverse('experiment_new'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_create_new_experiment_post_empty(self):
        """Test creating a new experiment with empty data"""
        data = {}
        response = self.client.post(reverse('experiment_new'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_choose_experiment_steps_get(self):
        """Test http get for choosing experiment steps"""
        response = self.client.get(reverse('experimentsteps_choose', kwargs={'experiment_id': 1}))
        self.assertIsNotNone(response.context['steps'])
        self.assertEqual(len(response.context['steps']), 5)
        self.assertEqual(response.context['object'].id, 1)

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

    @patch('experiments_manager.views.views.GitHubHelper')
    @patch('experiments_manager.views.views.GitHubHelper.list_files_in_folder')
    @patch('experiments_manager.views.views.get_files_for_steps')
    @patch('experiments_manager.views.views.get_files_for_step')
    def test_experiment_detail_view(self, mock_context_data, mock_get_files_in_repository, mock_github_helper_file_list,
                                    mock_github_helper):
        self.test_choose_experiment_steps_post()
        mock_context_data.return_value = {'git_list': self.get_mock_files()}
        mock_github_helper.return_value = None
        mock_github_helper_file_list.return_value = ['file']
        mock_get_files_in_repository.return_value = self.get_mock_files()

        response = self.client.get(reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'}))
        chosen_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment).count()
        self.assertEqual(response.context['active_step_id'], 1)

    def test_experiment_detail_view_wrong_user(self):
        c = Client()
        c.login(username='test2', password='test2')
        args = [reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'})]
        self.assertRaises(AssertionError, c.get, *args)

    def test_experiment_detail_view_anon_user(self):
        c = Client()
        response = c.get(reverse('experiment_detail', kwargs={'pk': 1, 'slug': 'experiment'}))
        self.assertEqual(response.status_code, 302)

    @patch('experiments_manager.views.views.get_github_helper')
    @patch('experiments_manager.views.views.get_files_for_step')
    def test_get_file_list_for_exp_step(self, mock_get_files_in_repository, mock_github_helper):
        self.test_choose_experiment_steps_post()
        mock_github_helper.return_value = None
        mock_get_files_in_repository.return_value = self.get_mock_files()
        response = self.client.get(reverse('file_list_for_step'), {'experiment_id': 1, 'step_id': 2})
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_json['files'], [
            {'file_url': '/experiments/file/1/?file_name=/src/main.py', 'slug': 'main-py', 'file_path': '/src/main.py',
             'type': 'file', 'static_code_analysis': [], 'file_name': 'main.py'},
            {'file_url': '/experiments/file/1/?file_name=/sr/tests.py', 'slug': 'tests-py', 'file_path': '/sr/tests.py',
             'type': 'file', 'static_code_analysis': [], 'file_name': 'tests.py'}])

    def test_get_file_list_for_exp_non_exist_step(self):
        response = self.client.get(reverse('file_list_for_step'), {'experiment_id': 1, 'step_id': 1})
        self.assertEqual(response.status_code, 404)

    @patch('experiments_manager.views.views_create.GitHubHelper')
    def test_step_four_in_experiment(self, mock_github_helper):
        """Test if the fourth step in creating an experiment loads"""
        response = self.client.get(reverse('experiment_first_time', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['object'])
        self.assertFalse(response.context['configured'])
        self.assertTrue(response.context['travis'])

    def test_complete_step_gonext(self):
        """Test complete the current step and go to next
        Creates two chosen steps and tests if moved on to the next step"""
        ChosenExperimentSteps.objects.create(
            step_id=1,
            experiment=self.experiment,
            step_nr=1,
            started_at=datetime.now(),
            active=True,
            location='src/data',
            main_module='make_dataset'
        )
        chosen_step_two = ChosenExperimentSteps.objects.create(
            step_id=2,
            experiment=self.experiment,
            step_nr=2,
            location='src/data',
            main_module='make_dataset'
        )
        old_step = self.experiment.get_active_step()
        response = self.client.get(reverse('complete_step_and_go_to_next', kwargs={'experiment_id': 1,
                                                                                   'create_package': 0}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(old_step != self.experiment.get_active_step())
        self.assertTrue(self.experiment.get_active_step().pk == chosen_step_two.pk)

    @patch('experiments_manager.views.views.GitHubHelper')
    def test_publish_experiment(self, mock_gh_helper):
        """Test if an experiment can be published"""
        mock_gh_helper.return_value = MockGitHub('test', 'test')
        response = self.client.get(reverse('experiment_publish_2', kwargs={'pk': 1, 'slug': self.experiment.slug()}))
        self.assertEqual(response.status_code, 302)
        self.experiment.refresh_from_db()
        self.assertTrue(self.experiment.unique_id)
        self.assertTrue(self.experiment.publish_url_zip == 'https://test_release')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_experiment_readonly_view(self, mock_social_token):
        """Test if readonly view works after publishing an experiment"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        git_repo = GitRepository.objects.create(name='Workbench-Acceptance-Experiment', owner=self.workbench_user,
                                                github_url='https://github')
        experiment = Experiment.objects.create(title='Workbench-Acceptance-Experiment',
                                               description='test',
                                               owner=self.workbench_user,
                                               git_repo=git_repo,
                                               language_id=1,
                                               template_id=2)

        self.publish_experiment(experiment)
        experiment.refresh_from_db()
        response = self.client.get(reverse('experiment_readonly', kwargs={'unique_id': experiment.unique_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['completed'])

    def get_mock_files(self):
        Foo = namedtuple('Foo', ['name', 'path', 'type', 'slug', 'pylint_results'])
        main = Foo(name='main.py', path='/src/main.py', type='file', slug='main-py', pylint_results=[])
        test = Foo(name='tests.py', path='/sr/tests.py', type='file', slug='tests-py', pylint_results=[])
        return [main, test]

    @patch('experiments_manager.views.views.GitHubHelper')
    def publish_experiment(self, experiment, mock_gh_helper):
        """Test if an experiment can be published"""
        mock_gh_helper.return_value = MockGitHub('test', 'test')
        self.client.get(reverse('experiment_publish_2', kwargs={'pk': experiment.pk,
                                                                'slug': experiment.slug()}))


class MockGitRelease(object):
    def __init__(self):
        self.html_url = "https://test_release"


class MockGitHub(object):
    def __init__(self, owner, title):
        self.owner = owner
        self.title = title

    def create_release(self, tag_name, name, body, pre_release):
        return MockGitRelease()
