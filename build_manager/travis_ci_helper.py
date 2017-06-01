"""TravisCiHelper module"""
import logging

import requests
from travispy import TravisPy
from travispy.errors import TravisError

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TravisCiHelper(object):
    """Travis CI helper provides functions to interact with Travis CI API through TravisPy
    You can use thise module given a GitHubHelper to enable or disable Travis for that GitHub repository,
    trigger a build and get the last log of a build."""

    def __init__(self, github_helper):
        """":param github_helper: A GitHubHelper instance for the repository on which you want to enable Travis"""
        self.github_helper = github_helper
        self.travis = TravisPy.github_auth(self.github_helper.socialtoken)
        self.travis_user = self.travis.user()
        self.repo_slug = self._get_repo_slug()
        self.travis_repo = self.travis.repo(self.repo_slug)

    def enable_travis_for_repository(self):
        """Enable Travis CI for the repository"""
        return self.travis_repo.enable()

    def disable_travis_for_repository(self):
        """Disable Travis CI for the repository"""
        return self.travis_repo.disable()

    def trigger_build_for_repo(self):
        """Trigger a build for this repository"""
        repo_slug_2f = self._get_repo_slug(two_f=True)
        url = 'https://api.travis-ci.org/repo/{0}/requests'.format(repo_slug_2f)
        body = '{"request": {"branch":"master"} }'
        access_token = self._get_access_token()
        auth_token = 'token {0}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Travis-API-Version': '3',
                   'Authorization': auth_token}
        response = requests.post(url, data=body, headers=headers)
        if response.status_code == 202:
            logger.info('build triggered for repo %s, travis response: %s', self.repo_slug, response.content)
            return True
        else:
            return False

    def get_log_for_last_build(self):
        """Retrieve the last log for Travis CI.
        If retrieving failed, returns Log not found"""
        try:
            build = self.travis.build(self.travis_repo.last_build_id)
            log = build.jobs[0].log.body
            return log
        except TravisError:
            logger.error('could not retrieve log of last build for %s', self.repo_slug)
            return 'Log not found'

    def get_last_build_status(self):
        build = self.travis.build(self.travis_repo.last_build_id)
        return build.passed

    def _get_access_token(self):
        headers = {'Content-Type': 'application/json', 'User-Agent': 'TravisMOOCworkbench',
                   'Accept': 'application/vnd.travis-ci.2+json'}
        response = requests.post('https://api.travis-ci.org/auth/github', headers=headers,
                                 params={"github_token": self.github_helper.socialtoken})
        contents = response.json()
        return contents['access_token']

    def _get_repo_slug(self, two_f=False):
        if two_f:
            return '{0}%2F{1}'.format(self.travis_user.login, self.github_helper.github_repository.name)
        return '{0}/{1}'.format(self.travis_user.login, self.github_helper.github_repository.name)
