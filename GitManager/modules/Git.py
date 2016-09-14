from git import Repo
from MOOCworkbench.settings import BASE_DIR
from os import listdir, path
from .modules import Gitolite, GitoliteRepo

REPOSITORY_FOLDER = 'gitrepositories'
BASE_REPO_FOLDER = 'bare_repos'


class GitRepo():

    def __init__(self, repository_name, user, type='python'):
        self.repository_name = repository_name
        self.user = user
        self.type = type
        self.gitolite = Gitolite()
        self.gitolite_repo = None
        self.PATH = '{0}/{1}/{2}/{3}'.format(BASE_DIR, REPOSITORY_FOLDER, self.user, self.repository_name)
        self.BARE_PATH = '{0}/{1}/{2}/{3}/{4}'.format(BASE_DIR, REPOSITORY_FOLDER, user, BASE_REPO_FOLDER, repository_name)
        if path.isdir(self.PATH):
            self.repo = Repo(self.PATH)

    def create_new_repository(self):
        self.gitolite_repo = self.gitolite.add_repo(self.repository_name, self.user)
        
    def clone_bare_repo(self, repo):
        self.repo = repo.clone(self.PATH)

        # write base file
        file_name = '{0}/main.py'.format(self.repo.working_dir)
        open(file_name, 'a').close()

        # commit and push base file
        self.repo.index.add([file_name])
        self.repo.index.commit("Initial commit by MOOC workbench")
        self.repo.remote().push()

    def commit(files, commit_message):
        self.repo.index.add(files)
        self.repo.index.commit(commit_message)

    def push():
        self.repo.remote().push()

    def add_submodule_to_repo(self):
        Exception("Not implemented yet!")

    def list_files_in_repo(self):
        # check if this user repository exists
        file_list = []
        for obj in self.repo.tree():
            file_list.append({'file': obj.name, 'hash': obj, 'isdir': path.isdir('{0}/{1}'.format(self.PATH, obj.name))})
        return file_list

    def list_git_commits(self):
        commit_list = []
        for commit in self.repo.iter_commits():
            commit_list.append({'date': commit.authored_date, 'author': commit.author, 'hash': commit.hexsha, 'message': commit.message})
        return commit_list

    def view_file_in_repo(self, file_name):
        tree = self.repo.tree()
        blob = tree / file_name
        data = blob.data_stream.read()
        return data

    def list_files_in_repo_folder(self, folder_name):
        tree = self.repo.tree()
        folder = tree / folder_name
        file_list = []
        for obj in folder:
            file_list.append({'file': obj.name, 'hash': obj, 'isdir': path.isdir('{0}/{1}'.format(self.PATH, obj.name))})
        return file_list
