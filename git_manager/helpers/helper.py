from git_manager.helpers.github_helper import GitHubHelper


def get_github_helper(request, exp_or_package):
    assert exp_or_package.owner.user == request.user
    return GitHubHelper(request.user, exp_or_package.git_repo.name)
