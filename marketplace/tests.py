from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.shortcuts import reverse
from django.core.management import call_command

from user_manager.models import WorkbenchUser
from experiments_manager.models import Experiment, ChosenExperimentSteps
from git_manager.models import GitRepository
from marketplace.models import ExternalPackage, InternalPackage
from marketplace.models import PackageVersion, Language, Category
from helpers.helper import ExperimentPackageTypeMixin
from docs_manager.models import Docs
from build_manager.models import TravisInstance


class MarketplaceTestCase(TestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/steps.json', verbosity=0)
        call_command('loaddata', 'fixtures/measures.json', verbosity=0)
        call_command('loaddata', 'fixtures/package_categories_languages.json', verbosity=0)
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)

        self.user = User.objects.create_user('test', 'test@test.nl', 'test')
        self.workbench_user = WorkbenchUser.objects.get(user=self.user)

        self.second_user = User.objects.create_user('test2', 'test@test.nl', 'test2')
        self.git_repo = GitRepository.objects.create(name='Experiment', owner=self.workbench_user, github_url='https://github')
        self.experiment = Experiment.objects.create(title='Experiment',
                                                    description='test',
                                                    owner=self.workbench_user,
                                                    git_repo=self.git_repo,
                                                    language_id=1,
                                                    template_id=2)
        self.language = Language.objects.first()
        self.category = Category.objects.first()

        self.chosen_step = ChosenExperimentSteps.objects.create(step_id=1, experiment_id=1, step_nr=1)

        self.internal_package = InternalPackage.objects.create(name='Package',
                                                               description='Package',
                                                               git_repo=self.git_repo,
                                                               language_id=1,
                                                               category_id=1,
                                                               owner_id=1)
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_post_save_new_internal_package(self):
        """
        During setUp a new InternalPackage is created,
        this test ensures that also a TravisCiConfig, PackageVersion
        and Docs instances are created.
        """
        package_version = PackageVersion.objects.filter(id=1)
        self.assertTrue(package_version)
        docs = Docs.objects.filter(id=1)
        self.assertTrue(docs)
        travis = TravisInstance.objects.filter(id=1)
        self.assertTrue(travis)

    def test_marketplace_index_not_signed_in(self):
        """
        Test to ensure the marketplace index is only accessible
        for signed in users
        """
        c = Client()
        response = c.get(reverse('marketplace_index'))
        self.assertEqual(response.status_code, 302)

    def test_marketplace_index(self):
        """
        Test to ensure that the Marketplace index
        loads for signed in users
        """
        response = self.client.get(reverse('marketplace_index'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['new_packages'])
        self.assertIsNotNone(response.context['new_internal_packages'])
        self.assertIsNotNone(response.context['recent_updates'])
        self.assertIsNotNone(response.context['recent_resources'])

    def test_empty_package_list_view(self):
        """
        Test to ensure the package list loads
        """
        response = self.client.get(reverse('package_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['object_list'])

    def test_create_external_package_get(self):
        """
        Test to ensure the page for creating an external page
        loads successfully
        """
        response = self.client.get(reverse('package_new'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_create_external_package_post(self):
        external_package_data = {'name': 'My new package',
                                 'description': 'Desc.',
                                 'project_page': 'http://test.nl',
                                 'category': '1',
                                 'language': '1'}
        response = self.client.post(reverse('package_new'), data=external_package_data)
        self.assertEqual(response.status_code, 302)
        external_package = ExternalPackage.objects.filter(id=2)
        self.assertTrue(external_package)

    def test_create_external_package_post_invalid_url(self):
        external_package_data = {'name': 'My new package',
                                 'description': 'Desc.',
                                 'project_page': 'http://test',
                                 'category': '1',
                                 'language': '1'}
        response = self.client.post(reverse('package_new'), data=external_package_data)
        self.assertEqual(response.status_code, 200)
        external_package = ExternalPackage.objects.filter(id=2)
        self.assertFalse(external_package)

    def test_create_internal_package_get(self):
        response = self.client.get(reverse('internalpackage_create', kwargs={'experiment_id': 1, 'step_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('marketplace.views.PackageGitRepoInit')
    def test_create_internal_package_post(self, mock_package_repo_init):

        internal_package_data = {'name': 'My new package',
                                 'description': 'Desc',
                                 'category': '1',
                                 'language': '1'
                                 }
        mock_package_repo_init.return_value = RepoInitMock(self.git_repo)
        response = self.client.post(reverse('internalpackage_create', kwargs={'experiment_id': 1, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 302)
        internal_package = InternalPackage.objects.filter(id=2)
        self.assertTrue(internal_package)

    def test_create_internal_package_post_missing_data(self):
        internal_package_data = {'name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internalpackage_create', kwargs={'experiment_id': 1, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=2)
        self.assertFalse(internal_package)

    def test_create_internal_package_post_missing_experiment_id(self):
        internal_package_data = {'name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internalpackage_create', kwargs={'experiment_id': 0, 'step_id': 1}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=2)
        self.assertFalse(internal_package)

    def test_create_internal_package_post_missing_step_id(self):
        internal_package_data = {'name': 'My new package',
                                 'description': 'Desc',
                                 }
        response = self.client.post(reverse('internalpackage_create', kwargs={'experiment_id': 1, 'step_id': 0}),
                                    data=internal_package_data)
        self.assertEqual(response.status_code, 200)
        internal_package = InternalPackage.objects.filter(id=2)
        self.assertFalse(internal_package)

    def test_internal_package_dashboard(self):
        response = self.client.get(reverse('internalpackage_dashboard', kwargs={'pk': 1}))
        package = InternalPackage.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['docs'])
        self.assertEqual(response.context['object'], package)
        self.assertEqual(response.context['object_type'], ExperimentPackageTypeMixin.PACKAGE_TYPE)
        self.assertIsNotNone(response.context['edit_form'])

    def test_internal_package_detail(self):
        response = self.client.get(reverse('package_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['version_history'])
        self.assertIsNotNone(response.context['resources'])

    def test_internalpackage_edit_post(self):
        """
        Test if edit page for internal package can save
        (Note: this view has no template and is embedded in the dashboard)
        """
        internalpackage_data = {'name': '23u4892', 'description': 'New Desc', 'category': 1, 'language': 1}
        response = self.client.post(reverse('internalpackage_update', kwargs={'pk': 1}), data=internalpackage_data)
        self.assertEqual(response.status_code, 302)
        internalpackage = InternalPackage.objects.filter(name='23u4892')
        self.assertTrue(internalpackage)

    def test_packageversion_create_get(self):
        """
        Test http get on view creating new package version,
        asserts if context contains form.
        """
        response = self.client.get(reverse('packageversion_new', kwargs={'package_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    def test_packageversion_create_post(self):
        """
        Test creating package version with all required fields.
        """
        package_version_data = {'version_nr': 'v0.2', 'changelog': 'New stuff', 'url': 'https://test.test'}
        response = self.client.post(reverse('packageversion_new', kwargs={'package_id': 1}), data=package_version_data)
        self.assertEqual(response.status_code, 302)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertTrue(new_package_version)

    def test_packageversion_create_post_no_changelog(self):
        """
        Test creating package version without changelog,
        should fail because changelog is required.
        """
        package_version_data = {'version_nr': 'v0.2', 'url': 'https://test.test'}
        response = self.client.post(reverse('packageversion_new', kwargs={'package_id': 1}), data=package_version_data)
        self.assertEqual(response.status_code, 200)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertFalse(new_package_version)

    def test_packageversion_create_post_no_url(self):
        """
        Test creating package version without url to new version,
        should fail because url is required.
        """
        package_version_data = {'version_nr': 'v0.2', 'changelog': 'New stuff',}
        response = self.client.post(reverse('packageversion_new', kwargs={'package_id': 1}), data=package_version_data)
        self.assertEqual(response.status_code, 200)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertFalse(new_package_version)

    def test_internalpackageversion_create_get(self):
        """
        Test to ensure that getting the page for creating a new
        internalpackage version loads successfully.
        """
        response = self.client.get(reverse('internalpackageversion_new', kwargs={'package_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])

    @patch('marketplace.views.create_tag_for_package_version')
    @patch('marketplace.views.update_setup_py_with_new_version')
    def test_internalpackageversion_create_post(self, mock_tag, mock_update_setup_py):
        """
        Test to ensure that creating a new packageversion for an internalpackage is possible.
        """
        mock_tag.return_value = None
        mock_update_setup_py.return_value = None
        packageversion_data = {'version_nr': '0.2', 'pre_release': 1, 'changelog': 'My changes'}
        response = self.client.post(reverse('internalpackageversion_new', kwargs={'package_id': 1}), data=packageversion_data)
        self.assertEqual(response.status_code, 302)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertTrue(new_package_version)
        self.assertTrue(new_package_version[0].pre_release)

    @patch('marketplace.views.create_tag_for_package_version')
    @patch('marketplace.views.update_setup_py_with_new_version')
    def test_internalpackageversion_create_post_no_version_nr(self, mock_tag, mock_update_setup_py):
        """
        Test creating new internal package version with missing version_nr,
        creating should fail.
        """
        mock_tag.return_value = None
        mock_update_setup_py.return_value = None
        packageversion_data = {'pre_release': 1, 'changelog': 'My changes'}
        response = self.client.post(reverse('internalpackageversion_new', kwargs={'package_id': 1}), data=packageversion_data)
        self.assertEqual(response.status_code, 200)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertFalse(new_package_version)

    @patch('marketplace.views.create_tag_for_package_version')
    @patch('marketplace.views.update_setup_py_with_new_version')
    def test_internalpackageversion_create_post(self, mock_tag, mock_update_setup_py):
        """
        Test creating new internal package version with missing pre_release bool,
        creating should pass with default pre_release value (False).
        """
        mock_tag.return_value = None
        mock_update_setup_py.return_value = None
        packageversion_data = {'version_nr': '0.2', 'changelog': 'My changes'}
        response = self.client.post(reverse('internalpackageversion_new', kwargs={'package_id': 1}), data=packageversion_data)
        self.assertEqual(response.status_code, 302)
        new_package_version = PackageVersion.objects.filter(id=2)
        self.assertTrue(new_package_version)
        self.assertFalse(new_package_version[0].pre_release)

    def test_packageresource_create_get(self):
        """
        Test to ensure that the page for creating packageresource loads.
        """
        response = self.client.get(reverse('packageresource_new', kwargs={'package_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])



class RepoInitMock(object):
    def __init__(self, git_repo):
        self.git_repo = git_repo

    def init_repo_boilerplate(self):
        return self.git_repo