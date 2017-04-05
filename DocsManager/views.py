from django.shortcuts import render
from DocsManager.sphinx_helper import SphinxHelper
from ExperimentsManager.helper import verify_and_get_experiment
from ExperimentsManager.helper import get_steps
from django.contrib.auth.decorators import login_required
from GitManager.github_helper import GitHubHelper


@login_required
def view_doc_of_experiment(request, experiment_id, page_slug=None):
    experiment = verify_and_get_experiment(request, experiment_id)
    steps = get_steps(experiment)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    sphinx_helper = SphinxHelper(experiment, steps, github_helper.github_repository.owner.login)
    if page_slug:
        document = sphinx_helper.get_document(page_slug)
    else:
        document = sphinx_helper.get_document('index')
    return render(request, 'DocsManager/docs_template.html', {'document': document, 'experiment': experiment})


@login_required
def docs_status(request, experiment_id):
    pass
