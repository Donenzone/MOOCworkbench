from django.shortcuts import render
from rest_framework import viewsets
from GitManager.models import GitRepository
from GitManager.serializer import GitRepositorySerializer
from .Modules import Git

# Create your views here.
class GitRepositoryViewSet(viewsets.ModelViewSet):
    queryset = GitRepository.objects.all().order_by('-created')
    serializer_class = GitRepositorySerializer


def index(request):
    Git.create_new_repository('test', 'Python')
    return render(request, 'index.html')