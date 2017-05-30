"""Cookiecutter_manager tests """
import os
import shutil

from django.test import TestCase
from django.core.management import call_command


from .models import CookieCutterTemplate

from .helpers.helper_cookiecutter import clone_cookiecutter_template, \
    clone_cookiecutter_template_with_dict


class CookieCutterTemplateTestCases(TestCase):
    """Test if cookiecutter managers can be cloned"""
    def setUp(self):
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        self.cookiecutter_template = CookieCutterTemplate.objects.create(
            location='https://github.com/jlmdegoede/cookiecutter-data-science.git',
            name='Default data science template',
            language_id=1,
            docs_src_location='docs/')
        self.folder_location = 'test_cookiecutter/'
        os.mkdir(self.folder_location)
        self.project_name_1 = 'test_project/'
        self.project_name_2 = 'test_project_second/'

    def test_clone_cookiecutter(self):
        """Test cloning a cookiecutter template with pre-defined vars"""
        clone_cookiecutter_template(self.cookiecutter_template, self.folder_location,
                                    self.project_name_1, 'MOOC workbench')
        self.assertTrue(os.path.exists(os.path.join(self.folder_location, self.project_name_1)))

    def test_clone_cookiecutter_with_dict(self):
        """Test cloning a cookiecutter template with a dictionary of vars"""
        cookiecutter_vars = {'project_name': self.project_name_2, 'author_name': 'MOOC workbench',
                             'repo_name': self.project_name_2, 'description': 'Cloning test'}
        clone_cookiecutter_template_with_dict(self.cookiecutter_template, self.folder_location, cookiecutter_vars)
        self.assertTrue(os.path.exists(os.path.join(self.folder_location, self.project_name_2)))

    def tearDown(self):
        project_path_one = os.path.join(self.folder_location, self.project_name_1)
        if os.path.exists(project_path_one):
            shutil.rmtree(project_path_one)
        project_path_two = os.path.join(self.folder_location, self.project_name_2)
        if os.path.exists(project_path_two):
            shutil.rmtree(project_path_two)
        shutil.rmtree(self.folder_location)
