from django.test import TestCase
from .models import Experiment
from UserManager.models import WorkbenchUser
from django.contrib.auth.models import User
from django.test import Client


class ExperimentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.create(netid='jlmdegoede', user=self.user)
        self.experiment = Experiment.objects.create(title='Experiment', description='test', version='1.0', owner=self.workbench_user)

    def test_index_not_signed_in(self):
        c = Client()
        response = c.get('/experiments/')
        self.assertEqual(response.status_code, 302)

    def test_index_signed_in(self):
        c = Client()
        c.login(username='test', password='test')
        response = c.get('/experiments/')
        self.assertIsNotNone(response.context['table'])