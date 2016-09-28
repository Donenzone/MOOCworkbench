import os
import shutil


def get_worker_repository_folder_path(repository_name):
    return 'RunManager/gitrepositories/{0}'.format(repository_name)


def check_if_existing_worker_repository(repository_name):
    return os.path.isdir(get_worker_repository_folder_path(repository_name))


def remove_if_existing_worker_repository(repository_name):
    if check_if_existing_worker_repository(repository_name):
        shutil.rmtree(get_worker_repository_folder_path(repository_name))