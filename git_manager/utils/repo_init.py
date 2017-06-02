import logging

from cookiecutter_manager.helpers.helper_cookiecutter import \
    clone_cookiecutter_template_with_dict
from cookiecutter_manager.models import CookieCutterTemplate
from experiments_manager.consumers import \
    send_exp_package_creation_status_update

from ..helpers.git_helper import GitHelper, clean_up_after_git_helper
from ..helpers.github_helper import GitHubHelper
from ..models import GitRepository

logger = logging.getLogger(__name__)


class PackageCreationProgress(object):
    STEP_CREATING_GITHUB_REPO = 2
    STEP_CLONING_REPO = 3
    STEP_FILTERING_SUBTREE = 4
    STEP_CREATING_BOILERPLATE_CODE = 5
    STEP_CLEAN_UP = 6


class PackageGitRepoInit(object):
    TEMPLATE_FOLDER = 'codetemplates/'

    def __init__(self, internal_package, username, experiment=None, step_folder=None):
        self.existing_repo = False
        self.experiment = experiment
        self.internal_package = internal_package
        self.step_folder = step_folder
        self.username = username
        self.github_helper = self.initialize_github_helper(experiment, internal_package)
        if self.experiment:
            self.language_helper = self.experiment.language_helper()
            self.language = self.experiment.language

    def initialize_github_helper(self, experiment, internal_package):
        try:
            return GitHubHelper(internal_package.owner, internal_package.name, create=True)
        except Exception as e:
            self.github_helper = GitHubHelper(internal_package.owner, internal_package.name)
            self.existing_repo = True
            git_repo_obj = self.create_git_db_object()
            self.internal_package.git_repo = git_repo_obj
            self.internal_package.save()
            logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', experiment.owner,
                         internal_package, e)
            return self.github_helper

    def init_repo_boilerplate(self):
        # create git repository in DB
        git_repo_obj = self.create_git_db_object()
        self.internal_package.git_repo = git_repo_obj
        self.internal_package.save()

        # clone current experiment
        if self.experiment:
            git_helper = self.clone_basis_for_module_and_return_git_helper()
            # take code from module and commit it to new repo
            self.move_code_from_base_to_new(git_helper)
            send_exp_package_creation_status_update(self.username, PackageCreationProgress.STEP_CREATING_GITHUB_REPO)

        # clone the new repository
        module_git_helper = self.clone_new_module_repo()
        send_exp_package_creation_status_update(self.username, PackageCreationProgress.STEP_CLONING_REPO)
        # move files of subtree to own package folder
        if self.experiment:
            self.move_module_into_folder(module_git_helper, self.github_helper.repo_name)
            send_exp_package_creation_status_update(self.username, PackageCreationProgress.STEP_FILTERING_SUBTREE)

        # init the cookiecutter package template
        self.create_cookiecutter_boilerplate(module_git_helper)
        send_exp_package_creation_status_update(self.username, PackageCreationProgress.STEP_CREATING_BOILERPLATE_CODE)

        # remove the temp repo folders in github_repositories/
        if self.experiment:
            clean_up_after_git_helper(git_helper)
        clean_up_after_git_helper(module_git_helper)
        send_exp_package_creation_status_update(self.username, PackageCreationProgress.STEP_CLEAN_UP)

        language_helper = self.internal_package.language_helper()
        req_file_loc = language_helper.get_requirements_file_location()
        requirements_file = self.github_helper.view_file(req_file_loc)
        language_helper.parse_requirements(requirements_file)

        return git_repo_obj

    def create_cookiecutter_boilerplate(self, git_helper):
        template_to_clone = CookieCutterTemplate.objects.filter(meant_for=CookieCutterTemplate.PACKAGE,
                                                                language=self.language).first()
        project_dict = self.language_helper.cookiecutter_dict(self.internal_package)
        clone_cookiecutter_template_with_dict(template_to_clone, git_helper.repo_dir_of_user(), project_dict)
        git_helper.repo.git.add('.')
        git_helper.repo.index.commit('Pip package template added')
        git_helper.push()

    def create_git_db_object(self):
        repo = self.github_helper.github_repository
        git_repo_obj = GitRepository()
        git_repo_obj.name = repo.name
        git_repo_obj.owner = self.internal_package.owner
        git_repo_obj.github_url = repo.html_url
        git_repo_obj.save()
        return git_repo_obj

    def clone_basis_for_module_and_return_git_helper(self):
        github_helper_experiment = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
        git_helper = GitHelper(github_helper_experiment)
        try:
            git_helper.clone_or_pull_repository()
        except Exception as e:
            print(e)
        return git_helper

    def move_code_from_base_to_new(self, git_helper):
        git_helper.filter_and_checkout_subfolder(self.step_folder)
        new_remote = self.github_helper.get_clone_url()
        git_helper.set_remote(new_remote)
        git_helper.push()

    def clone_new_module_repo(self):
        package_repo = GitHelper(self.github_helper)
        package_repo.clone_or_pull_repository()
        return package_repo

    def move_module_into_folder(self, git_helper, package_name):
        if 'Python' in self.language.language:
            git_helper.move_repo_contents_to_folder(package_name)
        elif 'R' in self.language.language:
            git_helper.move_repo_contents_to_folder('R')
        git_helper.repo.index.commit('Moved module into own folder')
        git_helper.push()

    def _create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)
