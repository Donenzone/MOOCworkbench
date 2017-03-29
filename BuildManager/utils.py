from travispy import TravisPy
from GitManager.github_helper import GitHubHelper
import requests, json

def enable_travis_for_repository(github_helper):
    t = TravisPy.github_auth(github_helper.socialtoken)
    travis_user = t.user()
    repo_slug = get_repo_slug(github_helper, travis_user)
    travis_repo = t.repo(repo_slug)
    travis_repo.enable()

def trigger_build_for_repo(github_helper):
    t = TravisPy.github_auth(github_helper.socialtoken)
    travis_user = t.user()
    url = 'https://api.travis-ci.org/repo/{0}/requests'.format(get_repo_slug(github_helper, travis_user, two_f=True))
    body='{"request": {"branch":"master"} }'
    access_token = get_access_token(github_helper.socialtoken)
    auth_token = 'token {0}'.format(access_token)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Travis-API-Version': '3', 'Authorization': auth_token}
    r = requests.post(url, data=body, headers=headers)

def get_access_token(github_token):
    headers = {'User-Agent': 'TravisMOOCworkbench', 'Accept': 'application/vnd.travis-ci.2+json'}
    response = requests.post('https://api.travis-ci.org/auth/github', headers=headers, params={
            "github_token": github_token,
        })
    contents = response.json()
    return contents['access_token']

def get_repo_slug(github_helper, travis_user, two_f=False):
    if two_f:
        return '{0}%2F{1}'.format(travis_user.login, github_helper.github_repository.name)
    return '{0}/{1}'.format(travis_user.login, github_helper.github_repository.name)
