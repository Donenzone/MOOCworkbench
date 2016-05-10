from rest_framework import serializers
from GitManager.models import *


class WorkbenchUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkbenchUser
        fields = ('url', 'username', 'emailaddress', 'netid', 'can_run_experiments')