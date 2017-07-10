import os
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from experiments_manager.models import ChosenExperimentSteps, Experiment
from git_manager.models import GitRepository
from git_manager.helpers.github_helper import GitHubHelper
from user_manager.models import WorkbenchUser
from pylint_manager.models import PylintScanResult


from ..measurements.ci_measurement import CiEnabledMeasurement
from ..measurements.docs_measurement import DocsMeasurement
from ..measurements.pylint_measurement import PylintMeasurement
from ..measurements.requirements_measurement import RequirementsMeasurement
from ..measurements.vcs_measurement import VersionControlUseMeasurement
from ..measurements.test_measurement import TestMeasurement
from ..models import ExperimentMeasureResult, ExperimentMeasure


class QualityManagerTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/cookiecutter.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.git_repo = GitRepository.objects.create(name='Workbench-Acceptance-Experiment',
                                                     owner=self.workbench_user,
                                                     github_url='https://github.com/jlmdegoede/Workbench-Acceptance-Experiment.git')
        self.python_experiment = Experiment.objects.create(title='Workbench-Acceptance-Experiment',
                                                           description='test',
                                                           owner=self.workbench_user,
                                                           language_id=2,
                                                           git_repo=self.git_repo,
                                                           template_id=2)
        self.python_experiment.travis.enabled = True
        self.python_experiment.travis.save()

        self.chosen_step = ChosenExperimentSteps.objects.create(
            step_id=1,
            experiment=self.python_experiment,
            step_nr=1,
            started_at=datetime.now(),
            active=True,
            location='src/data',
            main_module='make_dataset'
        )

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_ci_measurement(self, mock_social_token):
        github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = github_token
        ci_measure = CiEnabledMeasurement(self.chosen_step)
        ci_measure.measure()
        ci_measure.save_and_get_result()
        measure = ExperimentMeasure.objects.get(name='Use of CI')
        result = ExperimentMeasureResult.objects.filter(measurement=measure)
        self.assertTrue(result)
        result = result[0]
        self.assertTrue(result.result)
        self.assertTrue(result.raw_values.all())

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_docs_measurement(self, mock_social_token):
        github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = github_token
        docs_measure = DocsMeasurement(self.chosen_step)
        docs_measure.measure()
        docs_measure.save_and_get_result()
        measure = ExperimentMeasure.objects.get(name='Documentation')
        result = ExperimentMeasureResult.objects.filter(measurement=measure)
        self.assertTrue(result)
        result = result[0]
        self.assertTrue(result.result)
        self.assertTrue(result.raw_values.all())

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_pylint_measurement(self, mock_social_token):
        github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = github_token
        pylint_measure = PylintMeasurement(self.chosen_step)
        pylint_measure.measure()
        pylint_measure.save_and_get_result()
        measure = ExperimentMeasure.objects.get(name='Static code analysis')
        result = ExperimentMeasureResult.objects.filter(measurement=measure)
        self.assertTrue(result)
        result = result[0]
        self.assertTrue(result.result)
        pylint_results = PylintScanResult.objects.filter(for_project=self.python_experiment.pylint)
        self.assertTrue(pylint_results)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_reqs_measurement(self, mock_social_token):
        github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = github_token
        reqs_measure = RequirementsMeasurement(self.chosen_step)
        reqs_measure.measure()
        reqs_measure.save_and_get_result()
        measure = ExperimentMeasure.objects.get(name='Dependencies defined')
        result = ExperimentMeasureResult.objects.filter(measurement=measure)
        self.assertTrue(result)
        result = result[0]
        self.assertTrue(result.result)

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_codecoverage_measurement(self, mock_social_token):
        mock_social_token.return_value = os.environ.get('GITHUB_TOKEN')
        with patch.object(GitHubHelper, 'owner', 'MOOCworkbench'):
            cov_measure = TestMeasurement(self.chosen_step)
            cov_measure.measure()
            cov_measure.save_and_get_result()
            measure = ExperimentMeasure.objects.get(name='Testing')
            result = ExperimentMeasureResult.objects.filter(measurement=measure)
            self.assertTrue(result)
            result = result[0]
            self.assertTrue(result.result)
            self.assertTrue(result.raw_values.all())

    @patch('git_manager.helpers.github_helper.GitHubHelper._get_social_token')
    def test_vcs_measurement(self, mock_social_token):
        github_token = os.environ.get('GITHUB_TOKEN')
        mock_social_token.return_value = github_token
        vcs_measure = VersionControlUseMeasurement(self.chosen_step)
        vcs_measure.measure()
        vcs_measure.save_and_get_result()
        measure = ExperimentMeasure.objects.get(name='Version control use')
        result = ExperimentMeasureResult.objects.filter(measurement=measure)
        self.assertTrue(result)
        result = result[0]
        self.assertTrue(result.result)
        self.assertTrue(result.raw_values.all())