from django.template.defaultfilters import slugify

from helpers.helper import get_package_or_experiment
from pylint_manager.helper import return_result_summary_for_file

from git_manager.helpers.github_helper import GitHubHelper
from experiments_manager.models import Experiment


class ContentFile(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path


class RepoFileListMixin(object):
    def get_context_data(self, **kwargs):
        context = super(RepoFileListMixin, self).get_context_data(**kwargs)
        exp_or_package = get_package_or_experiment(self.request, self.object_type, self.kwargs['pk'])
        location = self._folder_location(exp_or_package)

        if self.is_folder(location):
            return self._files_in_folder(location, context, exp_or_package)
        else:
            return self._single_file(location, context, exp_or_package)

    def _folder_location(self, exp_or_package):
        if isinstance(exp_or_package, Experiment):
            return exp_or_package.get_active_step().location
        return '/'

    def _files_in_folder(self, location, context, exp_or_package):
        content_files = self._get_files_in_repository(self.request.user,
                                                      exp_or_package.git_repo.name,
                                                      location)
        if isinstance(exp_or_package, Experiment):
            context['git_list'] = self._add_static_results_to_files(exp_or_package, content_files)
        else:
            context['git_list'] = content_files
        return context

    def _single_file(self, location, context, exp_or_package):
        git_file = ContentFile(name=location, path=location)
        git_file.pylint_results = return_result_summary_for_file(exp_or_package,
                                                                 git_file.path)
        context['git_list'] = [git_file]
        return context


    def _add_static_results_to_files(self, experiment, content_files):
        for git_file in content_files:
            git_file.pylint_results = return_result_summary_for_file(experiment,
                                                                     git_file.path)
            git_file.slug = slugify(git_file.name)
        return content_files

    def _get_files_in_repository(self, user, repo_name, folder_name):
        github_helper = GitHubHelper(user, repo_name)
        return github_helper.list_files_in_folder(folder_name)

    def is_folder(self, location):
        return not '.' in location
