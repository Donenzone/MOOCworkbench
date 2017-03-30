from .models import ExperimentMeasureResult, ExperimentMeasure

def get_measurement_messages_for_experiment(experiment):
    results = get_recent_measurements_for_all_types(experiment)
    message_list = [i.get_message() for i in results]
    if len(message_list) is 0:
        message_list.append('We don\'t know how you are doing yet. Check back later!')
    return message_list

def get_recent_measurements_for_all_types(experiment):
    measures = ExperimentMeasure.objects.all()
    measurement_list = []
    for measure in measures:
        recent_result = get_most_recent_measurement(experiment, measure)
        if recent_result:
            measurement_list.append(recent_result)
    return measurement_list

def get_most_recent_measurement(experiment, experiment_measure):
    result = ExperimentMeasureResult.objects.filter(experiment=experiment, measurement=experiment_measure).order_by('-created')
    if result.count() != 0:
        return result[0]
