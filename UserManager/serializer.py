from rest_framework import serializers
from GitManager.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email',)


class WorkbenchUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkbenchUser
        fields = ('url', 'user', 'netid', 'can_run_experiments')