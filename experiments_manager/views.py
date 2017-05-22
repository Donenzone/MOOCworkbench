import json
from datetime import datetime

from django.views.generic.detail import DetailView
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.views.generic.edit import UpdateView

from docs_manager.mixins import DocsMixin
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.mixins.repo_file_list import get_files_for_steps, _get_files_in_repository
from git_manager.views import get_user_repositories
from quality_manager.mixins import get_most_recent_measurement
from pylint_manager.helper import return_results_for_file
from recommendations.utils import get_recommendations

from .tables import ExperimentTable
from .forms import ExperimentForm, ExperimentEditForm
from .models import *
from .helper import verify_and_get_experiment, get_readme_of_experiment
from .mixins import ExperimentContextMixin
from .tasks import initialize_repository


class ExperimentDetailView(DocsMixin, ExperimentPackageTypeMixin, DetailView):
    model = Experiment
    template_name = "experiments_manager/experiment_detail/experiment_detail.html"

    def get_context_data(self, **kwargs):
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        self.object_type = self.get_requirement_type(experiment)
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        context['steps'] = get_files_for_steps(experiment, only_active=True)
        context['object_type'] = self.object_type
        if not experiment.completed:
            active_step = experiment.get_active_step()
            context['active_step_id'] = active_step.id
            context['final_step'] = experiment.get_active_step().step_nr == experiment.chosenexperimentsteps_set.count()
            context['recommendations'] = get_recommendations(active_step)
        context['index_active'] = True
        return context


class ExperimentCreateView(View):
    def get(self, request, experiment_id=0):
        try:
            form = ExperimentForm()
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_create/experiment_new.html", {'form': form,
                                                                                    'experiment_id': experiment_id,
                                                                                    'repository_list': repository_list})
        except ValueError as a:
            messages.add_message(request, messages.INFO, 'Before creating an experiment, please connect with GitHub')
            return redirect(to=reverse('view_my_profile'))

    def post(self, request, experiment_id=0):
        experiment = Experiment()
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            cookiecutter = form.cleaned_data['template']
            experiment.language = cookiecutter.language
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            initialize_repository.delay(experiment.id, cookiecutter.id)
            return redirect(to=reverse('experiment_status_create'))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_create/experiment_new.html",
                          {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


@login_required
def experiment_status_create(request):
    return render(request, 'experiments_manager/experiment_create/experiment_status_create.html', {})


@login_required
def experiment_first_time(request, pk):
    experiment = verify_and_get_experiment(request, pk)
    context = {}
    context['object'] = experiment
    context['object_type'] = ExperimentPackageTypeMixin.EXPERIMENT_TYPE
    context['object_id'] = experiment.pk
    context['configured'] = experiment.travis.enabled
    context['username'] = experiment.git_repo.owner
    context['reposlug'] = experiment.git_repo.name
    context['travis'] = experiment.travis
    context['coverage_configured'] = experiment.docs.enabled
    return render(request, 'experiments_manager/experiment_create/experiment_enable_builds.html', context)


class FileListForStep(View):
    def get(self, request):
        assert 'experiment_id' in request.GET
        assert 'step_id' in request.GET

        step_id = request.GET['step_id']
        experiment_id = request.GET['experiment_id']
        experiment = verify_and_get_experiment(request, experiment_id)

        step = get_object_or_404(ChosenExperimentSteps, pk=step_id)
        file_list = _get_files_in_repository(request.user, experiment.git_repo.name, step.location)
        return_dict = []
        for content_file in file_list:
            return_dict.append((content_file.name, content_file.type))
        return JsonResponse({'files': return_dict})


class ChooseExperimentSteps(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(ChooseExperimentSteps, self).get(request, experiment_id)
        context['steps'] = ExperimentStep.objects.all()
        return render(request, "experiments_manager/experiment_create/experimentsteps_choose.html", context)

    def post(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        step_json_list = json.loads(request.POST['steplist'])
        counter = 1
        if step_json_list:
            delete_existing_chosen_steps(experiment)
            cookiecutter = experiment.template
            for step in step_json_list:
                step = int(step)
                step = ExperimentStep.objects.get(id=step)
                chosen_experiment_step = ChosenExperimentSteps(experiment=experiment, step=step, step_nr=counter)
                if counter == 1:
                    chosen_experiment_step.active = True
                    chosen_experiment_step.started_at = datetime.now()
                cookiecutter_location = cookiecutter.folder_file_locations.get(step=step)
                chosen_experiment_step.location = cookiecutter_location.location
                chosen_experiment_step.main_module = cookiecutter_location.main_module
                chosen_experiment_step.save()
                counter += 1
            url = reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()})
            return JsonResponse({'url': url})
        else:
            return JsonResponse({'message': 'Choose at least one step'})


class FileViewGitRepository(ExperimentContextMixin, View):

    def get(self, request, experiment_id):
        context = super(FileViewGitRepository, self).get(request, experiment_id)
        file_name = request.GET['file_name']
        context['file_name'] = file_name
        experiment = verify_and_get_experiment(request, experiment_id)
        github_helper = GitHubHelper(request.user, experiment.git_repo.name)
        content_file = github_helper.view_file(file_name)
        pylint_results = return_results_for_file(experiment, file_name)
        context['content_file'] = self.add_pylint_results_to_content(pylint_results, content_file)
        return render(request, 'experiments_manager/file_detail.html', context)

    def add_pylint_results_to_content(self, pylint_results, content_file):
        counter = 0
        new_content_file_str = ''
        for line in content_file.split('\n'):
            pylint_for_line = pylint_results.filter(line_nr=counter)
            if pylint_for_line:
                new_content_file_str += "{0}\n".format(line)
                for pylint_line in pylint_for_line:
                    new_content_file_str += '<span class="nocode" id="{0}style">{1}</span>'.format(pylint_line.pylint_type,
                                                                                                     pylint_line.message)
            else:
                new_content_file_str += line + '\n'
            counter += 1
        return new_content_file_str


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner).order_by('-created')
    table = ExperimentTable(experiments)
    return render(request, 'experiments_manager/experiments_table.html', {'table': table})


