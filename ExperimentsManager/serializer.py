from rest_framework import serializers
from ExperimentsManager.models import *


class ScriptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Script
        fields = ('url', 'title', 'description', 'version', 'type')


class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Experiment
        fields = ('url', 'title', 'description', 'version', 'type')
