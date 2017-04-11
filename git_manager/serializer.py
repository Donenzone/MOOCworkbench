from rest_framework import serializers
from git_manager.models import *


class GitRepositorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GitRepository
        fields = ('url', 'title', 'git_url', 'subrepos',)