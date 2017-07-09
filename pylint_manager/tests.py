import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from experiments_manager.models import ChosenExperimentSteps, Experiment
from git_manager.models import GitRepository
from user_manager.models import WorkbenchUser

from .utils import run_pylint
from .models import PylintResult, PylintScanResult


class PylintManagerTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/templates.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.git_repo = GitRepository.objects.create(name='Workbench-Acceptance-Experiment',
                                                     owner=self.workbench_user,
                                                     github_url='https://github.com/MOOCworkbench/Workbench-Acceptance-Experiment.git')

        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=1,
                                                    template_id=2)
        self.chosen_experiment_step = ChosenExperimentSteps.objects.create(step_id=1,
                                                                           experiment=self.experiment,
                                                                           step_nr=1,
                                                                           active=True,
                                                                           location='/src/data/')

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_run_pylint(self, mock_social_token):
        """Test if to gather pylint results from a GitHub repository"""
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        run_pylint(self.experiment)
        pylint_scan = self.experiment.pylint
        pylint_scan_result = PylintScanResult.objects.filter(for_project=pylint_scan)
        pylint_results = PylintResult.objects.filter(for_result=pylint_scan_result)
        self.assertIsNotNone(pylint_results)
        self.assertIsNotNone(pylint_results)
