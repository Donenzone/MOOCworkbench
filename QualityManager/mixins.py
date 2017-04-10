from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from ExperimentsManager.helper import verify_and_get_experiment

class MeasurementMixin(object):

    def get_context_data(self, **kwargs):
        context = super(MeasurementMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        context['measurements'] = self._get_measurement_messages_for_experiment(experiment)
        return context

    def _get_measurement_messages_for_experiment(self, experiment):
        results = self._get_recent_measurements_for_all_types(experiment)
        message_list = [i.get_message() for i in results]
        if len(message_list) is 0:
            message_list.append('We don\'t know how you are doing yet. Check back later!')
        return message_list

    def _get_recent_measurements_for_all_types(self, experiment):
        measures = ExperimentMeasure.objects.all()
        measurement_list = []
        for measure in measures:
            recent_result = self._get_most_recent_measurement(experiment, measure)
            if recent_result:
                measurement_list.append(recent_result)
        return measurement_list

    def get_recent_measurements_for_type(self, experiment, measure):
        recent_results = ExperimentMeasureResult.objects.filter(experiment=experiment, measurement=measure).order_by('created')[:21]
        return recent_results

    def _get_most_recent_measurement(self, experiment, experiment_measure):
        result = ExperimentMeasureResult.objects.filter(experiment=experiment, measurement=experiment_measure).order_by('-created')
        if result.count() != 0:
            return result[0]
