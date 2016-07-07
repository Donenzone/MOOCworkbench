from git import Repo
from MOOCworkbench.settings import BASE_DIR
from os import listdir

REPOSITORY_FOLDER = 'gitrepositories'
BASE_REPO_FOLDER = 'bare_repos'


def create_new_repository(repository_name, user, type):
    try:
        path = '{0}/{1}/{2}/{3}/{4}'.format(BASE_DIR, REPOSITORY_FOLDER, user, BASE_REPO_FOLDER, repository_name)
        bare_repo = Repo.init(path, bare=True)
        return clone_bare_repo(repository_name, bare_repo, user, type)
    except Exception as e:
        return "Could not create new repo: {0}".format(e)


def clone_bare_repo(repository_name, repo, user, type):
    path = '{0}/{1}/{2}/{3}'.format(BASE_DIR, REPOSITORY_FOLDER, user, repository_name)
    cloned_repo = repo.clone(path)

    # write base file
    file_name = '{0}/main.py'.format(cloned_repo.working_dir)
    open(file_name, 'a').close()

    # commit and push base file
    cloned_repo.index.add([file_name])
    cloned_repo.index.commit("Initial commit by MOOC workbench")
    cloned_repo.remote().push()


def add_submodule_to_repo(repository_name, user):
    Exception("Not implemented yet!")


def list_files_in_repo(repository_name, user):
    # check if this user repository exists
    Exception("Not implemented yet!")


def list_git_commits(repository_name, user):
    Exception("Not implemented yet!")


def view_file_in_repo(file_path, user):
    Exception("Not implemented yet!")