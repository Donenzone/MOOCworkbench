from datetime import datetime, timedelta

from ..models import ExperimentMeasure


def get_description_measure_list():
    descriptions = {}
    for experiment_measure in ExperimentMeasure.objects.all():
        measurement_slug = experiment_measure.slug()
        descriptions[measurement_slug] = experiment_measure.description
    return descriptions


def get_nr_of_commits_last_week(experiment):
    raw_values = []
    key_values = []
    today = datetime.now().date()
    current_day = datetime.now().date() - timedelta(7)
    while current_day <= today:
        end_of_current_day = current_day + timedelta(1)
        commits_on_this_day = experiment.git_repo.commits.filter(timestamp__range=(current_day, end_of_current_day))
        key_values.append(current_day)
        raw_values.append(commits_on_this_day.count())
        current_day += timedelta(1)
    return raw_values, key_values
