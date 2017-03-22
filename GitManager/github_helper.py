from github import Github, GithubException
from allauth.socialaccount.models import SocialToken
from UserManager.models import get_workbench_user, WorkbenchUser

def get_github_object(user):
    if isinstance(user, WorkbenchUser):
        user = user.user
    socialtoken = SocialToken.objects.filter(account__user=user, account__provider='github')
    if socialtoken.count() != 0:
        return Github(login_or_token=socialtoken[0].token)
    else: return None

def get_user_information(github_object):
    return github_object.get_user()

def get_repository(user, repository_name):
    github_object = get_github_object(user)
    assert github_object is not None
    github_user = get_user_information(github_object)
    repo = github_user.get_repo(repository_name)
    return repo

def list_files_in_repo(user, repository_name, folder=''):
    try:
        repo = get_repository(user, repository_name)
        return repo.get_contents('/{0}'.format(folder))
    except GithubException as e:
        return [e.data['message']]

def view_file_in_repo(user, repository_name, file_name):
    pass

def list_files_in_repo_folder(user, repository_name, folder):
    pass

def commits_in_repository(user, repository_name):
    pass

def add_file_to_repository(user, repository_name, file_name, commit_message, folder='', contents=''):
    repo = get_repository(user, repository_name)
    if folder:
        repo_file_name = '/{0}/{1}'.format(folder, file_name)
    else:
        repo_file_name = '/{0}'.format(file_name)
    repo.create_file(repo_file_name, commit_message, contents)

def create_new_github_repository(name, user):
    github_api = get_github_object(user)
    github_user = github_api.get_user()
    repo = user.create_repo(name, auto_init=True)
    return repo
