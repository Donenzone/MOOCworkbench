from django.db import models
from user_manager.models import WorkbenchUser
from markdownx.models import MarkdownxField
import xmlrpc.client
from notifications.signals import notify
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField
from git_manager.models import GitRepository

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
        if package_version.count() is not 0:
            return package_version[0]
        return None


class ExternalPackage(Package):
    project_page = models.URLField()


class InternalPackage(Package):
    repo = models.ForeignKey(to=GitRepository)


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
    url = models.URLField()

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

