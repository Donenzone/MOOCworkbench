import logging
import requests


from travispy import TravisPy
from travispy.errors import TravisError


logger = logging.getLogger(__name__)


class TravisCiHelper(object):
    def __init__(self, github_helper):
        self.github_helper = github_helper
        self.travis = TravisPy.github_auth(self.github_helper.socialtoken)
        self.travis_user = self.travis.user()
        self.repo_slug = self.get_repo_slug()
        self.travis_repo = self.travis.repo(self.repo_slug)

    def enable_travis_for_repository(self):
        self.travis_repo.enable()

    def disable_travis_for_repository(self):
        self.travis_repo.disable()

    def trigger_build_for_repo(self):
        repo_slug_2f = self.get_repo_slug(two_f=True)
        url = 'https://api.travis-ci.org/repo/{0}/requests'.format(repo_slug_2f)
        body = '{"request": {"branch":"master"} }'
        access_token = self.get_access_token()
        auth_token = 'token {0}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Travis-API-Version': '3', 'Authorization': auth_token}
        response = requests.post(url, data=body, headers=headers)
        logger.debug('build triggered for repo %s, travis response: %s', self.repo_slug, response.content)

    def get_access_token(self):
        headers = {'Content-Type': 'application/json', 'User-Agent': 'TravisMOOCworkbench', 'Accept': 'application/vnd.travis-ci.2+json'}
        response = requests.post('https://api.travis-ci.org/auth/github', headers=headers, params={"github_token": self.github_helper.socialtoken})
        contents = response.json()
        return contents['access_token']

    def get_repo_slug(self, two_f=False):
        if two_f:
            return '{0}%2F{1}'.format(self.travis_user.login, self.github_helper.github_repository.name)
        return '{0}/{1}'.format(self.travis_user.login, self.github_helper.github_repository.name)

    def get_log_for_last_build(self):
        try:
            build = self.travis.build(self.travis_repo.last_build_id)
            log = build.jobs[0].log.body
            return log
        except TravisError as e:
            logger.error('could not retrieve log of last build for %s', self.repo_slug)
            return 'Log not found'
