import json

import requests

from experiments_manager.helper import verify_and_get_experiment

from ..models import CodeCoverage


class CoverallsHelper(object):
    """Helper class for interacting with the Coveralls API"""
    COVERALLS_URL = 'https://coveralls.io/github'
    COVERAGE_URL = 'https://coveralls.io/builds/{0}/source.json?filename={1}'

    def __init__(self, user, repo_name):
        """Provide the GitHub user and repository name for which repo to provide coverage info
        :param user: GitHub username
        :param repo_name: GitHub repository name"""
        self.user = user
        self.repo_name = repo_name
        self.url = '{0}/{1}/{2}.json'.format(self.COVERALLS_URL, self.user, self.repo_name)

    def code_coverage_data(self):
        """Get general coverage data for this repository"""
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(str(response.content, encoding='utf8'))
            return json_dict['covered_percent']

    def coverage_enabled_check(self):
        """Check if code coverage is enabled
        :returns True if code coverage is enabled"""
        response = requests.get(self.url)
        return response.status_code == 200

    def get_badge_url(self):
        """Get the badge url from coveralls indicating coverage percentage"""
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content.decode('utf-8'))
            return json_dict['badge_url']

    def _get_file_coverage_url(self, commit_sha, file_name):
        """Get the URL for a specific file
        :param commit_sha: The SHA hash of a commit in this repository
        :param file_name: File name for which to retrieve coverage info"""
        return self.COVERAGE_URL.format(commit_sha, file_name)

    def _get_latest_commit_sha(self):
        """Get the SHA hash from the latest commit picked up by Coveralls"""
        response = requests.get(self.url)
        if response.status_code == 200:
            json_dict = json.loads(response.content.decode('utf-8'))
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


def coveralls_create(travis_instance):
    """Create new coveralls instance from travis instance"""
    new_coveralls = CodeCoverage(travis_instance=travis_instance)
    new_coveralls.save()

    return new_coveralls


def get_experiment_from_request_post(request):
    """Get an experiment from the request object
    Expects object_id present in request.POST
    (code coverage currently only for experiments, so no internalpackages)"""
    assert 'object_id' in request.POST
    experiment_id = request.POST['object_id']
    return verify_and_get_experiment(request, experiment_id)


def enable_coveralls(travis_instance):
    """
    Checks if code coverage object exists. If so, sets the enabled
    property to true, else creates a new one with default settings
    (where enabled is automatically true)
    :param travis_instance: The travis instance to check for
    :return: None
    """
    coverage_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    if coverage_config:
        coverage_config = coverage_config[0]
        coverage_config.enabled = True
        coverage_config.save()
    else:
        coverage_config = coveralls_create(travis_instance)
    return coverage_config
