import subprocess
from MOOCworkbench.settings import STATICFILES_DIRS
class SphinxHelper(object):
    GITHUB_REPO_FOLDER = 'github_repositories'

    def __init__(self, experiment, steps, github_login):
        self.owner = github_login
        self.repo_name = experiment.git_repo.name
        self.path = '{0}/{1}/{2}/docs/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.base_path = '{0}/{1}/{2}/'.format(self.GITHUB_REPO_FOLDER, self.owner, self.repo_name)
        self.steps = steps

    def add_sphinx_to_repo(self):
        self.quickstart_sphinx()
        self.gen_docs_per_folder()
        self.prepend_to_conf_py()
        self.make_first_html()

    def quickstart_sphinx(self):
        subprocess.call(['sphinx-quickstart', '-q', '-a', self.owner, '-v', '0.1', '-p', self.repo_name, self.path, '--ext-autodoc', '--ext-coverage'])

    def gen_docs_per_folder(self):
        for step in self.steps:
            step_folder = '{0}{1}'.format(self.base_path, step.folder_name())
            subprocess.call(['sphinx-apidoc', '-o', self.path, step_folder])

    def make_first_html(self):
        self.make_command('clean')
        self.make_command('html')

    def prepend_to_conf_py(self):
        file_path = '{0}conf.py'.format(self.path)

        with open(file_path, 'r+') as conf_file:
            contents = conf_file.read()
            new_contents = 'import os\nimport sys\nsys.path.insert(0, os.path.abspath(\'../\'))\n' + contents
            conf_file.close()

        if new_contents:
            conf_file = open(file_path, 'w')
            conf_file.write(new_contents)
            conf_file.close()

    def make_command(self, command):
        subprocess.call(['make', '-C', self.path, command])

    def sync_docs_with_static(self):
        static_dir = STATICFILES_DIRS[0]
        static_user_dir = '{0}/{1}/'.format(static_dir, self.owner)
        subprocess.call(['mkdir', static_user_dir])
        static_dir_to_cp = '{0}{1}/'.format(static_user_dir, self.repo_name)
        subprocess.call(['mkdir', static_dir_to_cp])
        build_path = '{0}_build/html/'.format(self.path)
        subprocess.call(['cp', '-R', build_path, static_dir_to_cp])

    def get_docs_dir(self):
        return '{0}/{1}/html/index.html'.format(self.owner, self.repo_name)
