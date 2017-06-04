"""This module is responsible for creating new internal packages"""
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
    """Helper for PackageGitRepoInit with status codes"""
    STEP_CREATING_GITHUB_REPO = 2
    STEP_CLONING_REPO = 3
    STEP_FILTERING_SUBTREE = 4
    STEP_CREATING_BOILERPLATE_CODE = 5
    STEP_CLEAN_UP = 6


class PackageGitRepoInit(object):
    """Initializes a GitHub repository for a package
    Extracts a subtree if the experiment is not None and places this in new GitHub repository
    Then adds the CookieCutter template code
    If Experiment is None, only a new GitHub repository with cookiecutter is created
    If a GitHub repository already exists, existing_repo is set to True
    :param internal_package: The internalpackage object for which to create a new GitHub repo
    :param username: The user for which to create a new GitHub repository
    :param experiment: The experiment used to extract the source from and place this in the new package repo
    :param step_folder: The folder in the experiment that should be extracted and placed in the new package repo"""
    TEMPLATE_FOLDER = 'codetemplates/'

    def __init__(self, internal_package, username, experiment=None, step_folder=None):
        self.existing_repo = False
        self.experiment = experiment
        self.internal_package = internal_package
        self.step_folder = step_folder
        self.username = username
        self.github_helper = self.initialize_github_helper(experiment, internal_package)
        self.language_helper = None
        self.language = None
        if self.experiment:
            self.language_helper = self.experiment.language_helper()
            self.language = self.experiment.language

    def initialize_github_helper(self, experiment, internal_package):
        """Initialize the GitHub helper, by creating a new repository
        Fails if a repo already exists, in which case GitHubHelper is initialized with existing repo
        and package creation process is skipped"""
        try:
            return GitHubHelper(internal_package.owner, internal_package.name, create=True)
        except Exception as e:
            self.github_helper = GitHubHelper(internal_package.owner, internal_package.name)
            self.existing_repo = True
            git_repo_obj = self.create_git_db_object()
            self.internal_package.git_repo = git_repo_obj
            self.internal_package.save()
            logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', internal_package.owner,
                         internal_package, e)
            return self.github_helper

    def init_repo_boilerplate(self):
        """Initializes the repository with source code
        (1) Create new GitRepo DB object
        (2) If experiment not None, clone experiment repo, filter subtree
        (3) Clone new Package GitHub repo
        (4) Move files from filtered subtree into new package repo
        (5) Clone cookiecutter and move into new package repo
        (6) Clean-up and add existing requirements to new GitHub repo"""
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

        # a language_helper for an empty package cannot be added at the init
        # because not gitrepo object exists yet
        # so check if the language_helper is set and if not, set it now
        if not self.language_helper:
            self.language_helper = self.internal_package.language_helper()
            self.language = self.internal_package.language
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
        """Clone the cookiecutter template and commit all new files into the package repo"""
        template_to_clone = CookieCutterTemplate.objects.filter(meant_for=CookieCutterTemplate.PACKAGE,
                                                                language=self.language).first()
        project_dict = self.language_helper.cookiecutter_dict(self.internal_package)
        clone_cookiecutter_template_with_dict(template_to_clone, git_helper.repo_dir_of_user(), project_dict)
        git_helper.repo.git.add('.')
        git_helper.repo.index.commit('Pip package template added')
        git_helper.push()

    def create_git_db_object(self):
        """Create the DB object of the GitRepository with the required information"""
        repo = self.github_helper.github_repository
        git_repo_obj = GitRepository()
        git_repo_obj.name = repo.name
        git_repo_obj.owner = self.internal_package.owner
        git_repo_obj.github_url = repo.html_url
        git_repo_obj.save()
        return git_repo_obj

    def clone_basis_for_module_and_return_git_helper(self):
        """Clone the new Git repository of the package"""
        github_helper_experiment = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
        git_helper = GitHelper(github_helper_experiment)
        try:
            git_helper.clone_or_pull_repository()
        except Exception as e:
            print(e)
        return git_helper

    def move_code_from_base_to_new(self, git_helper):
        """Move the filtered subtree code from the old repo to the new
        By setting a new Remote URL for the repository and push the changes"""
        git_helper.filter_and_checkout_subfolder(self.step_folder)
        new_remote = self.github_helper.get_clone_url()
        git_helper.set_remote(new_remote)
        git_helper.push()

    def clone_new_module_repo(self):
        """Clone the package repository"""
        package_repo = GitHelper(self.github_helper)
        package_repo.clone_or_pull_repository()
        return package_repo

    def move_module_into_folder(self, git_helper, package_name):
        """Make sure the filtered subtree is placed into the package folder in the new repo"""
        if 'Python' in self.language.language:
            git_helper.move_repo_contents_to_folder(package_name)
        elif 'R' in self.language.language:
            git_helper.move_repo_contents_to_folder('R')
        git_helper.repo.index.commit('Moved module into own folder')
        git_helper.push()

    def _create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        """Create a new file in the repository
        :param file_name: File name of the file
        :param commit_message: Commit message
        :param folder: Optional folder where to place the file
        :param contents: Optional contents to fill the file with"""
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)
