from django.shortcuts import render
from rest_framework import viewsets
from GitManager.models import GitRepository
from GitManager.serializer import GitRepositorySerializer


# Create your views here.
class GitRepositoryViewSet(viewsets.ModelViewSet):
    queryset = GitRepository.objects.all().order_by('-created')
    serializer_class = GitRepositorySerializer
