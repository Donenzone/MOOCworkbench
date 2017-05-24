import os
import logging
import subprocess
import os
import shutil
import pickle
from os.path import isfile, isdir

from sphinx.websupport import WebSupport

from pylint_manager.utils import activate_virtualenv, deactivate_virtualenv
from git_manager.helpers.git_helper import GitHelper

logger = logging.getLogger(__name__)


class SphinxHelper(object):
    GITHUB_REPO_FOLDER = 'github_repositories'
    UNDOC_PICKLE_LOCATION = '_build/coverage/undoc.pickle'

    def __init__(self, exp_or_package, folders, github_helper):
        """
        SphinxHelper helps with tasks related to document generation with Sphinx
        :param experiment: The package or experiment for which documents should be generated/managed
        :param folders: The relevant folders that where source files live in the exp/package (for an experiment, the steps)
        :param github_login: The GitHub username under which the git repository lives
        """
        self.owner = github_helper.owner
        self.github_helper = github_helper
        self.repo_name = exp_or_package.git_repo.name
        self.docs_src_location = exp_or_package.template.docs_src_location
        if not self.docs_src_location:
            self.docs_src_location = 'docs/'
        self.path = os.path.join(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name, self.docs_src_location)
        self.base_path = os.path.join(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.folders = folders

    def create_gh_page_branch(self):
        self.github_helper.create_branch('gh-pages')

    def build_gh_pages(self):
        git_helper = GitHelper(self.github_helper)
        git_helper.clone_or_pull_repository()
        git_helper.switch_to_branch('master')
        html_folder = os.path.join(git_helper.repo_dir, 'docs/_build/html')
        user_dir = git_helper.repo_dir_of_user()
        repo_dir = git_helper.repo_dir

        subprocess.call(['mv', html_folder, '.'], cwd=user_dir)
        subprocess.call(['git', 'pull'], cwd=repo_dir)
        subprocess.call(['git', 'checkout', 'gh-pages'], cwd=repo_dir)

        for file_name in os.listdir(repo_dir):
            if file_name != '.git':
                if isfile(os.path.join(repo_dir, file_name)):
                    os.remove(os.path.join(repo_dir, file_name))
                elif isdir(os.path.join(repo_dir, file_name)):
                    shutil.rmtree(os.path.join(repo_dir, file_name))

        for file_name in os.listdir(os.path.join(user_dir, 'html/')):
            subprocess.call(['mv', os.path.join(user_dir, 'html/', file_name), repo_dir])

        subprocess.call(['touch', '.nojekyll'], cwd=repo_dir)
        shutil.rmtree(os.path.join(user_dir, 'html/'))
        subprocess.call(['git', 'add', '.'], cwd=repo_dir)
        git_helper.commit('Updated docs')
        git_helper.push()

        git_helper = None
        shutil.rmtree(repo_dir)

    def get_coverage_data(self):
        coverage_pickle = '{0}{1}'.format(self.path, self.UNDOC_PICKLE_LOCATION)
        total_undocumented_functions = 0
        total_undocumented_classes = 0
        try:
            coverage_list = pickle.load(open(coverage_pickle, 'rb'))

            for coverage in coverage_list:
                for module_info in coverage.items():
                    if 'funcs' in module_info[1]:
                        funcs = module_info[1]['funcs']
                        total_undocumented_functions += len(funcs)
                    if 'classes' in module_info[1]:
                        classes = module_info[1]['classes']
                        total_undocumented_classes += len(classes)
            return coverage_list, total_undocumented_functions, total_undocumented_classes
        except IOError as e:
            logger.error("Coverage data not found for (%s, %s): %s", self.owner, self.repo_name, e)

    def _get_docs_dir(self):
        return '{0}/{1}/html/index.html'.format(self.owner, self.repo_name)

    def get_document(self, document_name):
        datadir = '{0}_build/html/data'.format(self.path)
        support = WebSupport(datadir=datadir)
        return support.get_document(document_name)
