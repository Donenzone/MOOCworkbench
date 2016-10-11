from rest_framework import serializers


def serializer_experiment_run_factory(experiment_run_model):
    class ExperimentRunSerializer(serializers.ModelSerializer):
        class Meta:
            model = experiment_run_model
            fields = ('status', 'experiment', 'created', 'owner', 'output', 'selected_worker')

    return ExperimentRunSerializer