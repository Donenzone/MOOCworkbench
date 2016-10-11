import requests
from helpers.url_helper import build_url
from WorkerHelper.models import AbstractWorker
from rest_framework.renderers import JSONRenderer
# Create your models here.


class Worker(AbstractWorker):

    def submit(self, experiment_run):
        self.status = self.BUSY
        self.save()
        serializer = ExperimentRunSerializer(experiment_run)
        json = JSONRenderer().render(serializer.data)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        requests.post(build_url(self.location, ['api', 'experiment-run'], 'POST'), data=json, headers=headers)
