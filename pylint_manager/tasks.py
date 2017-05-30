from MOOCworkbench.celery import app
from git_manager.helpers.helper import get_exp_or_package_from_repo_name


@app.task
def task_run_pylint(repository_name):
    experiment = get_exp_or_package_from_repo_name(repository_name)
    language_helper = experiment.language_helper()
    language_helper.static_code_analysis()(experiment)
