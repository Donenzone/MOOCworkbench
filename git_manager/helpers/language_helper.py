import os
import shutil

import requirements
from rpy2.robjects.packages import importr

from requirements_manager.models import Requirement
from requirements_manager.helper import delete_existing_requirements
from pylint_manager.utils import run_rlint, run_pylint
from .git_helper import GitHelper
from .github_helper import GitHubHelper


class LanguageHelper(object):
    def __init__(self, exp_or_package):
        self.exp_or_package = exp_or_package
        self.github_helper = GitHubHelper(self.exp_or_package.owner.user, self.exp_or_package.git_repo.name)

    def parse_requirements(self, requirements_file):
        pass

    def build_requirements_file(self):
        pass

    def write_requirements_file(self):
        pass

    def update_requirements(self):
        pass

    def get_requirements_file_location(self):
        pass

    def static_code_analysis(self):
        pass


class PythonHelper(LanguageHelper):

    def __init__(self, exp_or_package):
        LanguageHelper.__init__(self, exp_or_package)

    def parse_requirements(self, requirements_file):
        for req in requirements.parse(requirements_file):
            requirement = Requirement()
            requirement.package_name = req.name
            if req.specs:
                requirement.version = req.specs[0][1]
            requirement.save()

            self.exp_or_package.requirements.add(requirement)
            self.exp_or_package.save()

    def build_requirements_file(self):
        requirements_txt = ''
        for requirement in self.exp_or_package.requirements.all():
            requirements_txt += '{0}\n'.format(str(requirement))
        return requirements_txt

    def delete_requirement(self):
        pass

    def write_requirements_file(self):
        requirements_txt = self.build_requirements_file()
        self.github_helper.update_file('requirements.txt', 'Updated requirements.txt file by MOOC workbench',
                                  requirements_txt)

    def update_requirements(self):
        requirements_file = self.github_helper.view_file('requirements.txt')
        delete_existing_requirements(self.exp_or_package)
        self.parse_requirements(requirements_file)

    def get_requirements_file_location(self):
        return 'requirements.txt'

    def static_code_analysis(self):
        return run_pylint


class RHelper(LanguageHelper):
    def __init__(self, exp_or_package):
        LanguageHelper.__init__(self, exp_or_package)

    def parse_requirements(self, requirements_file):
        lines = requirements_file.split('\n')
        active_req = Requirement()
        for line in lines:
            active_req = self.parse_line_requirement(line, active_req)
            if active_req.package_name is not None and active_req.version is not None:
                active_req.save()
                self.exp_or_package.requirements.add(active_req)
                self.exp_or_package.save()
                active_req = Requirement()

    def parse_line_requirement(self, line, requirement):
        line_split = line.split(':')
        if len(line_split) > 1:
            if line_split[0] == 'Package':
                package_name = line_split[1]
                requirement.package_name = package_name
            elif line_split[0] == 'Version':
                version = line_split[1]
                requirement.version = version
        return requirement

    def write_requirements_file(self):
        self.build_requirements_file()

    def update_requirements(self):
        requirements_file = self.github_helper.view_file('src/packrat/packrat.lock')
        delete_existing_requirements(self.exp_or_package)
        self.parse_requirements(requirements_file)

    def _delete_requirements(self, git_helper):
        shutil.rmtree(os.path.join(git_helper.repo_dir, 'src/packrat'))

    def get_requirements_file_location(self):
        return 'src/packrat/packrat.lock'

    def static_code_analysis(self):
        return run_rlint

    def build_requirements_file(self):
        # clone repository
        git_helper = GitHelper(self.github_helper)
        git_helper.clone_or_pull_repository()
        self._delete_requirements(git_helper)

        # make src dir active
        os.chdir(git_helper.repo_dir + '/src/')

        # R cli install
        packrat = importr('packrat')
        packrat.init()
        utils = importr('utils')
        for requirement in self.exp_or_package.requirements.all():
            if requirement.package_name != 'packrat': # no need to install packrat
                utils.install_packages(requirement.package_name)
        packrat.snapshot()

        git_helper.commit('Updated dependencies in Packrat')
        git_helper.push()

