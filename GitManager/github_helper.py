from github import Github
from github.GithubException import GithubException
from allauth.socialaccount.models import SocialToken
from UserManager.models import get_workbench_user, WorkbenchUser

class GitHubHelper(object):
    def __init__(self, user, repo_name = None, create=False):
        self.github_object = self.get_github_object(user)
        self.github_user = self.github_object.get_user()
        
        if create:
            self.github_repository = self.create_new_repository()
        elif repo_name:
            self.github_repository = self.github_user.get_repo(repo_name)
            self.repo_name = repo_name

    def get_github_object(self, user):
        if isinstance(user, WorkbenchUser):
            user = user.user
        socialtoken = SocialToken.objects.filter(account__user=user, account__provider='github')
        if socialtoken.count() != 0:
            return Github(login_or_token=socialtoken[0].token)
        else: return None

    def list_files_in_repo(self, folder=''):
        try:
            repo = self.github_repository
            return repo.get_contents('/{0}'.format(folder))
        except GithubException as e:
            return [e.data['message']]

    def view_file_in_repo(self, file_name):
        pass

    def list_files_in_repo_folder(self, folder):
        pass

    def get_commits_in_repository(self, since):
        return self.github_repository.get_commits(since=since)

    def get_repo_file_name(self, file_name, folder=''):
        if folder:
            repo_file_name = '/{0}/{1}'.format(folder, file_name)
        else:
            repo_file_name = '/{0}'.format(file_name)
        return repo_file_name

    def add_file_to_repository(self, file_name, commit_message, folder='', contents=''):
        try:
            repo_file_name = self.get_repo_file_name(self.github_repository, file_name, folder)
            self.github_repository.create_file(repo_file_name, commit_message, contents)
        except GithubException as e:
            print(e)

    def create_new_repository(self):
        return self.github_user.create_repo(self.repo_name)

    def update_file_in_repository(self, file_name, commit_message, contents, folder=''):
        repo_file_name = self.get_repo_file_name(file_name, folder)
        current_file = self.github_repository.get_file_contents(repo_file_name)
        self.github_repository.update_file(repo_file_name, commit_message, contents, current_file.sha)
