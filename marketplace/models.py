import xmlrpc.client

from autoslug import AutoSlugField
from django.urls import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from markdownx.models import MarkdownxField
from model_utils.models import TimeStampedModel
from notifications.signals import notify

from build_manager.models import TravisInstance, TravisCiConfig
from docs_manager.models import Docs
from git_manager.models import GitRepository
from requirements_manager.models import Requirement
from user_manager.models import WorkbenchUser


PYPI_URL = 'https://pypi.python.org/pypi'


class PackageCategory(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    parent = models.ForeignKey(to='self', null=True, blank=True)

    def __str__(self):
        return self.name


class PackageLanguage(TimeStampedModel):
    language = models.CharField(max_length=255)

    def __str__(self):
        return self.language


class Package(TimeStampedModel):
    package_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    subscribed_users = models.ManyToManyField(to=WorkbenchUser)
    category = models.ForeignKey(to=PackageCategory)
    language = models.ForeignKey(to=PackageLanguage)
    owner = models.ForeignKey(to=WorkbenchUser, related_name='owner')

    def __str__(self):
        return self.package_name

    def get_latest_package_version(self):
        package_version = PackageVersion.objects.filter(package=self).order_by('-created')
        if package_version:
            return package_version[0]
        return None


class ExternalPackage(Package):
    project_page = models.URLField()


class InternalPackage(Package):
    git_repo = models.ForeignKey(to=GitRepository)
    travis = models.ForeignKey(to=TravisInstance, null=True)
    docs = models.ForeignKey(to=Docs, null=True)
    requirements = models.ManyToManyField(to=Requirement)

    def get_absolute_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.pk})

    def get_docs_folder(self):
        return [self.python_package_name]

    @property
    def python_package_name(self):
        return slugify(self.package_name).replace('-', '_')


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

        instance.save()

        package_version = PackageVersion(package=instance, version_nr='0.1', changelog='Initial version', added_by=instance.owner, url='')
        package_version.save()


class PackageResource(TimeStampedModel):
    package = models.ForeignKey(to=Package)
    resource = MarkdownxField()
    url = models.URLField(null=True)
    added_by = models.ForeignKey(to=WorkbenchUser)


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
        return '{0}v{1} added at {2}'.format(self.package, self.version_nr, self.created)


@receiver(post_save, sender=PackageVersion)
def send_notification(sender, instance, created, **kwargs):
    if created:
        subscribed_users = instance.package.subscribed_users.all()
        message = 'Package {0} is updated to {1}'.format(instance.package, instance.version_nr)
        for user in subscribed_users:
            notify.send(user, recipient=user.user, verb=message)


def update_all_versions():
    for package in Package.objects.all():
        get_latest_version(package)


def get_latest_version(package):
    if not package.internal_package:
        pypi = xmlrpc.client.ServerProxy(PYPI_URL)
        release = pypi.package_releases(package.package_name)
        if len(release) != 0:
            release = release[0]
            newest_release = package.get_latest_package_version()
            if newest_release is None or newest_release.check_if_version_is_newer(release):
                url = '{0}/{1}/{2}'.format(PYPI_URL, package.package_name, release)
                newer_release = PackageVersion(package=package, version_nr=release, changelog="Auto-added", url=url)
                newer_release.save()

