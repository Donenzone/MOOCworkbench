import os
import shutil

from django.test import TestCase
from django.contrib.auth.models import User
from git import Repo
from django.core.management import call_command

from docs_manager.sphinx_helper import SphinxHelper
from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment, ChosenExperimentSteps
from experiments_manager.models import ExperimentStep
from git_manager.models import GitRepository
from coverage_manager.models import CodeCoverage
from helpers.helper import ExperimentPackageTypeMixin


class SphinxHelperTest(TestCase):
    @classmethod
    def setUpClass(cls):
        clone_url = 'https://github.com/jlmdegoede/Sandbox-Research-5.git'
        cls.repo_dir = 'github_repositories/jlmdegoede/Sandbox-Research-5/'
        Repo.clone_from(clone_url, cls.repo_dir)

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Sandbox-Research-5', owner=self.workbench_user, github_url='https://github.com/jlmdegoede/Sandbox-Research-5')
        self.experiment = Experiment.objects.create(title='Experiment', description='test', owner=self.workbench_user, git_repo=self.git_repo)

        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        step = ExperimentStep.objects.get(name='Publication phase')
        self.chosen_step = ChosenExperimentSteps.objects.create(experiment=self.experiment, step=step, step_nr=1)
        self.steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)

        self.sphinx = SphinxHelper(self.experiment, self.steps, 'jlmdegoede')

    def test_init(self):
        self.assertIsNotNone(self.sphinx)

    def test_add_sphinx_to_repo(self):
        self.sphinx.add_sphinx_to_repo()
        docs_dir = '{0}/docs'.format(self.repo_dir)
        build_dir = '{0}/docs/_build'.format(self.repo_dir)
        self.assertTrue(os.path.isdir(docs_dir))
        self.assertTrue(os.path.isdir(build_dir))

    def test_resync_docs(self):
        self.sphinx.build_and_sync_docs()

    def test_coverage_measurement(self):
        self.sphinx.update_coverage()
        coverage = self.sphinx.get_coverage_data()
        self.assertTrue(coverage[0])
        self.assertIsInstance(coverage[1], int)
        self.assertIsInstance(coverage[2], int)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repo_dir)