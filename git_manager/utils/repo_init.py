import os

from experiments_manager.models import ChosenExperimentSteps
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from git_manager.models import GitRepository
from requirements_manager.helper import build_requirements_file
from helpers.helper import replace_variable_in_file
from helpers.helper import get_absolute_path
from marketplace.helpers.helper import SetupPyVariables, build_setup_py


class GitRepoInit(object):
    TEMPLATE_FOLDER = 'codetemplates/'

    def __init__(self, github_helper, type):
        self.github_helper = github_helper
        self.template_type_folder = '{0}{1}/'.format(self.TEMPLATE_FOLDER, type)

    def create_travis_file(self):
        self._create_new_file_in_repo('.travis.yml', 'Added Travis CI config',
                                      contents=self.get_file_contents('.travis.yml'))

    def create_readme_file(self):
        self._create_new_file_in_repo('README.md', 'Added README file', contents=self.get_file_contents('README.md'))

    def _create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)

    def replace_folder_in_file(self, contents, folder):
        return contents.replace('{0}', folder)

    def get_file_contents(self, filename, part_of_step=False, folder=None):
        if part_of_step:
            path = '{0}{1}steps/{2}'.format(get_absolute_path(), self.template_type_folder, filename)
        else:
            path = '{0}{1}{2}'.format(get_absolute_path(), self.template_type_folder, filename)
        file_to_open = open(path, 'r')

        contents = file_to_open.read()
        if folder:
            contents = self.replace_folder_in_file(contents, folder)
        return contents


    class Meta:
        abstract = True


class PackageGitRepoInit(GitRepoInit):

    def __init__(self, internal_package, experiment, step_folder):
        github_helper_package = GitHubHelper(experiment.owner, internal_package.package_name, create=True)
        super().__init__(github_helper_package, type='pip')
        self.experiment = experiment
        self.internal_package = internal_package
        self.step_folder = step_folder

    def init_repo_boilerplate(self):
        # create git repository in DB
        git_repo_obj = self.create_git_db_object()
        # clone current experiment
        git_helper = self.clone_basis_for_module_and_return_git_helper()
        # take code from module and commit it to new repo
        self.move_code_from_base_to_new(git_helper)

        # clone the new repository
        module_git_helper = self.clone_new_module_repo()
        self.move_module_into_folder(module_git_helper)

        self.create_setup_py()
        self.create_travis_file()
        self.create_readme_file()

        return git_repo_obj

    def create_git_db_object(self):
        repo = self.github_helper.github_repository
        git_repo_obj = GitRepository()
        git_repo_obj.name = repo.name
        git_repo_obj.owner = self.experiment.owner
        git_repo_obj.github_url = repo.html_url
        git_repo_obj.save()
        return git_repo_obj

    def clone_basis_for_module_and_return_git_helper(self):
        github_helper_experiment = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
        git_helper = GitHelper(github_helper_experiment)
        try:
            git_helper.clone_repository()
        except Exception as e:
            print(e)
        return git_helper

    def move_code_from_base_to_new(self, git_helper):
        git_helper.filter_and_checkout_subfolder(self.step_folder)
        new_remote = self.github_helper.get_clone_url()
        git_helper.set_remote(new_remote)
        git_helper.push_changes()

    def clone_new_module_repo(self):
        package_repo = GitHelper(self.github_helper)
        package_repo.clone_repository()
        return package_repo

    def move_module_into_folder(self, git_helper):
        git_helper.move_repo_contents_to_folder(self.step_folder)
        git_helper.repo.index.commit('Moved module into own folder')
        git_helper.push_changes()

    def create_setup_py(self):
        setup_py_template = self.get_file_contents('setup.py_template')
        setup_py = build_setup_py(self.internal_package, setup_py_template)
        self._create_new_file_in_repo('setup.py', commit_message='Added setup.py file', contents=setup_py)

    def copy_requirements_txt(self):
        requirements_txt = build_requirements_file(self.experiment.pk, self.experiment.get_object_type())
        self._create_new_file_in_repo('requirements.txt', commit_message='Added requirements.txt file', contents=requirements_txt)

