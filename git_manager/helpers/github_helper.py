from github import Github
from github.GithubException import GithubException
from allauth.socialaccount.models import SocialToken
from user_manager.models import WorkbenchUser
import base64


class GitHubHelper(object):
    def __init__(self, user, repo_name=None, create=False):
        self.user = self._get_user(user)

        self.socialtoken = self._get_social_token()
        self.github_object = self._get_github_object()
        self.github_user = self.github_object.get_user()

        if repo_name:
            self.repo_name = repo_name

        if create:
            self.github_repository = self._create_new_repository()
        elif repo_name is not None:
            self.github_repository = self.github_user.get_repo(repo_name)

    @property
    def owner(self):
        return self.github_repository.owner.login

    def get_clone_url(self):
        clone_url = self.github_repository.clone_url
        remaining_clone_url = clone_url.split('https://')[1]
        return 'https://{0}@{1}'.format(self.socialtoken, remaining_clone_url)

    def list_files_in_folder(self, folder=''):
        try:
            if not folder.startswith('/'):
                folder = '/{0}'.format(folder)
            return self.github_repository.get_contents(folder)
        except GithubException as e:
            return [e.data['message']]

    def view_file(self, file_name):
        try:
            encoded = self.github_repository.get_file_contents(file_name)
            decoded = base64.b64decode(encoded.content).decode("utf-8")
            return decoded
        except GithubException as e:
            print([e.data['message']])

    def get_commits_in_repository(self, since):
        return self.github_repository.get_commits(since=since)

    def add_file_to_repository(self, file_name, commit_message, folder='', contents=''):
        try:
            repo_file_name = self._get_repo_file_name(file_name, folder)
            self.github_repository.create_file(repo_file_name, commit_message, contents)
        except GithubException as e:
            print(e)

    def update_file(self, file_name, commit_message, contents, folder=''):
        repo_file_name = self._get_repo_file_name(file_name, folder)
        current_file = self.github_repository.get_file_contents(repo_file_name)
        self.github_repository.update_file(repo_file_name, commit_message, contents, current_file.sha)

    def create_release(self, tag_name, name, body, pre_release):
        self.github_repository.create_git_release(tag_name, name, body, prerelease=pre_release)

    def _get_repo_file_name(self, file_name, folder=''):
        return '/{0}/{1}'.format(folder, file_name) if folder else '/{0}'.format(file_name)

    def _create_new_repository(self):
        return self.github_user.create_repo(self.repo_name)

    def _get_github_object(self):
        return Github(login_or_token=self.socialtoken)

    def _get_user(self, user):
        if isinstance(user, WorkbenchUser):
            return user.user
        return user

    def _get_social_token(self):
        socialtoken = SocialToken.objects.filter(account__user=self.user, account__provider='github')
        if socialtoken.count() != 0:
            return socialtoken[0].token
        raise ValueError('SocialToken is missing')
