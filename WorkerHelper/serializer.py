from rest_framework import serializers
from .models import AbstractWorker


def serializer_factory(worker_model):
    class WorkerSerializer(serializers.ModelSerializer):
        class Meta:
            model = worker_model
            fields = [x.name for x in AbstractWorker._meta.fields]

    return WorkerSerializer
