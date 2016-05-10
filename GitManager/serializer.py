from rest_framework import serializers
from GitManager.models import *


class GitRepositorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GitRepository
        fields = ('url', 'title', 'git_url', 'subrepos',)