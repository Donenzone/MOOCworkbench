from GitManager.github_helper import GitHubHelper

def get_github_helper(request, experiment):
    assert experiment.owner.user == request.user
    return GitHubHelper(request.user, experiment.git_repo.name)
