import xmlrpc.client

from autoslug import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from markdownx.utils import markdownify
from model_utils.models import TimeStampedModel
from notifications.signals import notify

from build_manager.models import TravisCiConfig, TravisInstance
from coverage_manager.models import CodeCoverage
from docs_manager.models import Docs
from git_manager.helpers.language_helper import PythonHelper, RHelper
from git_manager.models import GitRepository
from helpers.helper_mixins import ExperimentPackageTypeMixin
from recommendations.models import Recommendation
from requirements_manager.models import Requirement
from user_manager.models import WorkbenchUser

PYPI_URL = 'https://pypi.python.org/pypi'


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    parent = models.ForeignKey(to='self', null=True, blank=True)

    def __str__(self):
        return self.name


class Language(TimeStampedModel):
    language = models.CharField(max_length=255)

    def __str__(self):
        return self.language


class BasePackage(TimeStampedModel):
    language = models.ForeignKey(to=Language)

    class Meta:
        abstract = True


alphanumeric = RegexValidator(r'^[a-z]*$', 'Only lowercase letters are allowed.')


class Package(BasePackage):
    name = models.CharField(max_length=255, unique=True, validators=[alphanumeric])
    description = models.TextField()
    subscribed_users = models.ManyToManyField(to=WorkbenchUser)
    owner = models.ForeignKey(to=WorkbenchUser, related_name='owner')
    category = models.ForeignKey(to=Category)
    recommended = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_latest_package_version(self):
        package_version = PackageVersion.objects.filter(package=self).order_by('-created')
        if package_version:
            return package_version[0]
        return None

    def get_absolute_url(self):
        return reverse('package_detail', kwargs={'pk': self.pk})

    def get_activity_message(self):
        return "Package {0} was created by {1}".format(self.name, self.owner)

    def recount_recommendations(self):
        content_type = ContentType.objects.get(model="package")
        update_recommendations(content_type, self)

    @property
    def recommendations(self):
        content_type = ContentType.objects.get(model="package")
        return Recommendation.objects.filter(content_type=content_type, object_id=self.pk)


def update_recommendations(content_type, content_object):
    recommendations = Recommendation.objects.filter(content_type=content_type, object_id=content_object.pk)
    content_object.recommended = recommendations.count()
    content_object.save()


class ExternalPackage(Package):
    project_page = models.URLField(help_text='URL to the project page of the package, for example to the PyPi location')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('externalpackage_detail', kwargs={'pk': self.pk})


class InternalPackage(Package):
    git_repo = models.ForeignKey(to=GitRepository, null=True)
    travis = models.ForeignKey(to=TravisInstance, null=True)
    docs = models.ForeignKey(to=Docs, null=True)
    requirements = models.ManyToManyField(to=Requirement)
    published = models.BooleanField(default=False)
    template = models.ForeignKey('cookiecutter_manager.CookieCutterTemplate')

    def get_absolute_url(self):
        return reverse('internalpackage_detail', kwargs={'pk': self.pk})

    def get_docs_folder(self):
        return [self.python_package_name]

    def get_object_type(self):
        return ExperimentPackageTypeMixin.PACKAGE_TYPE

    def success_url_dict(self, hash=''):
        return {'dependencies': reverse('package_dependencies',
                                        kwargs={'pk': self.pk, 'object_type': self.get_object_type()}) + hash,
                'resources': '',
                'versions': ''}

    def language_helper(self):
        language_helper_dict = {'Python3': PythonHelper, 'R': RHelper}
        return language_helper_dict[self.language.language](self)

    def __str__(self):
        return self.name

    @property
    def python_package_name(self):
        return slugify(self.name).replace('-', '_')

    def delete(self, using=None, keep_parents=False):
        if self.docs:
            self.docs.delete()
        if self.git_repo:
            self.git_repo.delete()
        if self.travis.codecoverage_set:
            coverage = self.travis.codecoverage_set.all()
            for cov in coverage:
                cov.delete()
        if self.travis:
            self.travis.delete()
        super(InternalPackage, self).delete()


@receiver(post_save, sender=InternalPackage)
def add_package_config(sender, instance, created, **kwargs):
    if created:
        docs = Docs()
        docs.save()
        instance.docs = docs

        travis_config = TravisCiConfig()
        travis_config.save()
        travis = TravisInstance(config=travis_config)
        travis.save()
        instance.travis = travis

        coverage = CodeCoverage()
        coverage.travis_instance = travis
        coverage.enabled = False
        coverage.save()

        instance.save()

        package_version = PackageVersion(package=instance, version_nr='0.0.1', changelog='Initial version',
                                         added_by=instance.owner, url='')
        package_version.save()


class PackageResource(TimeStampedModel):
    package = models.ForeignKey(to=Package)
    title = models.CharField(max_length=255)
    resource = models.TextField(help_text='Markdown allowed')
    url = models.URLField(null=True, blank=True, help_text='URL to resource (optional)')
    added_by = models.ForeignKey(to=WorkbenchUser)
    recommended = models.IntegerField(default=0)

    @property
    def markdown(self):
        return markdownify(self.resource)

    @property
    def recommendations(self):
        content_type = ContentType.objects.get(model="packageresource")
        return Recommendation.objects.filter(content_type=content_type, object_id=self.pk)

    def recount_recommendations(self):
        content_type = ContentType.objects.get(model="packageresource")
        update_recommendations(content_type, self)

    def __str__(self):
        return "{0} by {1}".format(self.title, self.added_by)

    def get_absolute_url(self):
        return reverse('packageresource_detail', kwargs={'pk': self.pk})

    def get_activity_message(self):
        return "New resource '{0}' by {1} for package {2}".format(self.title, self.added_by, self.package)


class PackageVersion(TimeStampedModel):
    package = models.ForeignKey(to=Package)
    version_nr = models.CharField(max_length=50)
    changelog = models.TextField()
    added_by = models.ForeignKey(to=WorkbenchUser, null=True)
    pre_release = models.BooleanField(default=False)
    url = models.URLField(null=True)

    def check_if_version_is_newer(self, version_nr):
        return self.version_nr != version_nr

    def __str__(self):
        return '{0} {1}'.format(self.package, self.version_nr)

    class Meta:
        unique_together = ('package', 'version_nr')

    def get_activity_message(self):
        return "{0} was updated to version {1}".format(self.package, self.version_nr)

    def get_absolute_url(self):
        return reverse('packageversion_list', kwargs={'pk': self.package.pk})


@receiver(post_save, sender=PackageVersion)
def send_notification(sender, instance, created, **kwargs):
    if created:
        subscribed_users = instance.package.subscribed_users.all()
        message = 'Package {0} is updated to {1}'.format(instance.package, instance.version_nr)
        for user in subscribed_users:
            notify.send(user, recipient=user.user, verb=message)


def update_all_versions():
    for package in ExternalPackage.objects.all():
        get_latest_version(package)


def get_latest_version(package):
    pypi = xmlrpc.client.ServerProxy(PYPI_URL)
    release = pypi.package_releases(package.name)
    if len(release) != 0:
        release = release[0]
        newest_release = package.get_latest_package_version()
        if newest_release is None or newest_release.check_if_version_is_newer(release):
            url = '{0}/{1}/{2}'.format(PYPI_URL, package.name, release)
            newer_release = PackageVersion(package=package, version_nr=release, changelog="Auto-added", url=url)
            newer_release.save()
