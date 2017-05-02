from quality_manager.models import ExperimentMeasureResult, ExperimentMeasure
from experiments_manager.helper import verify_and_get_experiment


class MeasurementMixin(object):

    def get_context_data(self, **kwargs):
        context = super(MeasurementMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])

        step = experiment.get_active_step()
        context['measurements'] = self._get_measurement_messages_for_experiment(step)
        return context

    def _get_measurement_messages_for_experiment(self, experiment):
        results = self._get_recent_measurements_for_all_types(experiment)
        message_list = [i.get_message() for i in results]
        if len(message_list) is 0:
            message_list.append('We don\'t know how you are doing yet. Check back later!')
        return message_list

    def _get_recent_measurements_for_all_types(self, step):
        measures = ExperimentMeasure.objects.all()
        measurement_list = []
        for measure in measures:
            recent_result = get_most_recent_measurement(step, measure)
            if recent_result:
                measurement_list.append(recent_result)
        return measurement_list


def get_recent_measurements_for_type(step, measure):
    recent_results = ExperimentMeasureResult.objects.filter(step=step,
                                                            measurement=measure).order_by('created')[:21]
    return recent_results


def get_most_recent_measurement(step, experiment_measure):
    if isinstance(experiment_measure, str):
        experiment_measure = ExperimentMeasure.objects.get(name=experiment_measure)
    result = ExperimentMeasureResult.objects.filter(step=step,
                                                    measurement=experiment_measure).order_by('-created')
    if result.count() != 0:
        return result[0]
