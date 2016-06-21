from git import Repo
from MOOCworkbench.settings import BASE_DIR


def create_new_repository(repository_name, type):
    bare_repo = Repo.init(BASE_DIR + '/' + repository_name, bare=True)


