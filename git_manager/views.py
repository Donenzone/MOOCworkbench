from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .models import GitRepository
from user_manager.models import WorkbenchUser
from git_manager.serializer import GitRepositorySerializer
from django.shortcuts import render, redirect, HttpResponse
from user_manager.models import get_workbench_user
import requests
from django.utils.crypto import get_random_string
from github import Github
from allauth.socialaccount.models import SocialToken
from .github_helper import *

# Create your views here.
class GitRepositoryViewSet(viewsets.ModelViewSet):
    queryset = GitRepository.objects.all().order_by('-created')
    serializer_class = GitRepositorySerializer


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


def create_new_github_repository_local(title, user, type, experiment):
    github_helper = GitHubHelper(user, title, create=True)
    repo = github_helper.github_repository

    git_repo = GitRepository()
    git_repo.name = repo.name
    git_repo.owner = get_workbench_user(user)
    git_repo.github_url = repo.html_url
    git_repo.save()

    return git_repo
