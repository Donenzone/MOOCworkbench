import os

from experiments_manager.models import ChosenExperimentSteps
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from git_manager.models import GitRepository


class GitRepoInit(object):
    TEMPLATE_FOLDER = 'codetemplates/'

    def __init__(self, github_helper, type):
        self.github_helper = github_helper
        self.template_type_folder = '{0}{1}/'.format(self.TEMPLATE_FOLDER, type)

    def _create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)

    def replace_folder_in_file(self, contents, folder):
        return contents.replace('{0}', folder)

    def replace_variable_in_file(self, contents, variable, value):
        variable_name = '{{{0}}}'.format(variable)
        print(variable_name)
        return contents.replace(variable_name, value)

    def get_file_contents(self, filename, part_of_step=False, folder=None):
        if part_of_step:
            path = '{0}{1}steps/{2}'.format(self.get_script_path(), self.template_type_folder, filename)
        else:
            path = '{0}{1}{2}'.format(self.get_script_path(), self.template_type_folder, filename)
        file_to_open = open(path, 'r')

        contents = file_to_open.read()
        if folder:
            contents = self.replace_folder_in_file(contents, folder)
        return contents

    def get_script_path(self):
        return '{0}/'.format(os.path.dirname(os.path.realpath(__file__)))

    class Meta:
        abstract = True


class PackageGitRepoInit(GitRepoInit):

    PACKAGE_NAME_VAR = 'PACKAGE_NAME'
    VERSION_VAR = 'VERSION'
    AUTHOR_VAR = 'AUTHOR'
    DESCRIPTION_VAR = 'DESCRIPTION'
    URL_VAR = 'URL'
    AUTHOR_MAIL = 'AUTHOR_EMAIL'
    LICENSE_VAR = 'LICENSE'
    PACKAGE_VAR = 'PACKAGE'

    def __init__(self, internal_package, experiment, step_folder):
        github_helper_package = GitHubHelper(experiment.owner, internal_package.package_name, create=True)
        super().__init__(github_helper_package, 'pip')
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
        self.create_setup_py(self.step_folder)

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

    def create_setup_py(self, package_name_python):
        setup_py_template = self.get_file_contents('setup.py_template')
        var_list = []
        var_list.append((self.PACKAGE_NAME_VAR, self.internal_package.package_name))
        var_list.append((self.VERSION_VAR, '0.1'))
        var_list.append((self.AUTHOR_VAR, str(self.internal_package.owner.user)))
        var_list.append((self.DESCRIPTION_VAR, self.internal_package.description))
        var_list.append((self.URL_VAR, 'http://test'))
        var_list.append((self.AUTHOR_MAIL, self.experiment.owner.user.email))
        var_list.append((self.LICENSE_VAR, 'MIT'))
        var_list.append((self.PACKAGE_VAR, package_name_python))
        for var in var_list:
            setup_py_template = self.replace_variable_in_file(setup_py_template, var[0], var[1])
        self._create_new_file_in_repo('setup.py', commit_message='Added setup.py file', contents=setup_py_template)


class ExperimentGitRepoInit(GitRepoInit):

    PROJECTNAME_VAR = 'PROJECTNAME'
    STEPFOLDER_VAR = 'STEPFOLDER'
    AUTHOR_VAR = 'AUTHOR'

    def __init__(self, experiment, type='python'):
        gh = GitHubHelper(experiment.owner, experiment.git_repo.name)
        super().__init__(gh, type)
        self.experiment = experiment

    def init_repo_boilerplate(self):
        self.create_readme_file()
        self.create_requirements_and_init_file()
        self.create_travis_file()
        self.create_settings_file()
        self.create_test_runner_file()
        self.create_data_folder()
        self.create_step_folders()

    def create_requirements_and_init_file(self):
        self._create_new_file_in_repo('requirements.txt', 'Added requirements file')
        self._create_new_file_in_repo('__init__.py', 'Added init file')

    def create_step_folders(self):
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        for step in chosen_experiment_steps:
            name = step.folder_name()
            commit_message = 'Create folder {0}'.format(name)
            self.github_helper.add_file_to_repository('__init__.py', commit_message, name)
            self.create_main_and_test_file(name)

    def create_main_and_test_file(self, folder):
        main_contents = self.get_file_contents('main.py', part_of_step=True, folder=folder)
        project_name = self.github_helper.github_repository.name
        main_contents = self.replace_variable_in_file(main_contents, self.PROJECTNAME_VAR, project_name)
        main_contents = self.replace_variable_in_file(main_contents, self.STEPFOLDER_VAR, folder)
        main_contents = self.replace_variable_in_file(main_contents, self.AUTHOR_VAR, str(self.experiment.owner))
        self._create_new_file_in_repo('main.py', commit_message='Added main.py file', folder=folder, contents=main_contents)
        self._create_new_file_in_repo('tests.py', commit_message='Added test.py file', folder=folder, contents=self.get_file_contents('tests.py', part_of_step=True, folder=folder))

    def create_travis_file(self):
        self._create_new_file_in_repo('.travis.yml', 'Added Travis CI config', contents=self.get_file_contents('.travis.yml'))

    def create_settings_file(self):
        self._create_new_file_in_repo('settings.py', 'Added settings.py', contents=self.get_file_contents('settings.py'))

    def create_test_runner_file(self):
        self._create_new_file_in_repo('test_runner.py', 'Added test_runner.py', contents=self.get_file_contents('test_runner.py'))

    def create_readme_file(self):
        self._create_new_file_in_repo('README.md', 'Added README file', contents=self.get_file_contents('README.md'))

    def create_data_folder(self):
        self._create_new_file_in_repo('__init__.py', 'Added data folder', 'data')

