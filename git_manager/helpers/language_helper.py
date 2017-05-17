import os
import shutil
import subprocess

import requirements
from rpy2.robjects.packages import importr

from MOOCworkbench.settings import PROJECT_ROOT
from docs_manager.sphinx_helper import SphinxHelper
from requirements_manager.models import Requirement
from requirements_manager.helper import delete_existing_requirements
from pylint_manager.utils import run_rlint, run_pylint
from marketplace.utils import internalpackage_publish_update, internalpackage_remove

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

    def cookiecutter_dict(self, internal_package):
        pass

    def publish_package(self):
        pass

    def remove_package(self):
        pass

    def get_document(self, document_name):
        pass

    def generate_documentation(self):
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

    def cookiecutter_dict(self, internal_package):
        return {'project_name': self.exp_or_package.name,
                'app_name': self.github_helper.repo_name,
                'full_name': self.exp_or_package.owner,
                'email': self.exp_or_package.owner.user.email,
                'github_username': self.github_helper.owner,
                'project_short_description': internal_package.description}

    def publish_package(self):
        internalpackage_publish_update(self.exp_or_package)

        self.exp_or_package.published = True
        self.exp_or_package.save()

    def remove_package(self):
        internalpackage_remove(self.exp_or_package)

        self.exp_or_package.published = False
        self.exp_or_package.save()

    def generate_documentation(self):
        git_helper = GitHelper(self.github_helper)
        git_helper.clone_or_pull_repository()
        folders = self.exp_or_package.get_docs_folder()
        sphinx_helper = SphinxHelper(self.exp_or_package, folders, self.github_helper.owner)
        sphinx_helper.add_sphinx_to_repo()
        sphinx_helper.build_and_sync_docs()

    def get_document(self, document_name):
        from experiments_manager.helper import get_steps
        steps = get_steps(self.exp_or_package)
        sphinx_helper = SphinxHelper(self.exp_or_package, steps, self.github_helper.owner)
        return sphinx_helper.get_document(document_name)


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
        old_active_dir = os.getcwd()
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
        os.chdir(old_active_dir)

    def cookiecutter_dict(self, internalpackage):
        dependencies = self.exp_or_package.requirements.all()
        depency_str = ''
        for dependency in dependencies:
            depency_str += '{0} (>= {1}), '.format(dependency.package_name, dependency.version)

        return {'author_name': self.exp_or_package.owner,
                'email': self.exp_or_package.owner.user.email,
                'github_username': self.github_helper.owner,
                'project_name': internalpackage.name,
                'description': internalpackage.description,
                'short_description': internalpackage.description,
                'depends': depency_str}

    def generate_documentation(self):
        from marketplace.models import InternalPackage
        if isinstance(self.exp_or_package, InternalPackage):
            self._devtools_document()

    def publish_package(self):
        self._devtools_document()

        self.exp_or_package.published = True
        self.exp_or_package.save()

    def remove_package(self):
        # R packages are installed directly from GitHub
        # so removing is "impossible"
        self.exp_or_package.published = False
        self.exp_or_package.save()

    def get_document(self, document_name):
        from marketplace.models import InternalPackage
        if isinstance(self.exp_or_package, InternalPackage):
            manual_file = 'man/{0}.Rd'.format(document_name)
            manual_contents = self.github_helper.view_file(manual_file)
            temp_file = self._temp_save_rd_file(manual_contents)
            self._convert_rd_to_txt(temp_file)
            self._del_tmp_file(temp_file)
            return
        else:
            return self.github_helper.view_file(document_name)

    def _devtools_document(self):
        git_helper = GitHelper(self.github_helper)
        git_helper.clone_or_pull_repository()

        old_active_dir = os.getcwd()
        os.chdir(git_helper.repo_dir + '/R/')

        devtools = importr('devtools')
        devtools.document()

        git_helper.commit('Published package and generated docs')
        git_helper.push()
        os.chdir(old_active_dir)

    def _temp_save_rd_file(self, manual):
        file_name = 'temp/temp{0}.Rd'.format(str(self.exp_or_package.pk))
        temp = open(file_name, 'w')
        temp.write(manual)
        temp.close()
        return file_name

    def _convert_rd_to_txt(self, rd_file):
        rd_file_path = os.path.join(PROJECT_ROOT, rd_file)
        p = subprocess.run(['R', 'CMD', 'Rdconv', '-t', 'txt', rd_file_path],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        result = p.stdout.decode('utf-8')
        return result

    def _del_tmp_file(self, file_name):
        os.remove(file_name)

