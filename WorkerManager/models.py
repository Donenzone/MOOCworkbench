import requests
from helpers.url_helper import build_url
from WorkerHelper.models import AbstractWorker
# Create your models here.


class Worker(AbstractWorker):

    def submit(self, experiment_git_repo_url, repo_name, run_id):
        data = {'git_url': experiment_git_repo_url, 'repo_name': repo_name, 'run_id': run_id}
        response = requests.post(build_url(self.location, ['worker', 'submit'], 'POST'), data=data)
        self.status = self.BUSY
        self.save()
        return response