@login_required
def complete_step_and_go_to_next(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    active_step = ChosenExperimentSteps.objects.filter(experiment=experiment, active=True)
    if active_step:
        active_step = active_step[0]
        active_step.active = False
        active_step.completed = True
        active_step.completed_at = datetime.now()
        active_step.save()
        next_step_nr = active_step.step_nr + 1
        next_step = ChosenExperimentSteps.objects.filter(experiment=experiment, step_nr=next_step_nr)
        if next_step.count() != 0:
            next_step = next_step[0]
            next_step.active = True
            next_step.save()
            return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))
    return redirect(to=reverse('experiment_publish', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))


@login_required
def experiment_publish(request, pk, slug):
    experiment = verify_and_get_experiment(request, pk)
    experiment.completed = True
    experiment.save()
    return render(request, 'experiments_manager/experiment_publish.html', {'experiment': experiment})


@login_required
def experiment_generate_uuid_and_make_public(request, pk, slug):
    experiment = verify_and_get_experiment(request, pk)
    if not experiment.unique_id:
        experiment.unique_id = get_random_string(32)
        experiment.public = True
        experiment.save()
        # create github release
        github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
        tag_name = 'release_{0}'.format(experiment.unique_id)
        git_release = github_helper.create_release(tag_name=tag_name, name=experiment.title,
                                     body='This is an automatically created release by the MOOC workbench',
                                     pre_release=False)
        experiment.publish_url_zip = git_release.html_url
        # https://github.com/PyGithub/PyGithub/pull/522#pullrequestreview-22171287
        # once merged and released, change this to zipball_url pls kthxby
        experiment.save()
    return redirect(to=reverse('experiment_readonly', kwargs={'unique_id': experiment.unique_id}))


class ExperimentReadOnlyView(DocsMixin, ExperimentPackageTypeMixin, DetailView):
    model = Experiment
    template_name = "experiments_manager/experiment_detail/experiment_readonly.html"

    def get_object(self, queryset=None):
        return Experiment.objects.get(unique_id=self.kwargs['unique_id'])

    def get_context_data(self, **kwargs):
        experiment = self.object
        self.object_type = self.get_requirement_type(experiment)
        context = super(ExperimentReadOnlyView, self).get_context_data(**kwargs)
        context['steps'] = get_files_for_steps(experiment)
        context['object_type'] = self.object_type
        context['object_id'] = experiment.pk
        context['completed'] = True
        context['object_list'] = self.object.requirements.all()
        context['data_schema_list'] = self.object.schema.fields.all()
        context['readme'] = get_readme_of_experiment(self.object)
        context['experiment_id'] = self.object.id
        return context


class ExperimentEditView(UpdateView):
    model = Experiment
    form_class = ExperimentEditForm
    template_name = 'experiments_manager/experiment_edit.html'

    def get_form(self, form_class=None):
        form_instance = super(ExperimentEditView, self).get_form(form_class)
        form_instance.initial = {'title': self.object.title,
                                 'description': self.object.description,
                                 'github_url': self.object.git_repo.github_url}
        return form_instance

    def get_context_data(self, **kwargs):
        context = super(ExperimentEditView, self).get_context_data(**kwargs)
        context['settings_active'] = True
        return context

    def form_valid(self, form):
        git_repo = self.object.git_repo
        git_repo.github_url = form.cleaned_data['github_url']
        git_repo.save()
        messages.add_message(self.request, messages.SUCCESS, 'Changes saved successfully.')
        return super(ExperimentEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('experiment_edit', kwargs={'pk': self.object.id})


@login_required
def experimentstep_scorecard(request, pk, slug):
    experiment = verify_and_get_experiment(request, pk)
    completed_step = experiment.get_active_step()
    context = {}

    context['completed_step'] = completed_step
    context['experiment'] = experiment

    testing_results = get_most_recent_measurement(completed_step, 'Testing')
    context['testing'] = testing_results

    docs_results = get_most_recent_measurement(completed_step, 'Documentation')
    context['docs'] = docs_results

    ci_results = get_most_recent_measurement(completed_step, 'Use of CI')
    context['ci'] = ci_results

    vcs_results = get_most_recent_measurement(completed_step, 'Version control use')
    context['vcs'] = vcs_results

    dependency_results = get_most_recent_measurement(completed_step, 'Dependencies defined')
    context['dependency'] = dependency_results

    pylint_results = get_most_recent_measurement(completed_step, 'Static code analysis')
    context['pylint'] = pylint_results

    context['final_step'] = experiment.chosenexperimentsteps_set.count() == experiment.get_active_step().step_nr

    return render(request, 'experiments_manager/experiment_scorecard.html', context)


@login_required
def readme_of_experiment(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    content_file = get_readme_of_experiment(experiment)
    return render(request, 'experiments_manager/experiment_detail/experiment_readme.html', {'readme': content_file,
                                                                                            'object': experiment,
                                                                                            'readme_active': True})


@login_required
def experiment_issues(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    context = {'object': experiment, 'object_type': experiment.get_object_type(), 'issues_active': True}
    context['issues'] = github_helper.get_issues()
    return render(request, 'experiments_manager/experiment_detail/experiment_issues.html', context)


@login_required
def experiment_single_issue(request, experiment_id, issue_nr):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    issue = github_helper.get_single_issue(int(issue_nr))
    return JsonResponse({'contents': issue.body, 'title': issue.title})
