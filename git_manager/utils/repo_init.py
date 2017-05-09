import shutil

from requirements_manager.helper import build_requirements_file_object_type_id
from helpers.helper import get_absolute_path
from cookiecutter_manager.helpers.helper_cookiecutter import clone_cookiecutter_template_with_dict
from cookiecutter_manager.models import CookieCutterTemplate
from experiments_manager.consumers import send_exp_package_creation_status_update

from ..helpers.github_helper import GitHubHelper
from ..helpers.git_helper import GitHelper
from ..models import GitRepository


class GitRepoInit(object):
    TEMPLATE_FOLDER = 'codetemplates/'

    def __init__(self, github_helper, type):
        self.github_helper = github_helper

    def _create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)

    class Meta:
        abstract = True


class PackageGitRepoInit(GitRepoInit):

    def __init__(self, internal_package, experiment, step_folder, username):
        github_helper_package = GitHubHelper(experiment.owner, internal_package.name, create=True)
        super().__init__(github_helper_package, type='pip')
        self.experiment = experiment
        self.internal_package = internal_package
        self.step_folder = step_folder
        self.username = username

    def init_repo_boilerplate(self):
        # create git repository in DB
        git_repo_obj = self.create_git_db_object()
        # clone current experiment
        git_helper = self.clone_basis_for_module_and_return_git_helper()
        # take code from module and commit it to new repo
        self.move_code_from_base_to_new(git_helper)
        send_exp_package_creation_status_update(self.username, 2)

        # clone the new repository
        module_git_helper = self.clone_new_module_repo()
        send_exp_package_creation_status_update(self.username, 3)
        # move files of subtree to own package folder
        self.move_module_into_folder(module_git_helper, self.github_helper.repo_name)
        send_exp_package_creation_status_update(self.username, 4)

        # init the cookiecutter package template
        self.create_cookiecutter_boilerplate(module_git_helper)
        send_exp_package_creation_status_update(self.username, 5)

        # remove the temp repo folders in github_repositories/
        self.clean_up_github_folders(git_helper)
        self.clean_up_github_folders(module_git_helper)
        send_exp_package_creation_status_update(self.username, 6)

        return git_repo_obj

    def create_cookiecutter_boilerplate(self, git_helper):
        template_to_clone = CookieCutterTemplate.objects.filter(meant_for=CookieCutterTemplate.PACKAGE).first()
        project_dict = {'project_name': self.internal_package.name,
                        'app_name': self.github_helper.repo_name,
                        'full_name': self.username,
                        'email': self.experiment.owner.user.email,
                        'github_username': self.github_helper.owner,
                        'project_short_description': self.internal_package.description}
        clone_cookiecutter_template_with_dict(template_to_clone, git_helper.repo_dir_of_user(), project_dict)
        git_helper.repo.git.add('.')
        git_helper.repo.index.commit('Pip package template added')
        git_helper.push()

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
        git_helper.move_repo_contents_to_folder(package_name)
        git_helper.repo.index.commit('Moved module into own folder')
        git_helper.push()

    def copy_requirements_txt(self):
        requirements_txt = build_requirements_file_object_type_id(self.experiment.pk, self.experiment.get_object_type())
        self._create_new_file_in_repo('requirements.txt', commit_message='Added requirements.txt file',
                                      contents=requirements_txt)

    def clean_up_github_folders(self, git_helper):
        shutil.rmtree(git_helper.repo_dir)
