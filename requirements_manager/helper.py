from .models import Requirement


def delete_existing_requirements(exp_or_package):
    for req in exp_or_package.requirements.all():
        exp_or_package.requirements.remove(req)
        exp_or_package.save()
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
        from .tasks import task_write_requirements_file
        task_write_requirements_file.delay(experiment.pk, experiment.get_object_type())
        return True
    return False
