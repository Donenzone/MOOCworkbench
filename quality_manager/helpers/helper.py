from ..models import ExperimentMeasure


def get_description_measure_list():
    descriptions = {}
    for experiment_measure in ExperimentMeasure.objects.all():
        measurement_slug = experiment_measure.slug()
        descriptions[measurement_slug] = experiment_measure.description
    return descriptions
