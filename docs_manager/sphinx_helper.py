import subprocess
from MOOCworkbench.settings import STATICFILES_DIRS
from sphinx.websupport import WebSupport

class SphinxHelper(object):
    GITHUB_REPO_FOLDER = 'github_repositories'

    def __init__(self, experiment, steps, github_login):
        self.owner = github_login
        self.repo_name = experiment.git_repo.name
        self.path = '{0}/{1}/{2}/docs/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.base_path = '{0}/{1}/{2}/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.steps = steps

    def add_sphinx_to_repo(self):
        self._quickstart_sphinx()
        self._gen_docs_per_folder()
        self._prepend_to_conf_py()
        self._make_first_html()

    def _quickstart_sphinx(self):
        subprocess.call(['sphinx-quickstart', '-q', '-a', self.owner, '-v', '0.1', '-p', self.repo_name, self.path, '--ext-autodoc', '--ext-coverage'])

    def _gen_docs_per_folder(self):
        for step in self.steps:
            step_folder = '{0}{1}'.format(self.base_path, step.folder_name())
            subprocess.call(['sphinx-apidoc', '-o', self.path, step_folder])

    def _make_first_html(self):
        self._make_command('clean')
        self._make_command('html')

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

    def _make_command(self, command):
        subprocess.call(['make', '-C', self.path, command])

    def build_and_sync_docs(self):
        build_path = '{0}_build/html/'.format(self.path)
        support = WebSupport(srcdir=self.path,
                             builddir=build_path)
        support.build()

    def _get_docs_dir(self):
        return '{0}/{1}/html/index.html'.format(self.owner, self.repo_name)

    def get_document(self, document_name):
        datadir = '{0}_build/html/data'.format(self.path)
        support = WebSupport(datadir=datadir)
        return support.get_document(document_name)
