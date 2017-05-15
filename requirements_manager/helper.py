from .models import Requirement


def delete_existing_requirements(self):
    for req in self.exp_or_package.requirements.all():
        self.exp_or_package.requirements.remove(req)
        self.exp_or_package.save()
        req.delete()


def add_internalpackage_to_experiment(internal_package, experiment):
    latest_version = internal_package.get_latest_package_version()
    new_requirement = Requirement()
    new_requirement.package_name = internal_package.name
    new_requirement.version = latest_version.version_nr
    new_requirement.package = internal_package
    new_requirement.save()

    if not experiment.requirements.filter(package_name=new_requirement.package_name):
        experiment.requirements.add(new_requirement)
        experiment.save()
        return True
    return False

