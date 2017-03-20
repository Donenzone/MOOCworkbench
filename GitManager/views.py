from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .models import GitRepository
from UserManager.models import WorkbenchUser
from GitManager.serializer import GitRepositorySerializer
from django.shortcuts import render, redirect, HttpResponse
from .modules.Gitolite import Gitolite
from .modules.Git import GitRepo
from UserManager.models import get_workbench_user
import requests
from django.utils.crypto import get_random_string
from github import Github
from allauth.socialaccount.models import SocialToken

# Create your views here.
class GitRepositoryViewSet(viewsets.ModelViewSet):
    queryset = GitRepository.objects.all().order_by('-created')
    serializer_class = GitRepositorySerializer


@login_required
def index(request):
    return render(request, 'index.html')


def get_github_object(user):
    workbench_user = get_workbench_user(user)
    socialtoken = SocialToken.objects.filter(account__user=user, account__provider='github')
    if socialtoken.count() != 0:
        return Github(login_or_token=socialtoken[0].token)
    else: return None


def get_user_repositories(user):
    github_api = get_github_object(user)
    if github_api:
        repo_list = []
        for repo in github_api.get_user().get_repos(type='owner'):
            repo_list.append((repo.name, repo.clone_url))
        return repo_list
    return []

def create_new_github_repository(title, user, type, experiment):
    github_api = get_github_object(user)
    user = github_api.get_user()
    repo = user.create_repo(title)
    print(repo)

def list_files_in_repo(repository_name, user):
    if repository_name and user:
        git_repo = GitRepo(repository_name, user, 'python')
        return git_repo.list_files_in_repo()
    else:
        return Exception("Repository name and/or username is empty!")


def view_file_in_repo(repository_name, file_name, user):
    if repository_name and user and file_name:
        git_repo = GitRepo(repository_name, user, 'python')
        return git_repo.view_file_in_repo(file_name)
    else:
        return Exception("Repository name and/or username is empty!")


def list_files_in_repo_folder(repository_name, user, folder):
    if repository_name and user:
        git_repo = GitRepo(repository_name, user, 'python')
        return git_repo.list_files_in_repo_folder(folder)


def commits_in_repository(repository_name, user):
    if repository_name and user:
        git_repo = GitRepo(repository_name, user, 'python')
        return git_repo.list_git_commits()
    else:
        return Exception("Repository name and/or username is empty!")
