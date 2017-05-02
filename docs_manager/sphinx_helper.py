import subprocess
import pickle

from sphinx.websupport import WebSupport


class SphinxHelper(object):
    GITHUB_REPO_FOLDER = 'github_repositories'
    UNDOC_PICKLE_LOCATION = '_build/coverage/undoc.pickle'

    def __init__(self, experiment, folders, github_login):
        """
        SphinxHelper helps with tasks related to document generation with Sphinx
        :param experiment: The package or experiment for which documents should be generated/managed
        :param folders: The relevant folders that where source files live in the exp/package (for an experiment, the steps)
        :param github_login: The GitHub username under which the git repository lives
        """
        self.owner = github_login
        self.repo_name = experiment.git_repo.name
        self.path = '{0}/{1}/{2}/docs/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.base_path = '{0}/{1}/{2}/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.folders = folders

    def add_sphinx_to_repo(self):
        """
        Add Sphinx to an existing repository.
        Assumes that this repository has already been cloned.
        :return: 
        """
        self._quickstart_sphinx()
        self._gen_docs_per_folder()
        self._prepend_to_conf_py()
        self._make_first_html()

    def _quickstart_sphinx(self):
        subprocess.call(['sphinx-quickstart', '-q', '-a', self.owner, '-v', '0.1', '-p', self.repo_name,
                         self.path, '--ext-autodoc', '--ext-coverage'])

    def _gen_docs_per_folder(self):
        for folder in self.folders:
            folder_path = '{0}{1}'.format(self.base_path, folder)
            subprocess.call(['sphinx-apidoc', '-o', self.path, folder_path])

    def _make_first_html(self):
        self._make_command('clean')
        self._make_command('html', 'coverage')

    def _prepend_to_conf_py(self):
        file_path = '{0}conf.py'.format(self.path)

        with open(file_path, 'r+') as conf_file:
            contents = conf_file.read()
            new_contents = 'import os\nimport sys\nsys.path.insert(0, os.path.abspath(\'../\'))\n' + contents
            conf_file.close()

        if new_contents:
            conf_file = open(file_path, 'w')
            conf_file.write(new_contents)
            conf_file.close()

    def _make_command(self, command, arg=None):
        if arg:
            subprocess.call(['make', '-C', self.path, command, arg])
        else:
            subprocess.call(['make', '-C', self.path, command])

    def build_and_sync_docs(self):
        """
        After a pull, run this function to rebuild the docs.
        
        :return: 
        """
        build_path = '{0}_build/html/'.format(self.path)
        support = WebSupport(srcdir=self.path,
                             builddir=build_path)
        support.build()

    def update_coverage(self):
        build_path = '{0}_build/coverage/'.format(self.path)
        subprocess.call(['sphinx-build', '-v', '-b', 'coverage', self.path, build_path])

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
        except IOError as e:
            raise "Coverage data not found: {0}".format(e)
        return coverage_list, total_undocumented_functions, total_undocumented_classes

    def _get_docs_dir(self):
        return '{0}/{1}/html/index.html'.format(self.owner, self.repo_name)

    def get_document(self, document_name):
        datadir = '{0}_build/html/data'.format(self.path)
        support = WebSupport(datadir=datadir)
        return support.get_document(document_name)
