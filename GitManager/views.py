from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .models import GitRepository, GitHubAuth
from UserManager.models import WorkbenchUser
from GitManager.serializer import GitRepositorySerializer
from django.shortcuts import render, redirect, HttpResponse
from .Modules import Git
import requests
from django.utils.crypto import get_random_string
from github import Github

CLIENT_ID = '1697609f631820ff6ad3'
CLIENT_SECRET = 'd466715a419f4f5511b2ad0575b3f9466c88176e'


# Create your views here.
class GitRepositoryViewSet(viewsets.ModelViewSet):
    queryset = GitRepository.objects.all().order_by('-created')
    serializer_class = GitRepositorySerializer


@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def authorize_github(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    nr_of_github = GitHubAuth.objects.filter(workbench_user=workbench_user).count()

    github_auth = GitHubAuth(state=get_random_string(length=32), workbench_user=workbench_user)
    github_auth.save()
    return redirect(
        to='https://github.com/login/oauth/authorize?client_id=' + CLIENT_ID + '&state=' +
           github_auth.state + '&scope=repo read:repo_hook' + '&redirect_uri=https://mooc.jochem.xyz/github-callback/')


def get_user_repositories(user):
    workbench_user = WorkbenchUser.objects.get(user=user)
    git_auth = GitHubAuth.objects.get(workbench_user=workbench_user)
    g = Github(git_auth.auth_token)

    repo_list = []
    for repo in g.get_user().get_repos(type='owner'):
        repo_list.append(repo.name)
    return repo_list


@login_required
@csrf_exempt
def callback_authorization_github(request):
    if request.method == 'GET':
        workbench_user = WorkbenchUser.objects.get(user=request.user)
        code = request.GET['code']
        state = request.GET['state']
        github_auth = GitHubAuth.objects.filter(state=state, workbench_user=workbench_user)

        if github_auth.count() != 0 and state == github_auth[0].state:
            github_auth = github_auth[0]
            github_auth.code = code
            github_auth.save()
            data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'code': github_auth.code,
                    'redirect_uri': 'https://mooc.jochem.xyz/github-callback/', 'state': github_auth.state}
            response = requests.post('https://github.com/login/oauth/access_token', data=data)
            print(response.content.decode("utf-8"))
            splitted_response = response.content.decode("utf-8").split('=')
            access_token = splitted_response[1].split('&scope')[0]

            github_auth.auth_token = access_token
            github_auth.save()
            return redirect(to='/')


def create_new_repository(repository_name, user, type):
    if repository_name and user:
        Git.create_new_repository(repository_name, user, type)
    else:
        return Exception("Repository name and/or username empty!")
