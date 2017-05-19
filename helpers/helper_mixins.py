class ExperimentPackageTypeMixin(object):
    EXPERIMENT_TYPE = 'experiment'
    PACKAGE_TYPE = 'package'
    requirement_types = {'Experiment': EXPERIMENT_TYPE, 'InternalPackage': PACKAGE_TYPE}

    def get_requirement_type(self, django_object):
        return self.requirement_types[django_object.__class__.__name__]
