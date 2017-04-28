from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.github_helper import GitHubHelper


class RepoFileListMixin(object):
    def get_context_data(self, **kwargs):
        context = super(RepoFileListMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        context['git_list'] = self._get_files_in_repository(self.request.user,
                                                            experiment.git_repo.name,
                                                            self.step(experiment).location)
        return context

    def _get_files_in_repository(self, user, repo_name, folder_name):
        github_helper = GitHubHelper(user, repo_name)
        return github_helper.list_files_in_folder(folder_name)
