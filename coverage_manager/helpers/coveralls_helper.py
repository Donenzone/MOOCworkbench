import requests
import json


class CoverallsHelper(object):
    COVERALLS_URL = 'https://coveralls.io/github'
    COVERAGE_URL = 'https://coveralls.io/builds/{0}/source.json?filename={1}'

    def __init__(self, user, repo_name):
        self.user = user
        self.repo_name = repo_name
        self.url = '{0}/{1}/{2}.json'.format(self.COVERALLS_URL, self.user, self.repo_name)

    def code_coverage_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(str(response.content, encoding='utf8'))
            return json_dict['covered_percent']

    def coverage_enabled_check(self):
        response = requests.get(self.url)
        return response.status_code == 200

    def get_badge_url(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content.decode('utf-8'))
            return json_dict['badge_url']

    def _get_file_coverage_url(self, commit_sha, file_name):
        return self.COVERAGE_URL.format(commit_sha, file_name)

    def _get_latest_commit_sha(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content)
            return json_dict['commit_sha']

    def get_file_coverage(self, file_name):
        """
        Get file coverage for file from Coveralls API.
    
        :param file_name: File_name with folder for file for which coverage needs to be checked.
        :return: 
        Coverage in percentage rounded to two decimals.
        -1 if Coveralls returns anything other then status code 200
        0 if file is empty.
        """
        commit_sha = self._get_latest_commit_sha()
        file_coverage_url = self._get_file_coverage_url(commit_sha, file_name)
        response = requests.get(file_coverage_url)
        if response.status_code == 200:
            coverage_list = json.loads(response.content.decode('utf-8'))
            coverage_list_filter = [x for x in coverage_list if x is not None]
            nr_of_lines_covered = len([x for x in coverage_list_filter if x == 1])
            nr_of_lines = len(coverage_list_filter)
            if nr_of_lines != 0:
                coverage = nr_of_lines_covered / nr_of_lines
                return "{0:.2f}".format(coverage*100)
            else:
                return 0
        return -1
