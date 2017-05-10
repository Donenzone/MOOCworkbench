from .models import InternalPackage, ExternalPackage


class IsInternalPackageMixin(object):
    def get_context_data(self, **kwargs):
        context = super(IsInternalPackageMixin, self).get_context_data(**kwargs)
        if InternalPackage.objects.filter(pk=self.kwargs['pk']):
            context['is_internal'] = True
        else:
            context['is_internal'] = False
        return context


class ObjectTypeIdMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ObjectTypeIdMixin, self).get_context_data(**kwargs)
        package_id = self.kwargs['pk']

        package = InternalPackage.objects.filter(id=package_id)
        if package:
            package = package[0]
            context['object_type'] = package.get_object_type()
        else:
            package = ExternalPackage.objects.get(id=package_id)
        context['object_id'] = package.pk
        context['object'] = package

        return context