from django.template.defaultfilters import slugify

from experiments_manager.helper import verify_and_get_experiment
from pylint_manager.helper import return_result_summary_for_file

from git_manager.helpers.github_helper import GitHubHelper

class ContentFile(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path


class RepoFileListMixin(object):
    def get_context_data(self, **kwargs):
        context = super(RepoFileListMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        active_location = self.step(experiment).location
        if self.is_folder(active_location):
            content_files = self._get_files_in_repository(self.request.user,
                                                                experiment.git_repo.name,
                                                                active_location)

            for git_file in content_files:
                git_file.pylint_results = return_result_summary_for_file(experiment,
                                                                         git_file.path)
                git_file.slug = slugify(git_file.name)
            context['git_list'] = content_files
            return context
        else:
            context['git_list'] = [ContentFile(name=active_location, path=active_location)]
            return context

    def _get_files_in_repository(self, user, repo_name, folder_name):
        github_helper = GitHubHelper(user, repo_name)
        return github_helper.list_files_in_folder(folder_name)

    def is_folder(self, location):
        return not '.' in location