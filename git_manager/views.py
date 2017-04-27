from django.contrib.auth.decorators import login_required
from django.shortcuts import render


from user_manager.views import get_workbench_user
from git_manager.models import GitRepository
from git_manager.helpers.github_helper import GitHubHelper


@login_required
def index(request):
    return render(request, 'index.html')


def get_user_repositories(user):
    github_helper = GitHubHelper(user)
    github_api = github_helper.github_object
    if github_api:
        repo_list = []
        for repo in github_api.get_user().get_repos(type='owner'):
            repo_list.append((repo.name, repo.clone_url))
        return repo_list
    return []


def create_new_github_repository(title, user):
    github_helper = GitHubHelper(user, title, create=True)
    repo = github_helper.github_repository

    git_repo = GitRepository()
    git_repo.name = repo.name
    git_repo.owner = get_workbench_user(user)
    git_repo.github_url = repo.html_url
    git_repo.save()

    return git_repo
