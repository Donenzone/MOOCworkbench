from experiments_manager.helper import verify_and_get_experiment
from pylint_manager.helper import return_result_summary_for_file

from git_manager.helpers.github_helper import GitHubHelper


class RepoFileListMixin(object):
    def get_context_data(self, **kwargs):
        context = super(RepoFileListMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        content_files = self._get_files_in_repository(self.request.user,
                                                            experiment.git_repo.name,
                                                            self.step(experiment).location)

        for git_file in content_files:
            git_file.pylint_results = return_result_summary_for_file(experiment, git_file.path)
        context['git_list'] = content_files
        return context

    def _get_files_in_repository(self, user, repo_name, folder_name):
        github_helper = GitHubHelper(user, repo_name)
        return github_helper.list_files_in_folder(folder_name)
