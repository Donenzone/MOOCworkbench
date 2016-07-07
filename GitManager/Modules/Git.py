from git import Repo
from MOOCworkbench.settings import BASE_DIR


def create_new_repository(repository_name, user, type):
    path = BASE_DIR + '/' + user + '/bare_repos/' + repository_name
    bare_repo = Repo.init(path, bare=True)
    clone_bare_repo(repository_name, bare_repo, user)


def clone_bare_repo(repository_name, repo, user):
    cloned_repo = repo.clone(BASE_DIR + '/' + user + '/' + repo.working_dir)

    # write base file
    file_name = 'main.py'
    open(cloned_repo.working_dir + '/' + file_name, 'a').close()

    # commit and push base file
    cloned_repo.index.add([file_name])
    cloned_repo.index.commit("Initial commit by MOOC workbench")
    cloned_repo.remote().push()
