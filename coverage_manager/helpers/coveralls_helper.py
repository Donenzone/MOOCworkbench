import requests
import json

class CoverallsHelper(object):
    COVERALLS_URL = 'https://coveralls.io/github'

    def __init__(self, user, repo_name):
        self.user = user
        self.repo_name = repo_name
        self.url = '{0}/{1}/{2}.json'.format(self.COVERALLS_URL, self.user, self.repo_name)

    def code_coverage_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content)
            return json_dict['covered_percent']

    def coverage_enabled_check(self):
        response = requests.get(self.url)
        return response.status_code == 200

    def get_badge_url(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content)
            return json_dict['badge_url']
